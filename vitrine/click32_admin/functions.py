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

def get_timeline_data():
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=5)
    dates = [start_date + timedelta(days=x) for x in range(6)]
    
    timeline_data = {
        'labels': [date.strftime('%d/%m') for date in dates],
        'links': {
            'main_banner': [0] * 6,
            'whatsapp_1': [0] * 6,
            'whatsapp_2': [0] * 6,
            'phone': [0] * 6,
            'instagram': [0] * 6,
            'facebook': [0] * 6,
            'youtube': [0] * 6,
            'x_link': [0] * 6,
            'google_maps': [0] * 6,
            'website': [0] * 6
        }
    }
    
    for i, date in enumerate(dates):
        daily_clicks = ClickTrack.objects.filter(
            last_clicked__date=date
        ).aggregate(
            main_banner=Sum('click_count', filter=Q(element_type='main_banner')),
            whatsapp_1=Sum('click_count', filter=Q(element_type='whatsapp_link_1')),
            whatsapp_2=Sum('click_count', filter=Q(element_type='whatsapp_link_2')),
            phone=Sum('click_count', filter=Q(element_type='phone_link')),
            instagram=Sum('click_count', filter=Q(element_type='instagram_link')),
            facebook=Sum('click_count', filter=Q(element_type='facebook_link')),
            youtube=Sum('click_count', filter=Q(element_type='youtube_link')),
            x_link=Sum('click_count', filter=Q(element_type='x_link')),
            google_maps=Sum('click_count', filter=Q(element_type='google_maps_link')),
            website=Sum('click_count', filter=Q(element_type='website_link'))
        )
        for key in timeline_data['links']:
            value = daily_clicks[key]
            timeline_data['links'][key][i] = int(value) if value is not None and isinstance(value, (int, float)) else 0
    
    return timeline_data

# Outras funções permanecem inalteradas
def get_clicks_data():
    stores = (
        Store.objects
        .annotate(
            main_banner_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='main_banner')),
            whatsapp_1_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='whatsapp_link_1')),
            whatsapp_2_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='whatsapp_link_2')),
            phone_clicks=Sum('clicktrack__click_count', filter=Q(clicktrack__element_type='phone_link')),
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
            store.website_clicks or 0
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
            'website': store.website_clicks or 0,
            'total_clicks': total_clicks,
            'secondary_clicks': secondary_clicks,
            'last_clicked': store.last_clicked
        })
    
    return clicks_data

def get_site_metrics():
    home_accesses = ClickTrack.objects.filter(
        element_type='home_access', store__isnull=True
    ).aggregate(total=Sum('click_count'))['total'] or 0
    return {
        'home_accesses': home_accesses
    }

def get_store_count():
    return Store.objects.count()

def get_global_clicks():
    clicks_data = get_clicks_data()
    return sum(data['total_clicks'] for data in clicks_data)

def get_profile_accesses():
    clicks_data = get_clicks_data()
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
        'website': store_data.get('website', 0)
    }

def get_engagement_rate():
    clicks_data = get_clicks_data()
    total_clicks = sum(data['total_clicks'] for data in clicks_data)
    profile_accesses = sum(data['main_banner'] for data in clicks_data)
    return round((total_clicks / profile_accesses * 100) if profile_accesses > 0 else 0, 1)

def get_total_clicks_by_link_type():
    clicks = ClickTrack.objects.aggregate(
        
        whatsapp_1=Sum('click_count', filter=Q(element_type='whatsapp_link_1')),
        whatsapp_2=Sum('click_count', filter=Q(element_type='whatsapp_link_2')),
        phone=Sum('click_count', filter=Q(element_type='phone_link')),
        instagram=Sum('click_count', filter=Q(element_type='instagram_link')),
        facebook=Sum('click_count', filter=Q(element_type='facebook_link')),
        youtube=Sum('click_count', filter=Q(element_type='youtube_link')),
        x_link=Sum('click_count', filter=Q(element_type='x_link')),
        google_maps=Sum('click_count', filter=Q(element_type='google_maps_link')),
        website=Sum('click_count', filter=Q(element_type='website_link'))
    )
    return {
        'labels': ['WhatsApp 1', 'WhatsApp 2','Telefone' ,'Instagram', 'Facebook', 'YouTube', 'X Link', 'Google Maps', 'Website'],
        'data': [
            
            clicks.get('whatsapp_1', 0) or 0,
            clicks.get('whatsapp_2', 0) or 0,
            clicks.get('phone', 0) or 0,
            clicks.get('instagram', 0) or 0,
            clicks.get('facebook', 0) or 0,
            clicks.get('youtube', 0) or 0,
            clicks.get('x_link', 0) or 0,
            clicks.get('google_maps', 0) or 0,
            clicks.get('website', 0) or 0
        ]
    }