from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum, Max, Q
from .models import Store, Tag, ClickTrack
import logging

logger = logging.getLogger(__name__)

def home(request):
    tag_name = request.GET.get('filter')
    tags = Tag.objects.all()

    if tag_name:
        stores = Store.objects.filter(tags__name=tag_name).distinct()
    else:
        stores = Store.objects.all()

    stores = stores.order_by('-highlight', 'name')
    return render(request, 'home.html', {
        'stores': stores,
        'tags': tags,
        'selected_tag': tag_name
    })

def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'store_detail.html', {'store': store})

def advertise(request):
    return render(request, 'advertise.html')

def about(request):
    return render(request, 'about.html')

def clicks_dashboard(request):
    # Obter todos os comércios (stores)
    stores = Store.objects.all()

    # Lista para armazenar os dados consolidados
    clicks_data = []

    # Para cada comércio, buscar os cliques e consolidar
    for store in stores:
        click_entries = ClickTrack.objects.filter(store=store)
        store_data = {
            'store_name': store.name,
            'main_banner': click_entries.filter(element_type='main_banner').aggregate(total=Sum('click_count'))['total'] or 0,
            'whatsapp': click_entries.filter(element_type='whatsapp_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'instagram': click_entries.filter(element_type='instagram_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'facebook': click_entries.filter(element_type='facebook_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'youtube': click_entries.filter(element_type='youtube_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'x_link': click_entries.filter(element_type='x_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'google_maps': click_entries.filter(element_type='google_maps_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'website': click_entries.filter(element_type='website_link').aggregate(total=Sum('click_count'))['total'] or 0,
            'last_clicked': click_entries.aggregate(last=Max('last_clicked'))['last']
        }
        clicks_data.append(store_data)

    # Log para depuração
    logger.info(f"Consolidated clicks data: {clicks_data}")

    return render(request, 'admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })

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