from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='início'), # home que exibirá as lojas
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    path('anuncie/', views.advertise, name='anuncie'),
    path('sobre/', views.about, name='sobre')
]