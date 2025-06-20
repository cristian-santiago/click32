from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
import os
import shutil
import logging
import json
from .forms import StoreForm, TagForm, CategoryForm, GroupForm
from vitrine.models import Store, Tag, Category
from .functions import get_site_metrics, get_clicks_data, get_store_count, get_total_clicks_by_link_type, get_global_clicks, get_profile_accesses, get_heatmap_data, get_timeline_data, get_comparison_data, get_store_highlight_data, get_engagement_rate

logger = logging.getLogger(__name__)

# Decorador personalizado para verificar permissões
def check_permission(permission_check, login_url='/admin/login/'):
    def decorator(view_func):
        @login_required(login_url=login_url)
        def wrapper(request, *args, **kwargs):
            if permission_check(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return decorator

# Manipulador de erro 403
def permission_denied(request, exception):
    return render(request, '403.html', status=403)

@check_permission(lambda u: u.is_staff)
def dashboard(request):
    context = {
        'can_view_stores': request.user.has_perm('vitrine.view_store'),
    }
    return render(request, 'click32_admin/dashboard.html', context)

@check_permission(lambda u: u.is_superuser)
def click_dashboard(request):
    return render(request, 'click32_admin/click_dashboard.html')

@check_permission(lambda u: u.has_perm('vitrine.view_store'))
def admin_dashboard(request):
    return render(request, 'click32_admin/admin_dashboard.html')

@check_permission(lambda u: u.is_superuser)
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'click32_admin/store_list.html', {'stores': stores})

@check_permission(lambda u: u.is_superuser)
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.save()
            tags_raw = request.POST.get('tags', '')
            tag_ids = [int(t) for t in tags_raw.split(',') if t.isdigit()]
            store.tags.set(tag_ids)
            return redirect('click32_admin:store_list')
    else:
        form = StoreForm()
    return render(request, 'click32_admin/store_form.html', {
        'form': form,
        'store': None,
        'imagens': ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4'],
    })

@check_permission(lambda u: u.is_superuser)
def store_edit(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            old_obj = Store.objects.get(pk=store.pk)
            new_obj = form.save(commit=False)
            for field_name in ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4']:
                old_file = getattr(old_obj, field_name)
                new_file = getattr(new_obj, field_name)
                cleared = request.POST.get(f"{field_name}-clear")
                if cleared:
                    if old_file and os.path.isfile(old_file.path):
                        os.remove(old_file.path)
                        logger.info(f"Cleared field and deleted file: {old_file.path}")
                    setattr(new_obj, field_name, None)
                elif old_file and old_file != new_file:
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)
                        logger.info(f"Replaced file: {old_file.path}")
            new_obj.save()
            form.save_m2m()
            return redirect('click32_admin:store_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'click32_admin/store_form.html', {
        'form': form,
        'store': store,
        'imagens': ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4']
    })

@check_permission(lambda u: u.is_superuser)
@require_POST
def store_delete(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    for image_field in [store.main_banner, store.carousel_2, store.carousel_3, store.carousel_4]:
        if image_field and os.path.exists(image_field.path):
            try:
                os.remove(image_field.path)
                logger.info(f"Deleted image: {image_field.path}")
            except Exception as e:
                logger.error(f"Error deleting image {image_field.path}: {e}")
    store_dir = os.path.join('media', f'stores/{slugify(store.name)}')
    if os.path.isdir(store_dir):
        try:
            shutil.rmtree(store_dir)
            logger.info(f"Deleted store directory: {store_dir}")
        except Exception as e:
            logger.error(f"Error deleting store directory {store_dir}: {e}")
    store.delete()
    return redirect('click32_admin:store_list')

@check_permission(lambda u: u.is_superuser)
def clicks_dashboard(request):
    clicks_data = get_clicks_data()
    return render(request, 'click32_admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })

@check_permission(lambda u: u.has_perm('vitrine.view_store'))
def global_widgets_dashboard(request):
    clicks_data = get_clicks_data()
    clicks_summary = {
        'main_banner': sum(data['main_banner'] for data in clicks_data),
        'whatsapp': sum(data['whatsapp'] for data in clicks_data),
        'instagram': sum(data['instagram'] for data in clicks_data),
        'facebook': sum(data['facebook'] for data in clicks_data),
        'youtube': sum(data['youtube'] for data in clicks_data),
        'x_link': sum(data['x_link'] for data in clicks_data),
        'google_maps': sum(data['google_maps'] for data in clicks_data),
        'website': sum(data['website'] for data in clicks_data),
    }
    site_metrics = get_site_metrics()
    context = {
        'store_count': get_store_count(),
        'global_clicks': get_global_clicks(),
        'clicks_data': clicks_data,
        'clicks_summary': clicks_summary,
        'home_accesses': site_metrics['home_accesses'],
        'clicks_summary_json': mark_safe(json.dumps(clicks_summary)),
    }
    return render(request, 'click32_admin/global_dashboard.html', context)

@check_permission(lambda u: u.has_perm('vitrine.view_store'))
def widgets_dashboard(request):
    context = {
        'store_count': get_store_count(),
        'global_clicks': get_global_clicks(),
        'profile_accesses': get_profile_accesses(),
        'heatmap_data': get_heatmap_data(),
        'store_highlight': get_store_highlight_data(),
        'site_metrics': get_site_metrics(),
    }
    return render(request, 'click32_admin/dashboard_widgets.html', context)

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.info(f"Tentativa de login com username: {username}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            logger.info(f"Usuário autenticado: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
            if user.is_staff or user.is_superuser:
                login(request, user)
                logger.info("Login bem-sucedido")
                next_url = request.POST.get('next') or request.GET.get('next') or reverse('click32_admin:dashboard')
                # Ensure next_url is not empty and is safe
                if not next_url or next_url == '':
                    next_url = reverse('click32_admin:dashboard')
                # Restrict access to certain URLs for non-superusers
                if any(x in next_url for x in ['tags', 'categories', 'users', 'groups']):
                    if not user.is_superuser:
                        logger.info(f"Usuário {user.username} sem permissão para {next_url}, redirecionando para dashboard")
                        next_url = reverse('click32_admin:dashboard')
                return redirect(next_url)
            else:
                logger.info("Usuário não é administrador")
                response = render(request, 'click32_admin/login.html', {
                    'error': 'Acesso negado: usuário não é administrador',
                    'next': request.POST.get('next', request.GET.get('next', ''))
                })
        else:
            logger.info("Falha na autenticação")
            response = render(request, 'click32_admin/login.html', {
                'error': 'Credenciais inválidas',
                'next': request.POST.get('next', request.GET.get('next', ''))
            })
    else:
        response = render(request, 'click32_admin/login.html', {
            'next': request.GET.get('next', '')
        })
    
    # Prevent caching of the login page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def admin_logout(request):
    logout(request)
    request.session.flush()  # Clear the session to invalidate CSRF token
    response = redirect('click32_admin:admin_login')
    # Prevent caching of the login page after logout
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@check_permission(lambda u: u.is_superuser)
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'click32_admin/tag_list.html', {'tags': tags})

@check_permission(lambda u: u.is_superuser)
def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:tag_list')
    else:
        form = TagForm()
    return render(request, 'click32_admin/tag_form.html', {'form': form})

@check_permission(lambda u: u.is_superuser)
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:tag_list')
    else:
        form = TagForm(instance=tag)
    return render(request, 'click32_admin/tag_form.html', {'form': form})

@check_permission(lambda u: u.is_superuser)
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        tag.delete()
        return redirect('click32_admin:tag_list')
    return render(request, 'click32_admin/tag_confirm_delete.html', {'tag': tag})

@check_permission(lambda u: u.is_superuser)
def category_list(request):
    categories = Category.objects.prefetch_related('tags').all()
    return render(request, 'click32_admin/category_list.html', {'categories': categories})

@check_permission(lambda u: u.is_superuser)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return redirect('click32_admin:category_list')
    else:
        form = CategoryForm()
    return render(request, 'click32_admin/category_form.html', {'form': form})

@check_permission(lambda u: u.is_superuser)
def category_edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'click32_admin/category_form.html', {'form': form})

@check_permission(lambda u: u.is_superuser)
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('click32_admin:category_list')
    return render(request, 'click32_admin/category_confirm_delete.html', {'category': category})

@check_permission(lambda u: u.is_superuser)
def total_clicks_by_link_type_api(request):
    data = get_total_clicks_by_link_type()
    return JsonResponse(data)

@check_permission(lambda u: u.is_superuser)
def timeline_data_api(request):
    data = get_timeline_data()
    return JsonResponse(data)

@check_permission(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all()
    return render(request, 'click32_admin/user_list.html', {'users': users})

@check_permission(lambda u: u.is_superuser)
def user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('click32_admin:user_list')
    else:
        form = UserCreationForm()
    return render(request, 'click32_admin/user_form.html', {'form': form, 'title': 'Criar Usuário'})

@check_permission(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'click32_admin/user_form.html', {'form': form, 'title': 'Editar Usuário', 'user': user})

@check_permission(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('click32_admin:user_list')
    return render(request, 'click32_admin/user_confirm_delete.html', {'user': user})

@check_permission(lambda u: u.is_superuser)
def user_change_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:user_list')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'click32_admin/user_change_password.html', {'form': form, 'user': user})

@check_permission(lambda u: u.is_superuser)
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'click32_admin/group_list.html', {'groups': groups})

@check_permission(lambda u: u.is_superuser)
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:group_list')
    else:
        form = GroupForm()
    return render(request, 'click32_admin/group_form.html', {'form': form, 'title': 'Criar Grupo'})

@check_permission(lambda u: u.is_superuser)
def group_edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'click32_admin/group_form.html', {'form': form, 'title': 'Editar Grupo', 'group': group})

@check_permission(lambda u: u.is_superuser)
def group_delete(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect('click32_admin:group_list')
    return render(request, 'click32_admin/group_confirm_delete.html', {'group': group})