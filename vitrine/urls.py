from django.urls import path, register_converter
from django.views.generic import TemplateView
from vitrine.admin_instance import click32_admin_site
from . import views



class StoreSlugConverter:
    regex = '[\w-]+'  # slugs com letras, números e hífens
    def to_python(self, value): return value
    def to_url(self, value): return value

register_converter(StoreSlugConverter, 'storeslug')

urlpatterns = [



    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),

    # Página principal
    path('', views.home, name='home'),
    
    # URLs específicas PRIMEIRO
    path('store/<int:store_id>/', views.store_detail_by_id, name='store_detail_by_id'),
    path('store/uuid/<uuid:qr_uuid>/', views.store_detail_by_uuid, name='store_detail_by_uuid'),
    path('store/<int:store_id>/flyer/', views.view_flyer, name='view_flyer'),
    path('fetch-flyer-pages/<int:store_id>/', views.fetch_flyer_pages, name='fetch_flyer_pages'),
    
    # Páginas estáticas
    path('anuncie/', views.advertise, name='anuncie'),
    path('sobre/', views.about, name='sobre'),
    path('faq/', views.faq, name='faq'),
    
    # APIs
    path('start-session/', views.start_session, name='start_session'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('active-users-count/', views.active_users_count, name='active_users_count'),
    path('track-click/<int:store_id>/<str:element_type>/', views.track_click, name='track_click'),
    path('track-share/<int:store_id>/', views.track_share, name='track_share'),
    path('track-pwa-click/', views.track_pwa_click, name='track_pwa_click'),

    path('log-debug/', views.log_debug, name='log_debug'),
    path("service-worker.js", views.service_worker),
    path("sw-config.js", views.sw_config),

    # SEMPRE A ÚLTIMA
    path('<storeslug:slug>/', views.store_detail, name='store_detail'),

    
]