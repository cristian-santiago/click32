from django.db.models import Sum, Max, Q
from vitrine.models import Store, ClickTrack, Category
from django.utils import timezone
from datetime import timedelta


def get_category_tags():
    categories = Category.objects.prefetch_related('tags').all()
    return [
        {
            'name': category.name,
            'icon': category.icon or 'fa-th',
            'tags': [tag.name for tag in category.tags.all()]
        }
        for category in categories
    ]

def get_timeline_data(store_id=None, start_date=None, end_date=None):
    # Período padrão: últimos 30 dias se não passado
    if start_date is None or end_date is None:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)  # 30 dias
    
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    
    timeline_data = {
        'labels': [d.strftime('%d/%m') for d in dates],
        'links': {
            'main_banner': [0] * len(dates),
            'whatsapp_1': [0] * len(dates),
            'whatsapp_2': [0] * len(dates),
            'phone': [0] * len(dates),
            'instagram': [0] * len(dates),
            'facebook': [0] * len(dates),
            'youtube': [0] * len(dates),
            'x_link': [0] * len(dates),
            'ifood': [0] * len(dates),
            'anota_ai': [0] * len(dates),         
            'google_maps': [0] * len(dates),
            'flyer': [0] * len(dates)
        }
    }
    
    base_filter = Q(last_clicked__date__range=[start_date, end_date])
    if store_id:
        base_filter &= Q(store_id=store_id)
    
    for i, date in enumerate(dates):
        daily_clicks = ClickTrack.objects.filter(base_filter & Q(last_clicked__date=date)).aggregate(
            main_banner=Sum('click_count', filter=Q(element_type='main_banner')),
            whatsapp_1=Sum('click_count', filter=Q(element_type='whatsapp_link_1')),
            whatsapp_2=Sum('click_count', filter=Q(element_type='whatsapp_link_2')),
            phone=Sum('click_count', filter=Q(element_type='phone_link')),
            instagram=Sum('click_count', filter=Q(element_type='instagram_link')),
            facebook=Sum('click_count', filter=Q(element_type='facebook_link')),
            youtube=Sum('click_count', filter=Q(element_type='youtube_link')),
            x_link=Sum('click_count', filter=Q(element_type='x_link')),
            google_maps=Sum('click_count', filter=Q(element_type='google_maps_link')),
            anota_ai=Sum('click_count', filter=Q(element_type='anota_ai_link')),
            ifood=Sum('click_count', filter=Q(element_type='ifood_link')),
            flyer=Sum('click_count', filter=Q(element_type='flyer_pdf')),
        )
        for key in timeline_data['links']:
            value = daily_clicks[key]
            timeline_data['links'][key][i] = int(value) if value is not None and isinstance(value, (int, float)) else 0
    
    return timeline_data

# Outras funções permanecem inalteradas

def get_clicks_data(store_id=None, start_date=None, end_date=None):
    # Calcula período padrão se não passado (mês atual até hoje)
    if start_date is None or end_date is None:
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)
    
    base_query = Q(clicktrack__last_clicked__date__range=[start_date, end_date])
    if store_id:
        base_query &= Q(clicktrack__store_id=store_id)
    
    stores = (
        Store.objects
        .annotate(
            main_banner_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='main_banner')),
            whatsapp_1_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='whatsapp_link_1')),
            whatsapp_2_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='whatsapp_link_2')),
            phone_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='phone_link')),
            instagram_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='instagram_link')),
            facebook_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='facebook_link')),
            youtube_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='youtube_link')),
            x_link_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='x_link')),
            google_maps_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='google_maps_link')),
            ifood_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='ifood_link')),
            anota_ai_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='anota_ai_link')),
            flyer_clicks=Sum('clicktrack__click_count', filter=base_query & Q(clicktrack__element_type='flyer_pdf')),
            last_clicked=Max('clicktrack__last_clicked', filter=base_query)
        )
    )
    if store_id:
        stores = stores.filter(id=store_id)
    
    clicks_data = []
    for store in stores:
        total_clicks = sum([
            store.main_banner_clicks or 0,
            store.whatsapp_1_clicks or 0,
            store.whatsapp_2_clicks or 0,
            store.phone_clicks or 0,
            store.instagram_clicks or 0,
            store.facebook_clicks or 0,
            store.youtube_clicks or 0,
            store.x_link_clicks or 0,
            store.google_maps_clicks or 0,
            store.ifood_clicks or 0,
            store.anota_ai_clicks or 0,
            store.flyer_clicks or 0
        ])
        secondary_clicks = total_clicks - (store.main_banner_clicks or 0)
        clicks_data.append({
            'store': store,
            'main_banner': store.main_banner_clicks or 0,
            'whatsapp_1': store.whatsapp_1_clicks or 0,
            'whatsapp_2': store.whatsapp_2_clicks or 0,
            'phone': store.phone_clicks or 0,
            'instagram': store.instagram_clicks or 0,
            'facebook': store.facebook_clicks or 0,
            'youtube': store.youtube_clicks or 0,
            'x_link': store.x_link_clicks or 0,
            'google_maps': store.google_maps_clicks or 0,
            'ifood': store.ifood_clicks or 0,
            'anota_ai': store.anota_ai_clicks or 0,
            'flyer': store.flyer_clicks or 0,
            'total_clicks': total_clicks,
            'secondary_clicks': secondary_clicks,
            'last_clicked': store.last_clicked
        })
    
    return clicks_data

def get_site_metrics(store_id=None, start_date=None, end_date=None):
    # Adapta para filtro (home_accesses é global, mas filtra se store_id passado; assume home_accesses não é por store)
    base_filter = Q(element_type='home_access', store__isnull=True)
    if start_date and end_date:
        base_filter &= Q(last_clicked__date__range=[start_date, end_date])
    home_accesses = ClickTrack.objects.filter(base_filter).aggregate(total=Sum('click_count'))['total'] or 0
    return {'home_accesses': home_accesses}

def get_store_count():
    return Store.objects.count()

def get_global_clicks(store_id=None, start_date=None, end_date=None):
    clicks_data = get_clicks_data(store_id, start_date, end_date)
    return sum(data['total_clicks'] for data in clicks_data)

def get_profile_accesses(store_id=None, start_date=None, end_date=None):
    clicks_data = get_clicks_data(store_id, start_date, end_date)
    return sum(data['main_banner'] for data in clicks_data)

def get_heatmap_data():
    clicks_data = get_clicks_data()
    max_clicks = max((data['total_clicks'] for data in clicks_data), default=1)
    heatmap_data = []
    for data in clicks_data[:10]:
        intensity = data['total_clicks'] / max_clicks if max_clicks > 0 else 0
        heatmap_data.append({
            'store_name': data['store'].name,
            'clicks': data['total_clicks'],
            'intensity': 'high' if intensity > 0.66 else 'medium' if intensity > 0.33 else 'low'
        })
    return heatmap_data

def get_comparison_data(store_ids=None):
    clicks_data = get_clicks_data()
    if store_ids:
        clicks_data = [data for data in clicks_data if data['store'].id in store_ids]
    return clicks_data[:3]

def get_store_highlight_data(store_id=None):
    clicks_data = get_clicks_data()
    store_data = clicks_data[0] if clicks_data else {}
    if store_id:
        store_data = next((data for data in clicks_data if data['store'].id == store_id), clicks_data[0] if clicks_data else {})
    return {
        'store_name': store_data.get('store').name if store_data.get('store') else 'N/A',
        'main_banner': store_data.get('main_banner', 0),
        'whatsapp_1': store_data.get('whatsapp_1', 0),
        'whatsapp_2': store_data.get('whatsapp_2', 0),
        'phone': store_data.get('phone', 0),
        'instagram': store_data.get('instagram', 0),
        'facebook': store_data.get('facebook', 0),
        'youtube': store_data.get('youtube', 0),
        'x_link': store_data.get('x_link', 0),
        'google_maps': store_data.get('google_maps', 0),
        'ifood': store_data.get('ifood', 0),
        'anota_ai': store_data.get('anota_ai', 0),
        'flyer_pdf': store_data.get('flyer_pdf', 0)
    }

def get_engagement_rate(store_id=None, start_date=None, end_date=None):
    clicks_data = get_clicks_data(store_id, start_date, end_date)
    total_clicks = sum(data['total_clicks'] for data in clicks_data)
    profile_accesses = sum(data['main_banner'] for data in clicks_data)
    return round((total_clicks / profile_accesses * 100) if profile_accesses > 0 else 0, 1)

def get_total_clicks_by_link_type(store_id=None, start_date=None, end_date=None):
    # Período padrão como em get_clicks_data
    if start_date is None or end_date is None:
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)
    
    base_filter = Q(last_clicked__date__range=[start_date, end_date])
    if store_id:
        base_filter &= Q(store_id=store_id)
    
    clicks = ClickTrack.objects.filter(base_filter).aggregate(
        whatsapp_1=Sum('click_count', filter=Q(element_type='whatsapp_link_1')),
        whatsapp_2=Sum('click_count', filter=Q(element_type='whatsapp_link_2')),
        phone=Sum('click_count', filter=Q(element_type='phone_link')),
        instagram=Sum('click_count', filter=Q(element_type='instagram_link')),
        facebook=Sum('click_count', filter=Q(element_type='facebook_link')),
        youtube=Sum('click_count', filter=Q(element_type='youtube_link')),
        x_link=Sum('click_count', filter=Q(element_type='x_link')),
        google_maps=Sum('click_count', filter=Q(element_type='google_maps_link')),
        ifood=Sum('click_count', filter=Q(element_type='ifood_link')),
        anota_ai=Sum('click_count', filter=Q(element_type='anota_ai_link')),
        flyer=Sum('click_count', filter=Q(element_type='flyer_pdf')),
    )
    return {
        'labels': ['WhatsApp 1', 'WhatsApp 2', 'Telefone', 'Instagram', 'Facebook', 'YouTube', 'X Link', 'Google Maps', 'Anota Ai', 'iFood', 'Flyer'],
        'data': [
            clicks.get('whatsapp_1', 0) or 0,
            clicks.get('whatsapp_2', 0) or 0,
            clicks.get('phone', 0) or 0,
            clicks.get('instagram', 0) or 0,
            clicks.get('facebook', 0) or 0,
            clicks.get('youtube', 0) or 0,
            clicks.get('x_link', 0) or 0,
            clicks.get('google_maps', 0) or 0,
            clicks.get('anota_ai', 0) or 0,
            clicks.get('ifood', 0) or 0,
            clicks.get('flyer', 0) or 0,
        ]
    }