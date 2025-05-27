from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Store, Tag, ClickTrack
import logging

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
    if selected_tag:
        stores = Store.objects.filter(tags__name=selected_tag).distinct().order_by('-highlight', 'name')
    else:
        stores = Store.objects.all().order_by('-highlight', 'name')
    
    context = {'stores': stores, 'tag_groups': get_tag_groups()}
    return render(request, 'home.html', context)


def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    context = {'store': store, 'tag_groups': get_tag_groups()}
    return render(request, 'store_detail.html', context)

def advertise(request):
    
    context = {'tag_groups': get_tag_groups()}
    return render(request, 'advertise.html', context)

def about(request):
    context = {'tag_groups': get_tag_groups()}
    return render(request, 'about.html', context)    



def track_click(request, store_id, element_type):
    try:
        store = Store.objects.get(id=store_id)
        valid_elements = [choice[0] for choice in ClickTrack.element_type.field.choices]
        
        if element_type not in valid_elements:
            logger.error(f"Invalid element_type: {element_type}")
            return HttpResponse("Invalid element type")

        click_track, created = ClickTrack.objects.get_or_create(
            store=store,
            element_type=element_type,
            defaults={'click_count': 0}
        )
        click_track.click_count += 1
        click_track.save()
        logger.info(f"Tracked click for store_id={store_id}, element_type={element_type}, count={click_track.click_count}")

        # Map element_type to the corresponding URL field
        url_field_map = {
            'main_banner': store.website_link,  # Adjust if main_banner should redirect elsewhere
            'carousel_2': store.website_link,   # Adjust as needed
            'carousel_3': store.website_link,   # Adjust as needed
            'carousel_4': store.website_link,   # Adjust as needed
            'whatsapp_link': store.whatsapp_link,
            'instagram_link': store.instagram_link,
            'facebook_link': store.facebook_link,
            'youtube_link': store.youtube_link,
            'x_link': store.x_link,
            'google_maps_link': store.google_maps_link,
            'website_link': store.website_link,
        }
        redirect_url = url_field_map.get(element_type, '/')
        if not redirect_url:
            logger.warning(f"No URL defined for {element_type} on store {store.name}")
            return redirect('/')
        return redirect(redirect_url)
    except Store.DoesNotExist:
        logger.error(f"Store not found: store_id={store_id}")
        return HttpResponse("Store not found")
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return HttpResponse("Error processing click")