from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum, Max, Q
from .models import Store, ClickTrack
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
#-------------------------------

#def clicks_dashboard(request):
    print(">>> Entrou na clicks_dashboard <<<")
    # Agregações diretamente nos objetos Store
    stores = (
        Store.objects
        .annotate(
            main_banner_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='main_banner')),
            whatsapp_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='whatsapp_link')),
            instagram_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='instagram_link')),
            facebook_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='facebook_link')),
            youtube_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='youtube_link')),
            x_link_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='x_link')),
            google_maps_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='google_maps_link')),
            website_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='website_link')),
            last_clicked=Max('clicktrack__last_clicked')
        )
    )

    clicks_data = []
    for store in stores:
        # Usa 0 para valores nulos
        main_banner = store.main_banner_clicks or 0
        whatsapp = store.whatsapp_clicks or 0
        instagram = store.instagram_clicks or 0
        facebook = store.facebook_clicks or 0
        youtube = store.youtube_clicks or 0
        x_link = store.x_link_clicks or 0
        google_maps = store.google_maps_clicks or 0
        website = store.website_clicks or 0

        total_clicks = main_banner + whatsapp + instagram + facebook + youtube + x_link + google_maps + website

        clicks_data.append({
            'store': store,  # agora é um objeto Store
            'main_banner': main_banner,
            'whatsapp': whatsapp,
            'instagram': instagram,
            'facebook': facebook,
            'youtube': youtube,
            'x_link': x_link,
            'google_maps': google_maps,
            'website': website,
            'total_clicks': total_clicks,
            'last_clicked': store.last_clicked
        })

    return render(request, 'admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })

#--------------------------------
def track_click(request, store_id, element_type):
    try:
        store = get_object_or_404(Store, id=store_id)
        valid_elements = [
            'main_banner', 'whatsapp_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'website_link'
        ]
        if element_type not in valid_elements:
            return HttpResponse(status=400)

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
        else:
            link_field = f"{element_type}"
            link = getattr(store, link_field, None)
            if link:
                return HttpResponseRedirect(link)
            return HttpResponse(status=404)
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return HttpResponse(status=500)
    
def teste_print(request):
    print(">>> DEBUG: view teste_print foi chamada <<<")
    return HttpResponse("Teste de print no console OK!")