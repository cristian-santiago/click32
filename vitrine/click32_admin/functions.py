from django.db.models import Sum, Max, Q
from vitrine.models import Store, ClickTrack, Category, PWADownloadClick, ActiveSession  
from django.utils import timezone
from datetime import timedelta
import json


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


def get_dashboard_data():
    # Dados existentes...
    store_count = Store.objects.count()
    
    # Cliques globais (excluindo home_access para não duplicar)
    global_clicks = ClickTrack.objects.exclude(element_type='home_access').aggregate(
        total=Count('click_count')
    )['total'] or 0
    
    # Acessos à home
    home_accesses = ClickTrack.objects.filter(element_type='home_access').aggregate(
        total=Count('click_count')
    )['total'] or 0
    
    # Dados de cliques por elemento
    clicks_summary = {
        'whatsapp_1': ClickTrack.objects.filter(element_type='whatsapp_link_1').aggregate(total=Count('click_count'))['total'] or 0,
        'whatsapp_2': ClickTrack.objects.filter(element_type='whatsapp_link_2').aggregate(total=Count('click_count'))['total'] or 0,
        'instagram': ClickTrack.objects.filter(element_type='instagram_link').aggregate(total=Count('click_count'))['total'] or 0,
        'facebook': ClickTrack.objects.filter(element_type='facebook_link').aggregate(total=Count('click_count'))['total'] or 0,
        'youtube': ClickTrack.objects.filter(element_type='youtube_link').aggregate(total=Count('click_count'))['total'] or 0,
        'x_link': ClickTrack.objects.filter(element_type='x_link').aggregate(total=Count('click_count'))['total'] or 0,
        'google_maps': ClickTrack.objects.filter(element_type='google_maps_link').aggregate(total=Count('click_count'))['total'] or 0,
        'anota_ai': ClickTrack.objects.filter(element_type='anota_ai_link').aggregate(total=Count('click_count'))['total'] or 0,
        'ifood': ClickTrack.objects.filter(element_type='ifood_link').aggregate(total=Count('click_count'))['total'] or 0,
        'flyer': ClickTrack.objects.filter(element_type='flyer_pdf').aggregate(total=Count('click_count'))['total'] or 0,
    }
    
    # Dados do PWA Download
    pwa_stats = {
        'total_clicks': PWADownloadClick.objects.count(),
        'accepted_installs': PWADownloadClick.objects.filter(action='accepted').count(),
        'dismissed_installs': PWADownloadClick.objects.filter(action='dismissed').count(),
        'button_clicks': PWADownloadClick.objects.filter(action='clicked').count(),
    }
    
    
    
    # Calcular taxa de conversão
    if pwa_stats['button_clicks'] > 0:
        pwa_stats['conversion_rate'] = round((pwa_stats['accepted_installs'] / pwa_stats['button_clicks']) * 100, 1)
    else:
        pwa_stats['conversion_rate'] = 0
    
    
    
    # Ranking de lojas (lógica existente)
    stores_with_clicks = Store.objects.annotate(
        total_clicks=Count('clicktrack__click_count'),
        main_banner=Count('clicktrack__click_count', filter=models.Q(clicktrack__element_type='main_banner'))
    ).order_by('-total_clicks')
    
    clicks_data = []
    for store in stores_with_clicks:
        clicks_data.append({
            'store': store,
            'total_clicks': store.total_clicks or 0,
            'main_banner': store.main_banner or 0,
            'secondary_clicks': (store.total_clicks or 0) - (store.main_banner or 0)
        })
    
    session_metrics = get_session_metrics()
    
    return {
        'store_count': store_count,
        'global_clicks': global_clicks,
        'home_accesses': home_accesses,
        'clicks_summary': clicks_summary,
        'clicks_summary_json': json.dumps(clicks_summary),
        'clicks_data': clicks_data,
        'pwa_stats': pwa_stats,
        'pwa_stats_json': json.dumps(pwa_stats),
        'active_users_count': session_metrics['active_5min'],  # Padrão 5min
        'session_metrics': session_metrics,
        'session_metrics_json': json.dumps(session_metrics),
    }


def get_active_users_count(minutes=5):
    """
    Retorna contagem de usuários ativos nos últimos X minutos
    """
    cutoff_time = timezone.now() - timedelta(minutes=minutes)
    active_count = ActiveSession.objects.filter(
        last_activity__gte=cutoff_time
    ).count()
    return active_count

def get_session_metrics():
    """
    Retorna métricas completas de sessões
    """    
    try:
        one_min_ago = timezone.now() - timedelta(minutes=1)
        five_min_ago = timezone.now() - timedelta(minutes=5)
        fifteen_min_ago = timezone.now() - timedelta(minutes=15)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        return {
            'active_1min': ActiveSession.objects.filter(last_activity__gte=one_min_ago).count(),
            'active_5min': ActiveSession.objects.filter(last_activity__gte=five_min_ago).count(),
            'active_15min': ActiveSession.objects.filter(last_activity__gte=fifteen_min_ago).count(),
            'active_1hour': ActiveSession.objects.filter(last_activity__gte=one_hour_ago).count(),
            'total_sessions_today': ActiveSession.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
        }
    except Exception as e:
        # Fallback em caso de erro
        return {
            'active_1min': 0,
            'active_5min': 0,
            'active_15min': 0,
            'active_1hour': 0,
            'total_sessions_today': 0,
        }