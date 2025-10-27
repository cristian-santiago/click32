from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Sum, Max, Q
from .models import Store, ClickTrack, Category, ShareTrack, PWADownloadClick, ActiveSession
from django.core.mail import send_mail
import pdf2image
import glob
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import F
import logging
from .click32_admin.functions import get_category_tags, get_site_metrics
import os
import random
import json
import uuid

logger = logging.getLogger(__name__)

# Decorador personalizado para verificar permissões
def check_permission(permission_check, login_url='/admin/login/'):
    def decorator(view_func):
        @login_required(login_url=login_url)
        def wrapper(request, *args, **kwargs):
            if permission_check(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return decorator

def get_tag_groups():
    return {
        'Comidas': ['Comidas', 'Pizzas', 'Lanches', 'Açaiterias'],
        'Comércios': ['Bazares', 'PetShops', 'Padarias', 'Auto Peças'],    
        'Serviços': ['Encanador', 'Pintor', 'Pedreiro', 'Técnico de Informática'],
        'Beleza': ['Beleza', 'Manicure', 'Salão de Beleza', 'Maquiadora'],
        'Saúde': ['Psicólogos', 'Fisioterapeutas', 'Nutricionista', 'Fonoaudiólogo'],
        'Educação': ['Alfabetização', 'Música', 'Inglês', 'Aulas Particulares'],
        'Outros': ['Aluguéis', 'Vendas', 'Trocas', 'Parcerias']
    }
#@cache_page(60 * 60 * 24)   # 24 horas
def home(request):
    selected_tag = request.GET.get('tag')
    stores_vip = None
    stores_deactivated = None

    # Chave de cache por tag (ou None)
    cache_key = f'stores_cache_{selected_tag or "all"}'
    cached_data = cache.get(cache_key)

    if cached_data:
        # Recupera dados já cacheados
        stores, stores_vip, stores_deactivated = cached_data
    else:
        # Busca do banco
        all_stores = Store.objects.filter(is_deactivated=False)
        stores_deactivated = list(Store.objects.filter(is_deactivated=True))

        if selected_tag:
            category = Category.objects.filter(name=selected_tag).first()
            if category:
                filtered_stores = all_stores.filter(tags__in=category.tags.all()).distinct()
            else:
                filtered_stores = all_stores.filter(tags__name=selected_tag).distinct()

            highlights = list(filtered_stores.filter(highlight=True))
            non_highlights = list(filtered_stores.filter(highlight=False))

            # Cache sem embaralhar
            stores = highlights + non_highlights
        else:
            stores_vip = list(all_stores.filter(is_vip=True)[:10])
            stores = list(all_stores)

        # Salva no cache por 5 minutos
        cache.set(cache_key, (stores, stores_vip, stores_deactivated), timeout=24*60*60)

    # Sempre embaralha antes de renderizar
    if selected_tag:
        highlights = [s for s in stores if s.highlight]
        non_highlights = [s for s in stores if not s.highlight]
        random.shuffle(highlights)
        random.shuffle(non_highlights)
        stores = highlights + non_highlights
    else:
        if stores_vip:
            random.shuffle(stores_vip)
        random.shuffle(stores)

    context = {
        'stores': stores,
        'stores_vip': stores_vip,
        'stores_deactivated': stores_deactivated,
        'category_tags': get_category_tags(),
        'selected_tag': selected_tag,
    }

    # Rastreia clique na home
    if not selected_tag:
        track_click(request, element_type='home_access')

    return render(request, 'home.html', context)

#@cache_page(60 * 60 * 24)   # 24 horas
def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug)
    if store.is_deactivated:
        return redirect('home')  # redireciona para a home se estiver desativada

    element_type = request.GET.get('element_type', 'direct_access')

# Define o tipo de clique real que será rastreado
    if element_type != 'main_banner':
    # Tenta obter o registro existente
        log_type = 'main_banner'  # Always log as profile access for store_detail loads
        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type=log_type,
            defaults={'click_count': 0, 'last_clicked': timezone.now()}
        )

        # Sempre incrementa (tanto acesso direto quanto reload contam)
        click_track.click_count = F('click_count') + 1
        click_track.last_clicked = timezone.now()
        click_track.save()
        click_track.refresh_from_db()  # Atualiza o valor real após o F()

    context = {
        'store': store,
        'category_tags': get_category_tags(),
    }
    return render(request, 'store_detail.html', context)

#@cache_page(60 * 60 * 24)   # 24 horas
def store_detail_by_id(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if store.is_deactivated:
        return redirect('home')
    element_type = request.GET.get('element_type', 'direct_access')
    redirect_url = f"{reverse('store_detail', args=[store.slug])}?element_type={element_type}"
    return redirect(redirect_url)

#@cache_page(60 * 60 * 24)   # 24 horas
def store_detail_by_uuid(request, qr_uuid):
    store = get_object_or_404(Store, qr_uuid=qr_uuid)
    if store.is_deactivated:
        return redirect('home')

    redirect_url = f"{reverse('store_detail', args=[store.slug])}?element_type=direct_access"
    return redirect(redirect_url)

@cache_page(60 * 60 * 24)   # 24 horas
def advertise(request):
    context = {'category_tags': get_category_tags()}
    return render(request, 'advertise.html', context)

# @cache_page(60 * 60 * 24)   # 24 horas
def about(request):
    context = {'category_tags': get_category_tags()}
    return render(request, 'about.html', context)

#--------------------------------
@check_permission(lambda u: u.is_superuser)
def track_click(request, store_id=None, element_type=None):
    try:
        valid_elements = [
            'main_banner', 'whatsapp_link_1','whatsapp_link_2','phone_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'ifood_link', 'anota_ai_link', 'home_access', 'flyer_pdf'
        ]
        if element_type not in valid_elements:
            return HttpResponse(status=400)

        # Contagem de "home_access"
        if element_type == 'home_access':
            click_track, created = ClickTrack.objects.get_or_create(
                store=None,
                element_type='home_access',
                defaults={'click_count': 1}
            )
            if not created:
                click_track.click_count += 1
                click_track.save()
            logger.info("Click tracked: Home Access")
            return None

        store = get_object_or_404(Store, id=store_id)

        # Cria ou atualiza contagem do clique
        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type=element_type,
            defaults={'click_count': 1}
        )
        if not created:
            click_track.click_count += 1
            click_track.save()

        logger.info(f"Click tracked: {store.name} - {element_type}")

        # Redirecionamento específico por tipo
        if element_type == 'phone_link':
            # Retorna Json para o JS controlar o redirecionamento
            return JsonResponse({'status': 'click_logged', 'phone': store.phone_link})

        if element_type == 'main_banner':
            redirect_url = f"{reverse('store_detail', args=[store.slug])}?element_type=main_banner"
            return redirect(redirect_url)
        elif element_type == 'flyer_pdf':
            return redirect(reverse('view_flyer', args=[store_id]))
        else:
            link = getattr(store, element_type, None)
            if link:
                return HttpResponseRedirect(link)
            return redirect('store_detail', store_id=store_id)

    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return HttpResponse(status=500)
        

# ------------- SHARE TRACK -------------

@check_permission(lambda u: u.is_superuser)
def track_share(request, store_id):
    """
    View para registrar compartilhamentos de lojas
    """
    print("=== DEBUG TRACK_SHARE ===")
    print(f"Method: {request.method}")
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"CSRF Cookie: {request.COOKIES.get('csrftoken', 'NÃO ENCONTRADO')}")
    print(f"CSRF Header: {request.META.get('HTTP_X_CSRFTOKEN', 'NÃO ENCONTRADO')}")
    print(f"All Headers: {dict(request.headers)}")
    print("=========================")


    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        store = get_object_or_404(Store, id=store_id)
        
        # Cria registro de compartilhamento
        share_track = ShareTrack.objects.create(store=store)
        
        logger.info(f"Share tracked: {store.name}")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Compartilhamento registrado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Error tracking share for store {store_id}: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
    
#------------------ PWA DOWNLOAD CLICK
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

@check_permission(lambda u: u.is_superuser)
def track_pwa_click(request):
    """
    View para registrar cliques e instalações do PWA
    """
    print("=== DEBUG TRACK_SHARE ===")
    print(f"Method: {request.method}")
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"CSRF Cookie: {request.COOKIES.get('csrftoken', 'NÃO ENCONTRADO')}")
    print(f"CSRF Header: {request.META.get('HTTP_X_CSRFTOKEN', 'NÃO ENCONTRADO')}")
    print(f"All Headers: {dict(request.headers)}")
    print("=========================")

    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        action = data.get('action', 'clicked')
        
        print(f"🔄 Ação recebida: {action}")
        
        # Valida a ação
        valid_actions = ['clicked', 'accepted', 'dismissed']
        if action not in valid_actions:
            action = 'clicked'
        
        # Cria registro
        pwa_click = PWADownloadClick.objects.create(action=action)
        print(f"✅ Registro criado: {pwa_click}")
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Ação {action} registrada'
        })
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return JsonResponse({'error': 'Erro interno'}, status=500)

# view inactivated #
def submit_advertise(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        business = request.POST.get('business')
        message = request.POST.get('message')
        # Exemplo: salvar ou enviar e-mail
        send_mail(
            f'Novo Anunciante: {business}',
            f'Nome: {name}\nE-mail: {email}\nNegócio: {business}\nMensagem: {message}',
            'no-reply@click32.com',
            ['contato@click32.com'],
            fail_silently=True,
        )
        return redirect('advertise_success')  
    return render(request, 'advertise.html')

# view inactivated #
def advertise_success(request):
    return render(request, 'advertise_success.html')



def view_flyer(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if not store.flyer_pdf:
        logger.debug(f"No flyer_pdf for store {store.id}")
        return render(request, 'no_flyer.html', {'store': store})

    # Ensure the PDF file exists
    pdf_path = os.path.join(settings.MEDIA_ROOT, store.flyer_pdf.name)
    logger.debug(f"Checking PDF path: {pdf_path}, Exists: {os.path.exists(pdf_path)}")
    if not os.path.exists(pdf_path):
        return render(request, 'no_flyer.html', {
            'store': store,
            'error': 'O arquivo PDF do encarte não foi encontrado.'
        })

    try:
        # Convert PDF to images for rendering
        images = pdf2image.convert_from_path(pdf_path)
        
        # Generate URLs for each page
        page_urls = []
        for i, image in enumerate(images):
            image_path = os.path.join(settings.MEDIA_ROOT, f'flyers/temp_page_{store_id}_{i}.png')
            image.save(image_path, 'PNG')
            page_urls.append(f'{settings.MEDIA_URL}flyers/temp_page_{store_id}_{i}.png')

        # Track the click
        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type='flyer_pdf',
            defaults={'click_count': 0}
        )
        click_track.click_count += 1
        click_track.save()

        context = {
            'store': store,
            'page_urls': page_urls,
            'total_pages': len(page_urls),
        }
        return render(request, 'flyer.html', context)
    except Exception as e:
        logger.error(f"Error processing flyer for store {store_id}: {str(e)}")
        return render(request, 'no_flyer.html', {
            'store': store,
            'error': f'Erro ao processar o encarte: {str(e)}'
        })
    
def cleanup_temp_files(store_id):
    temp_files = glob.glob(os.path.join(settings.MEDIA_ROOT, f'flyers/temp_page_{store_id}_*.png'))
    for file in temp_files:
        try:
            os.remove(file)
            logger.debug(f"Removed temporary file: {file}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file}: {str(e)}")

def fetch_flyer_pages(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if not store.flyer_pdf:
        logger.debug(f"No flyer_pdf for store {store.id}")
        return JsonResponse({'error': 'Nenhum encarte disponível.'}, status=404)

    pdf_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, store.flyer_pdf.name))
    logger.debug(f"Checking PDF path: {pdf_path}, Exists: {os.path.exists(pdf_path)}")
    if not os.path.exists(pdf_path):
        return JsonResponse({'error': 'O arquivo PDF do encarte não foi encontrado.'}, status=404)

    try:
        # Clean up old temporary files
        cleanup_temp_files(store_id)
        # Convert PDF to images with lower DPI for faster loading
        images = pdf2image.convert_from_path(pdf_path, dpi=100, last_page=5)  # Limit to 5 pages
        logger.debug(f"Converted {len(images)} pages from PDF")
        
        page_urls = []
        for i, image in enumerate(images):
            image_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, f'flyers/temp_page_{store_id}_{i}.png'))
            logger.debug(f"Saving image to: {image_path}")
            image.save(image_path, 'PNG', quality=85)  # Reduce quality for smaller files
            page_urls.append(f'{settings.MEDIA_URL}flyers/temp_page_{store_id}_{i}.png')

        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type='flyer_pdf',
            defaults={'click_count': 0}
        )
        click_track.click_count += 1
        click_track.save()
        logger.info(f"Click tracked: {store.name} - flyer_pdf")

        return JsonResponse({'page_urls': page_urls})
    except Exception as e:
        logger.error(f"Error processing flyer for store {store_id}: {str(e)}")
        return JsonResponse({'error': f'Erro ao processar o encarte: {str(e)}'}, status=500)
    
from django.views.decorators.csrf import csrf_protect

# VIEWS PÚBLICAS - para usuários anônimos rastrearem sessão
@csrf_protect
def start_session(request):
    """
    Inicia uma nova sessão anônima - ACESSO PÚBLICO
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        from .models import ActiveSession
        
        # Cria nova sessão
        session = ActiveSession.objects.create()
        
        return JsonResponse({
            'status': 'success',
            'session_id': str(session.session_id),
            'message': 'Sessão iniciada'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro ao criar sessão: {str(e)}'}, status=500)

@csrf_protect
def heartbeat(request):
    """
    Atualiza a atividade de uma sessão existente - ACESSO PÚBLICO
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        from .models import ActiveSession
        
        data = json.loads(request.body) if request.body else {}
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'session_id obrigatório'}, status=400)
        
        # Tenta usar a sessão existente ou cria uma nova
        try:
            session_uuid = uuid.UUID(session_id)
            session, created = ActiveSession.objects.get_or_create(
                session_id=session_uuid,
                defaults={'last_activity': timezone.now()}
            )
            
            if not created:
                session.last_activity = timezone.now()
                session.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sessão atualizada' if not created else 'Nova sessão criada',
                'session_created': created,
                'session_id': str(session.session_id)
            })
            
        except ValueError:
            new_session = ActiveSession.objects.create()
            return JsonResponse({
                'status': 'success',
                'message': 'Nova sessão criada (ID anterior inválido)',
                'session_id': str(new_session.session_id),
                'session_created': True
            })
            
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

# VIEW PROTEGIDA - apenas para admin ver as métricas
@check_permission(lambda u: u.is_superuser)
def active_users_count(request):
    """Retorna quantidade de usuários ativos nos últimos X minutos - ACESSO RESTRITO"""
    try:
        from .models import ActiveSession
        
        minutes = int(request.GET.get('minutes', 5))
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        active_count = ActiveSession.objects.filter(
            last_activity__gte=cutoff_time
        ).count()
        
        return JsonResponse({
            'active_users': active_count,
            'timeframe_minutes': minutes,
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)