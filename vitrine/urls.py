from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # home que exibirá as lojas
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
]