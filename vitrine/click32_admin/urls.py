from django.urls import path

from . import views

handler403 = views.permission_denied
app_name = "click32_admin"

urlpatterns = [
    # Dashboards
    path('', views.dashboard, name='dashboard'),  # Raiz do admin
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),  # Dashboard alternativo
    path('clicks-dashboard/', views.clicks_dashboard, name='clicks-dashboard'),
    path('widgets-dashboard/', views.widgets_dashboard, name='widgets-dashboard'),
    path('global-dashboard/', views.global_widgets_dashboard, name='global-dashboard'),
    
    # Login
    path('login/', views.admin_login, name='admin_login'),  # Consolidado login
    path('logout/', views.admin_logout, name='logout'),

    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/password/', views.user_change_password, name='user_change_password'),
    
    # Groups
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    # Stores URL
    path('stores/', views.store_list, name='store_list'),
    path('stores/create/', views.store_create, name='store_create'),
    path('stores/<int:store_id>/edit/', views.store_edit, name='store_edit'),
    path('stores/<int:store_id>/delete/', views.store_delete, name='store_delete'),
    
    # Tags URL
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
    
    # Category
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # APIs
    path('api/total-clicks-by-link-type/', views.total_clicks_by_link_type_api, name='total_clicks_by_link_type_api'),
    path('api/timeline-data/', views.timeline_data_api, name='timeline_data_api'),
]