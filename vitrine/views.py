from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.text import get_valid_filename
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
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


def rate_limit_callback(request, exception):
    """Callback quando rate limit é excedido"""
    client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
    logger.warning(
        f"Rate limit exceeded - IP: {client_ip}, "
        f"Path: {request.path}, Method: {request.method}"
    )
    # Retorna a resposta padrão do ratelimit
    from django.http import HttpResponse
    return HttpResponse('Too Many Requests', status=429)

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
    try:
        selected_tag = request.GET.get('tag')
        stores_vip = None
        stores_deactivated = None

        logger.info(f"Home page accessed - Tag: {selected_tag or 'None'}")

        # Chave de cache por tag (ou None)
        cache_key = f'stores_cache_{selected_tag or "all"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Cache hit - Key: {cache_key}")
            stores, stores_vip, stores_deactivated = cached_data
        else:
            logger.debug(f"Cache miss - Key: {cache_key}")
            all_stores = Store.objects.filter(is_deactivated=False)
            stores_deactivated = list(Store.objects.filter(is_deactivated=True))

            if selected_tag:
                category = Category.objects.filter(name=selected_tag).first()
                if category:
                    filtered_stores = all_stores.filter(tags__in=category.tags.all()).distinct()
                    logger.debug(f"Filtered by category - Category: {selected_tag}, Stores: {filtered_stores.count()}")
                else:
                    filtered_stores = all_stores.filter(tags__name=selected_tag).distinct()
                    logger.debug(f"Filtered by tag - Tag: {selected_tag}, Stores: {filtered_stores.count()}")

                highlights = list(filtered_stores.filter(highlight=True))
                non_highlights = list(filtered_stores.filter(highlight=False))
                stores = highlights + non_highlights
            else:
                stores_vip = list(all_stores.filter(is_vip=True)[:10])
                stores = list(all_stores)
                logger.debug(f"All stores loaded - VIP: {len(stores_vip)}, Total: {len(stores)}")

            cache.set(cache_key, (stores, stores_vip, stores_deactivated), timeout=24*60*60)

        # Sempre embaralha antes de renderizar
        if selected_tag:
            highlights = [s for s in stores if s.highlight]
            non_highlights = [s for s in stores if not s.highlight]
            random.shuffle(highlights)
            random.shuffle(non_highlights)
            stores = highlights + non_highlights
            logger.debug(f"Stores shuffled with tag - Highlights: {len(highlights)}, Regular: {len(non_highlights)}")
        else:
            if stores_vip:
                random.shuffle(stores_vip)
            random.shuffle(stores)
            logger.debug(f"Stores shuffled - VIP: {len(stores_vip) if stores_vip else 0}, Total: {len(stores)}")

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

        logger.info(f"Home page rendered successfully - Total stores displayed: {len(stores)}")
        return render(request, 'home.html', context)

    except Exception as e:
        logger.error(f"Error rendering home page - Error: {str(e)}", exc_info=True)
        # Fallback seguro em caso de erro
        return render(request, 'home.html', {
            'stores': [],
            'stores_vip': [],
            'stores_deactivated': [],
            'category_tags': get_category_tags(),
            'selected_tag': None,
        })

#@cache_page(60 * 60 * 24)   # 24 horas

def store_detail(request, slug):
    try:
        store = get_object_or_404(Store, slug=slug)
        
        if store.is_deactivated:
            logger.warning(f"Attempt to access deactivated store - Slug: {slug}")
            return redirect('home')

        element_type = request.GET.get('element_type', 'direct_access')
        
        logger.info(f"Store detail accessed - Store: {store.name}, Slug: {slug}, Source: {element_type}")

        # Define o tipo de clique real que será rastreado
        if element_type != 'main_banner':
            log_type = 'main_banner'
            click_track, created = ClickTrack.objects.get_or_create(
                store=store,
                element_type=log_type,
                defaults={'click_count': 0, 'last_clicked': timezone.now()}
            )

            click_track.click_count = F('click_count') + 1
            click_track.last_clicked = timezone.now()
            click_track.save()
            click_track.refresh_from_db()

            logger.debug(f"Store click tracked - Store: {store.name}, Type: {log_type}, Count: {click_track.click_count}")

        context = {
            'store': store,
            'category_tags': get_category_tags(),
        }
        
        logger.info(f"Store detail rendered successfully - Store: {store.name}")
        return render(request, 'store_detail.html', context)

    except Store.DoesNotExist:
        logger.error(f"Store not found - Slug: {slug}")
        raise
    except Exception as e:
        logger.error(f"Error rendering store detail - Slug: {slug}, Error: {str(e)}", exc_info=True)
        raise

#@cache_page(60 * 60 * 24)
def store_detail_by_id(request, store_id):
    try:
        store = get_object_or_404(Store, id=store_id)
        
        if store.is_deactivated:
            logger.warning(f"Attempt to access deactivated store by ID - Store ID: {store_id}")
            return redirect('home')
            
        element_type = request.GET.get('element_type', 'direct_access')
        redirect_url = f"{reverse('store_detail', args=[store.slug])}?element_type={element_type}"
        
        logger.info(f"Redirecting store by ID - Store ID: {store_id}, Slug: {store.slug}, Source: {element_type}")
        return redirect(redirect_url)

    except Store.DoesNotExist:
        logger.error(f"Store not found by ID - Store ID: {store_id}")
        raise
    except Exception as e:
        logger.error(f"Error in store_detail_by_id - Store ID: {store_id}, Error: {str(e)}", exc_info=True)
        raise

#@cache_page(60 * 60 * 24)
def store_detail_by_uuid(request, qr_uuid):
    try:
        store = get_object_or_404(Store, qr_uuid=qr_uuid)
        
        if store.is_deactivated:
            logger.warning(f"Attempt to access deactivated store by UUID - UUID: {qr_uuid}")
            return redirect('home')

        redirect_url = f"{reverse('store_detail', args=[store.slug])}?element_type=direct_access"
        
        logger.info(f"Redirecting store by UUID - UUID: {qr_uuid}, Store: {store.name}, Slug: {store.slug}")
        return redirect(redirect_url)

    except Store.DoesNotExist:
        logger.error(f"Store not found by UUID - UUID: {qr_uuid}")
        raise
    except Exception as e:
        logger.error(f"Error in store_detail_by_uuid - UUID: {qr_uuid}, Error: {str(e)}", exc_info=True)
        raise

#@cache_page(60 * 60 * 24)
def advertise(request):
    try:
        logger.info("Advertise page accessed")
        context = {'category_tags': get_category_tags()}
        return render(request, 'advertise.html', context)
    except Exception as e:
        logger.error(f"Error rendering advertise page - Error: {str(e)}", exc_info=True)
        # Fallback básico
        return render(request, 'advertise.html', {'category_tags': []})

# @cache_page(60 * 60 * 24)
def about(request):
    try:
        logger.info("About page accessed")
        context = {'category_tags': get_category_tags()}
        return render(request, 'about.html', context)
    except Exception as e:
        logger.error(f"Error rendering about page - Error: {str(e)}", exc_info=True)
        # Fallback básico
        return render(request, 'about.html', {'category_tags': []})
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
    try:
        if request.method != 'POST':
            logger.warning(f"Invalid method in track_share - Method: {request.method}, Store ID: {store_id}")
            return JsonResponse({'error': 'Método não permitido'}, status=405)
        
        store = get_object_or_404(Store, id=store_id)
        
        # Log de debug para troubleshooting
        logger.debug(
            f"Track share request - Store: {store.name}, "
            f"User: {request.user}, "
            f"CSRF Token: {'Present' if request.META.get('HTTP_X_CSRFTOKEN') else 'Missing'}"
        )
        
        # Cria registro de compartilhamento
        share_track = ShareTrack.objects.create(store=store)
        
        logger.info(f"Share tracked successfully - Store: {store.name}, Share ID: {share_track.id}")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Compartilhamento registrado com sucesso'
        })
        
    except Store.DoesNotExist:
        logger.error(f"Store not found in track_share - Store ID: {store_id}")
        return JsonResponse({'error': 'Loja não encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error tracking share - Store ID: {store_id}, Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)

#------------------ PWA DOWNLOAD CLICK

@check_permission(lambda u: u.is_superuser)
def track_pwa_click(request):
    """
    View para registrar cliques e instalações do PWA
    """
    try:
        if request.method != 'POST':
            logger.warning(f"Invalid method in track_pwa_click - Method: {request.method}")
            return JsonResponse({'error': 'Método não permitido'}, status=405)
        
        data = json.loads(request.body) if request.body else {}
        action = data.get('action', 'clicked')
        
        # Log de debug para troubleshooting
        logger.debug(
            f"PWA click request - Action: {action}, "
            f"User: {request.user}, "
            f"CSRF Token: {'Present' if request.META.get('HTTP_X_CSRFTOKEN') else 'Missing'}"
        )
        
        # Valida a ação
        valid_actions = ['clicked', 'accepted', 'dismissed']
        if action not in valid_actions:
            logger.warning(f"Invalid PWA action received - Action: {action}, Defaulting to 'clicked'")
            action = 'clicked'
        
        # Cria registro
        pwa_click = PWADownloadClick.objects.create(action=action)
        
        logger.info(f"PWA action tracked successfully - Action: {action}, PWA Click ID: {pwa_click.id}")
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Ação {action} registrada'
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in track_pwa_click - Error: {str(e)}")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error in track_pwa_click - Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro interno'}, status=500)

'''
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

# view inactivated 

def advertise_success(request):
    return render(request, 'advertise_success.html')###

'''

def safe_media_path(filename):
    # Remove path traversal attempts
    safe_name = get_valid_filename(os.path.basename(filename))
    return os.path.join(settings.MEDIA_ROOT, safe_name)

def view_flyer(request, store_id):
    try:
        store = get_object_or_404(Store, id=store_id)
        
        if not store.flyer_pdf:
            logger.info(f"Flyer requested but not available - Store: {store.name}, ID: {store_id}")
            return render(request, 'no_flyer.html', {'store': store})

        # Ensure the PDF file exists
        pdf_path = safe_media_path(store.flyer_pdf.name)
        if not os.path.exists(pdf_path):
            
            return render(request, 'no_flyer.html', {
                'store': store,
                'error': 'O arquivo PDF do encarte não foi encontrado.'
            })

        logger.info(f"Processing flyer - Store: {store.name}, PDF: {store.flyer_pdf.name}")

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

        logger.info(f"Flyer displayed successfully - Store: {store.name}, Pages: {len(page_urls)}")

        context = {
            'store': store,
            'page_urls': page_urls,
            'total_pages': len(page_urls),
        }
        return render(request, 'flyer.html', context)
        
    except Store.DoesNotExist:
        logger.error(f"Store not found for flyer - Store ID: {store_id}")
        raise
    except Exception as e:
        logger.error(f"Error processing flyer - Store ID: {store_id}, Error: {str(e)}", exc_info=True)
        return render(request, 'no_flyer.html', {
            'store': store,
            'error': 'Erro ao processar o encarte.'
        })
    
def cleanup_temp_files(store_id):
    try:
        temp_files = glob.glob(os.path.join(settings.MEDIA_ROOT, f'flyers/temp_page_{store_id}_*.png'))
        if temp_files:
            for file in temp_files:
                try:
                    os.remove(file)
                    logger.debug(f"Temporary file cleaned up - File: {file}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file - File: {file}, Error: {str(e)}")
            logger.debug(f"Cleanup completed - Store ID: {store_id}, Files removed: {len(temp_files)}")
    except Exception as e:
        logger.error(f"Error during temp files cleanup - Store ID: {store_id}, Error: {str(e)}")

def fetch_flyer_pages(request, store_id):
    try:
        store = get_object_or_404(Store, id=store_id)
        
        if not store.flyer_pdf:
            logger.info(f"AJAX Flyer requested but not available - Store: {store.name}, ID: {store_id}")
            return JsonResponse({'error': 'Nenhum encarte disponível.'}, status=404)

        pdf_path = safe_media_path(store.flyer_pdf.name)
        if not os.path.exists(pdf_path):
            logger.warning(f"AJAX Flyer PDF file not found - Store: {store.name}, Path: {pdf_path}")
            return JsonResponse({'error': 'O arquivo PDF do encarte não foi encontrado.'}, status=404)

        logger.info(f"Processing AJAX flyer - Store: {store.name}, PDF: {store.flyer_pdf.name}")

        # Clean up old temporary files
        cleanup_temp_files(store_id)
        
        # Convert PDF to images with lower DPI for faster loading
        images = pdf2image.convert_from_path(pdf_path, dpi=100, last_page=5)
        
        page_urls = []
        for i, image in enumerate(images):
            image_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, f'flyers/temp_page_{store_id}_{i}.png'))
            image.save(image_path, 'PNG', quality=85)
            page_urls.append(f'{settings.MEDIA_URL}flyers/temp_page_{store_id}_{i}.png')

        # Track the click
        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type='flyer_pdf',
            defaults={'click_count': 0}
        )
        click_track.click_count += 1
        click_track.save()

        logger.info(f"AJAX flyer processed successfully - Store: {store.name}, Pages: {len(page_urls)}")

        return JsonResponse({'page_urls': page_urls})
        
    except Store.DoesNotExist:
        logger.error(f"Store not found for AJAX flyer - Store ID: {store_id}")
        return JsonResponse({'error': 'Loja não encontrada.'}, status=404)
    except Exception as e:
        logger.error(f"Error processing AJAX flyer - Store ID: {store_id}, Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro ao processar o encarte.'}, status=500)
    


@ratelimit(key='ip', rate='50/m', block=True)  # Bloqueia completamente
@ratelimit(key='ip', rate='500/h', block=True)  # Limite horário também
@csrf_protect
def start_session(request):
    """
    Inicia uma nova sessão anônima - ACESSO PÚBLICO
    """
    if request.method != 'POST':
        logger.warning(f"Invalid method in start_session - Method: {request.method}")
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        from .models import ActiveSession
        
        # Cria nova sessão
        session = ActiveSession.objects.create()
        
        logger.info(f"New session started - Session ID: {session.session_id}")
        
        return JsonResponse({
            'status': 'success',
            'session_id': str(session.session_id),
            'message': 'Sessão iniciada'
        })
        
    except Exception as e:
        logger.error(f"Error creating new session - Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erro ao criar sessão: {str(e)}'}, status=500)

@csrf_protect
def heartbeat(request):
    """
    Atualiza a atividade de uma sessão existente - ACESSO PÚBLICO
    """
    if request.method != 'POST':
        logger.warning(f"Invalid method in heartbeat - Method: {request.method}")
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        from .models import ActiveSession
        
        data = json.loads(request.body) if request.body else {}
        session_id = data.get('session_id')
        
        if not session_id:
            logger.warning("Heartbeat request missing session_id")
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
                logger.debug(f"Heartbeat updated - Session ID: {session_id}")
            else:
                logger.info(f"New session created from heartbeat - Session ID: {session.session_id}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sessão atualizada' if not created else 'Nova sessão criada',
                'session_created': created,
                'session_id': str(session.session_id)
            })
            
        except ValueError:
            logger.warning(f"Invalid session ID format - Session ID: {session_id}")
            new_session = ActiveSession.objects.create()
            logger.info(f"New session created due to invalid ID - New Session ID: {new_session.session_id}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Nova sessão criada (ID anterior inválido)',
                'session_id': str(new_session.session_id),
                'session_created': True
            })
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in heartbeat - Error: {str(e)}")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error in heartbeat - Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)


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
        
        logger.info(f"Active users count requested - Minutes: {minutes}, Count: {active_count}")
        
        return JsonResponse({
            'active_users': active_count,
            'timeframe_minutes': minutes,
            'last_updated': timezone.now().isoformat()
        })
        
    except ValueError as e:
        logger.error(f"Invalid minutes parameter in active_users_count - Value: {request.GET.get('minutes')}")
        return JsonResponse({'error': 'Parâmetro minutes deve ser um número'}, status=400)
    except Exception as e:
        logger.error(f"Error in active_users_count - Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)