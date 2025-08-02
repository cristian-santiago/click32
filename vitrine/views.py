from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Sum, Max, Q
from .models import Store, ClickTrack, Category
from django.core.mail import send_mail
import pdf2image
import glob
from django.urls import reverse
from django.conf import settings
import logging
from .click32_admin.functions import get_category_tags, get_site_metrics
import os
import random

logger = logging.getLogger(__name__)


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

def home(request):
    selected_tag = request.GET.get('tag')
    stores_vip = None  # Inicializa como None para evitar exibição com filtros

    if selected_tag:
        stores = Store.objects.all()
        category = Category.objects.filter(name=selected_tag).first()
        if category:
            stores = stores.filter(tags__in=category.tags.all()).distinct()
        else:
            stores = stores.filter(tags__name=selected_tag).distinct()

        # Separa os dois grupos
        highlights = list(stores.filter(highlight=True))
        non_highlights = list(stores.filter(highlight=False))

        # Embaralha ambos
        random.shuffle(highlights)
        random.shuffle(non_highlights)

        # Junta os dois grupos, destaques primeiro
        stores = highlights + non_highlights

    else:
        # Home sem filtro
        track_click(request, element_type='home_access')

        # VIP embaralhadas
        stores_vip = list(Store.objects.filter(is_vip=True)[:10])
        random.shuffle(stores_vip)

        # Demais lojas embaralhadas
        stores = list(Store.objects.all())
        random.shuffle(stores)

    context = {
        'stores': stores,
        'stores_vip': stores_vip,
        'category_tags': get_category_tags(),
        'selected_tag': selected_tag,
    }

    return render(request, 'home.html', context)

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    context = {
        'store': store,
        'category_tags': get_category_tags()
    }
    return render(request, 'store_detail.html', context)

def advertise(request):
    context = {'category_tags': get_category_tags()}
    return render(request, 'advertise.html', context)

def about(request):
    context = {'category_tags': get_category_tags()}
    return render(request, 'about.html', context)

#--------------------------------
def track_click(request, store_id=None, element_type=None):
    try:
        valid_elements = [
            'main_banner', 'whatsapp_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'website_link', 'home_access', 'flyer_pdf'
        ]
        if element_type not in valid_elements:
            return HttpResponse(status=400)

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
        else:
            store = get_object_or_404(Store, id=store_id)
            click_track, created = ClickTrack.objects.get_or_create(
                store=store,
                element_type=element_type,
                defaults={'click_count': 1}
            )
            if not created:
                click_track.click_count += 1
                click_track.save()
            logger.info(f"Click tracked: {store.name} - {element_type}")

            if element_type == 'main_banner':
                return render(request, 'store_detail.html', {'store': store})
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


def teste_print(request):
    print(">>> DEBUG: view teste_print foi chamada <<<")
    return HttpResponse("Teste de print no console OK!")



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
    

def manifest(request):
    return JsonResponse({
        "name": "Click32",
        "short_name": "Click32",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#2c3e50",
        "icons": [
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })