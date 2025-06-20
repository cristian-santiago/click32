from django.urls import path
from vitrine.admin_instance import click32_admin_site
from . import views



urlpatterns = [
    path('', views.home, name='home'), # home que exibirá as lojas
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    path('anuncie/', views.advertise, name='anuncie'),
    path('sobre/', views.about, name='sobre'),
    path('track-click/<int:store_id>/<str:element_type>/', views.track_click, name='track_click'),
    #path('advertise/submit/', views.submit_advertise, name='submit_advertise'),
    #path('advertise/success/', views.advertise_success, name='advertise_success'),

]