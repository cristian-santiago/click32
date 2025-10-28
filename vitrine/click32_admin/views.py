from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from datetime import date
from django.utils import timezone
from datetime import timedelta
import os
import shutil
import logging
import json
from .forms import StoreForm, TagForm, CategoryForm, GroupForm, StoreOpeningHourFormSet
from vitrine.models import Store, Tag, Category, ShareTrack, PWADownloadClick
from vitrine.views import cleanup_temp_files
from .functions import get_session_metrics, get_site_metrics, get_clicks_data, get_store_count, get_total_clicks_by_link_type, get_global_clicks, get_profile_accesses, get_heatmap_data, get_timeline_data, get_comparison_data, get_store_highlight_data, get_engagement_rate, get_dashboard_data

logger = logging.getLogger(__name__)

# Decorador personalizado para verificar permissões
def check_permission(permission_check, login_url='/admin/login/'):
    def decorator(view_func):
        @login_required(login_url=login_url)
        def wrapper(request, *args, **kwargs):
            if permission_check(request.user):
                return view_func(request, *args, **kwargs)
            else:
                logger.warning(
                    f"Permission denied - User: {request.user}, "
                    f"View: {view_func.__name__}, Path: {request.path}"
                )
                raise PermissionDenied
        return wrapper
    return decorator

# Manipulador de erro 403
def permission_denied(request, exception):
    logger.warning(f"403 Permission Denied - User: {request.user}, Path: {request.path}")
    return render(request, '403.html', status=403)

@check_permission(lambda u: u.is_staff)
def dashboard(request):
    logger.info(f"Dashboard accessed - User: {request.user}")
    context = {
        'can_view_stores': request.user.has_perm('vitrine.view_store'),
    }
    return render(request, 'click32_admin/dashboard.html', context)

@check_permission(lambda u: u.is_superuser)
def click_dashboard(request):
    logger.info(f"Click dashboard accessed - User: {request.user}")
    return render(request, 'click32_admin/click_dashboard.html')

@check_permission(lambda u: u.has_perm('vitrine.view_store'))
def admin_dashboard(request):
    logger.info(f"Admin dashboard accessed - User: {request.user}")
    return render(request, 'click32_admin/admin_dashboard.html')

@check_permission(lambda u: u.is_superuser)
def store_list(request):
    logger.info(f"Store list accessed - User: {request.user}")
    stores = Store.objects.all()
    logger.debug(f"Store list loaded - Count: {stores.count()}")
    return render(request, 'click32_admin/store_list.html', {'stores': stores})

@check_permission(lambda u: u.is_superuser)
def store_create(request):
    try:
        if request.method == 'POST':
            logger.info(f"Store creation attempted - User: {request.user}")
            form = StoreForm(request.POST, request.FILES)
            formset = StoreOpeningHourFormSet(request.POST, instance=Store())
            if form.is_valid() and formset.is_valid():
                store = form.save()
                formset.instance = store
                formset.save()
                tags_raw = request.POST.get('tags', '')
                tag_ids = [int(t) for t in tags_raw.split(',') if t.isdigit()]
                store.tags.set(tag_ids)
                
                logger.info(f"Store created successfully - Store: {store.name}, ID: {store.id}, User: {request.user}")
                return redirect('click32_admin:store_list')
            else:
                logger.warning(f"Store creation form invalid - Errors: {form.errors}, User: {request.user}")
        else:
            form = StoreForm()
            formset = StoreOpeningHourFormSet(instance=Store())
            
        return render(request, 'click32_admin/store_form.html', {
            'form': form,
            'formset': formset,
            'store': None,
            'imagens': ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4', 'flyer_pdf'],
        })
    except Exception as e:
        logger.error(f"Error in store_create - User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def store_edit(request, store_id):
    try:
        store = get_object_or_404(Store, pk=store_id)
        logger.info(f"Store edit accessed - Store: {store.name}, ID: {store_id}, User: {request.user}")

        if request.method == "POST":
            form = StoreForm(request.POST, request.FILES, instance=store)
            formset = StoreOpeningHourFormSet(request.POST, instance=store)
            if form.is_valid() and formset.is_valid():
                old_obj = Store.objects.get(pk=store.pk)
                new_obj = form.save(commit=False)
                
                # Process file changes
                for field_name in ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4', 'flyer_pdf']:
                    old_file = getattr(old_obj, field_name)
                    new_file = getattr(new_obj, field_name)
                    cleared = request.POST.get(f"{field_name}-clear")
                    
                    if cleared:
                        if old_file and os.path.isfile(old_file.path):
                            os.remove(old_file.path)
                            logger.info(f"File cleared and deleted - Field: {field_name}, File: {old_file.path}")
                        setattr(new_obj, field_name, None)
                        if field_name == 'flyer_pdf':
                            cleanup_temp_files(store_id)
                    elif old_file and old_file != new_file:
                        if os.path.isfile(old_file.path):
                            os.remove(old_file.path)
                            logger.info(f"File replaced - Field: {field_name}, Old file: {old_file.path}")
                        if field_name == 'flyer_pdf':
                            cleanup_temp_files(store_id)
                
                new_obj.save()
                form.save_m2m()
                formset.save()
                
                logger.info(f"Store updated successfully - Store: {store.name}, ID: {store_id}, User: {request.user}")
                return redirect('click32_admin:store_list')
            else:
                logger.warning(f"Store edit form invalid - Store: {store.name}, Errors: {form.errors}, User: {request.user}")
        else:
            form = StoreForm(instance=store)
            formset = StoreOpeningHourFormSet(instance=store)
            
        return render(request, 'click32_admin/store_form.html', {
            'form': form,
            'formset': formset,
            'store': store,
            'imagens': ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4', 'flyer_pdf']
        })
    except Store.DoesNotExist:
        logger.error(f"Store not found for edit - Store ID: {store_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in store_edit - Store ID: {store_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
@require_POST
def store_delete(request, store_id):
    try:
        store = get_object_or_404(Store, pk=store_id)
        logger.info(f"Store deletion attempted - Store: {store.name}, ID: {store_id}, User: {request.user}")

        # Delete associated files
        for image_field in [store.main_banner, store.carousel_2, store.carousel_3, store.carousel_4, store.flyer_pdf]:
            if image_field and os.path.exists(image_field.path):
                try:
                    os.remove(image_field.path)
                    logger.info(f"Store image deleted - File: {image_field.path}")
                except Exception as e:
                    logger.error(f"Error deleting store image - File: {image_field.path}, Error: {str(e)}")

        # Delete store directory
        store_dir = os.path.join('media', f'stores/{slugify(store.name)}')
        if os.path.isdir(store_dir):
            try:
                shutil.rmtree(store_dir)
                logger.info(f"Store directory deleted - Path: {store_dir}")
            except Exception as e:
                logger.error(f"Error deleting store directory - Path: {store_dir}, Error: {str(e)}")

        store_name = store.name
        store.delete()
        
        logger.info(f"Store deleted successfully - Store: {store_name}, ID: {store_id}, User: {request.user}")
        return redirect('click32_admin:store_list')
        
    except Store.DoesNotExist:
        logger.error(f"Store not found for deletion - Store ID: {store_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in store_delete - Store ID: {store_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def clicks_dashboard(request):
    logger.info(f"Clicks dashboard accessed - User: {request.user}")
    clicks_data = get_clicks_data()
    logger.debug(f"Clicks data loaded - Stores: {len(clicks_data)}")
    return render(request, 'click32_admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })

@check_permission(lambda u: u.is_superuser)
def global_widgets_dashboard(request):
    try:
        logger.info(f"Global widgets dashboard accessed - User: {request.user}")
        
        clicks_data = get_clicks_data()
        clicks_summary = {
            'whatsapp_1': sum(data['whatsapp_1'] for data in clicks_data),
            'whatsapp_2': sum(data['whatsapp_2'] for data in clicks_data),
            'phone': sum(data['phone'] for data in clicks_data),
            'instagram': sum(data['instagram'] for data in clicks_data),
            'facebook': sum(data['facebook'] for data in clicks_data),
            'youtube': sum(data['youtube'] for data in clicks_data),
            'x_link': sum(data['x_link'] for data in clicks_data),
            'google_maps': sum(data['google_maps'] for data in clicks_data),
            'anota_ai': sum(data['anota_ai'] for data in clicks_data),
            'ifood': sum(data['ifood'] for data in clicks_data),
            'flyer': sum(data['flyer'] for data in clicks_data),
        }
        
        site_metrics = get_site_metrics()
        
        pwa_stats = {
            'total_clicks': PWADownloadClick.objects.count(),
            'accepted_installs': PWADownloadClick.objects.filter(action='accepted').count(),
            'dismissed_installs': PWADownloadClick.objects.filter(action='dismissed').count(),
            'button_clicks': PWADownloadClick.objects.filter(action='clicked').count(),
        }
        
        if pwa_stats['button_clicks'] > 0:
            pwa_stats['conversion_rate'] = round((pwa_stats['accepted_installs'] / pwa_stats['button_clicks']) * 100, 1)
        else:
            pwa_stats['conversion_rate'] = 0
        
        session_metrics = get_session_metrics()
        
        logger.debug(f"Global dashboard metrics - Stores: {get_store_count()}, Active users: {session_metrics['active_5min']}, PWA conversion: {pwa_stats['conversion_rate']}%")

        context = {
            'store_count': get_store_count(),
            'global_clicks': get_global_clicks(),
            'clicks_data': clicks_data,
            'clicks_summary': clicks_summary,
            'home_accesses': site_metrics['home_accesses'],
            'clicks_summary_json': json.dumps(clicks_summary),
            'pwa_stats': pwa_stats,
            'pwa_stats_json': json.dumps(pwa_stats),
            'active_users_count': session_metrics['active_5min'],
            'session_metrics': session_metrics,
           # 'session_metrics_json': json.dumps(session_metrics),
        }
        return render(request, 'click32_admin/global_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in global_widgets_dashboard - User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.has_perm('vitrine.view_store'))
def widgets_dashboard(request):
    logger.info(f"Widgets dashboard accessed - User: {request.user}")
    context = {
        'store_count': get_store_count(),
        'global_clicks': get_global_clicks(),
        'profile_accesses': get_profile_accesses(),
        'heatmap_data': get_heatmap_data(),
        'store_highlight': get_store_highlight_data(),
        'site_metrics': get_site_metrics(),
    }
    logger.debug(f"Widgets dashboard data loaded - Stores: {context['store_count']}, Global clicks: {context['global_clicks']}")
    return render(request, 'click32_admin/dashboard_widgets.html', context)

@ratelimit(key='ip', rate='5/m')
def admin_login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            logger.info(f"Admin login attempt - Username: {username}")
            
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                logger.info(f"User authenticated - Username: {user.username}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")
                
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    logger.info(f"Admin login successful - User: {user.username}")
                    
                    next_url = request.POST.get('next') or request.GET.get('next') or reverse('click32_admin:dashboard')
                    if not next_url or next_url == '':
                        next_url = reverse('click32_admin:dashboard')
                    
                    # Restrict access to certain URLs for non-superusers
                    if any(x in next_url for x in ['tags', 'categories', 'users', 'groups']):
                        if not user.is_superuser:
                            logger.warning(f"Non-superuser attempted restricted access - User: {user.username}, URL: {next_url}")
                            next_url = reverse('click32_admin:dashboard')
                    
                    return redirect(next_url)
                else:
                    logger.warning(f"Non-admin user attempted login - Username: {username}")
                    response = render(request, 'click32_admin/login.html', {
                        'error': 'Acesso negado: usuário não é administrador',
                        'next': request.POST.get('next', request.GET.get('next', ''))
                    })
            else:
                logger.warning(f"Admin login failed - Username: {username}")
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
        
    except Exception as e:
        logger.error(f"Error in admin_login - Error: {str(e)}", exc_info=True)
        raise

def admin_logout(request):
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    logger.info(f"Admin logout - User: {username}")
    
    logout(request)
    request.session.flush()
    response = redirect('click32_admin:admin_login')
    
    # Prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

# Tag management views
@check_permission(lambda u: u.is_superuser)
def tag_list(request):
    logger.info(f"Tag list accessed - User: {request.user}")
    tags = Tag.objects.all()
    logger.debug(f"Tags loaded - Count: {tags.count()}")
    return render(request, 'click32_admin/tag_list.html', {'tags': tags})

@check_permission(lambda u: u.is_superuser)
def tag_create(request):
    try:
        if request.method == 'POST':
            logger.info(f"Tag creation attempted - User: {request.user}")
            form = TagForm(request.POST)
            if form.is_valid():
                tag = form.save()
                logger.info(f"Tag created successfully - Tag: {tag.name}, ID: {tag.id}, User: {request.user}")
                return redirect('click32_admin:tag_list')
            else:
                logger.warning(f"Tag creation form invalid - Errors: {form.errors}, User: {request.user}")
        else:
            form = TagForm()
        return render(request, 'click32_admin/tag_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in tag_create - User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def tag_edit(request, tag_id):
    try:
        tag = get_object_or_404(Tag, pk=tag_id)
        logger.info(f"Tag edit accessed - Tag: {tag.name}, ID: {tag_id}, User: {request.user}")

        if request.method == 'POST':
            form = TagForm(request.POST, instance=tag)
            if form.is_valid():
                form.save()
                logger.info(f"Tag updated successfully - Tag: {tag.name}, ID: {tag_id}, User: {request.user}")
                return redirect('click32_admin:tag_list')
            else:
                logger.warning(f"Tag edit form invalid - Tag: {tag.name}, Errors: {form.errors}, User: {request.user}")
        else:
            form = TagForm(instance=tag)
        return render(request, 'click32_admin/tag_form.html', {'form': form})
    except Tag.DoesNotExist:
        logger.error(f"Tag not found for edit - Tag ID: {tag_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in tag_edit - Tag ID: {tag_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def tag_delete(request, tag_id):
    try:
        tag = get_object_or_404(Tag, pk=tag_id)
        if request.method == 'POST':
            tag_name = tag.name
            tag.delete()
            logger.info(f"Tag deleted successfully - Tag: {tag_name}, ID: {tag_id}, User: {request.user}")
            return redirect('click32_admin:tag_list')
        logger.info(f"Tag delete confirmation - Tag: {tag.name}, ID: {tag_id}, User: {request.user}")
        return render(request, 'click32_admin/tag_confirm_delete.html', {'tag': tag})
    except Tag.DoesNotExist:
        logger.error(f"Tag not found for deletion - Tag ID: {tag_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in tag_delete - Tag ID: {tag_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

# Category management views (similar pattern as tags)
@check_permission(lambda u: u.is_superuser)
def category_list(request):
    logger.info(f"Category list accessed - User: {request.user}")
    categories = Category.objects.prefetch_related('tags').all()
    logger.debug(f"Categories loaded - Count: {categories.count()}")
    return render(request, 'click32_admin/category_list.html', {'categories': categories})

@check_permission(lambda u: u.is_superuser)
def category_create(request):
    try:
        if request.method == 'POST':
            logger.info(f"Category creation attempted - User: {request.user}")
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                logger.info(f"Category created successfully - Category: {category.name}, ID: {category.id}, User: {request.user}")
                return redirect('click32_admin:category_list')
            else:
                logger.warning(f"Category creation form invalid - Errors: {form.errors}, User: {request.user}")
        else:
            form = CategoryForm()
        return render(request, 'click32_admin/category_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in category_create - User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def category_edit(request, category_id):
    try:
        category = get_object_or_404(Category, pk=category_id)
        logger.info(f"Category edit accessed - Category: {category.name}, ID: {category_id}, User: {request.user}")

        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                logger.info(f"Category updated successfully - Category: {category.name}, ID: {category_id}, User: {request.user}")
                return redirect('click32_admin:category_list')
            else:
                logger.warning(f"Category edit form invalid - Category: {category.name}, Errors: {form.errors}, User: {request.user}")
        else:
            form = CategoryForm(instance=category)
        return render(request, 'click32_admin/category_form.html', {'form': form})
    except Category.DoesNotExist:
        logger.error(f"Category not found for edit - Category ID: {category_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in category_edit - Category ID: {category_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def category_delete(request, category_id):
    try:
        category = get_object_or_404(Category, pk=category_id)
        if request.method == 'POST':
            category_name = category.name
            category.delete()
            logger.info(f"Category deleted successfully - Category: {category_name}, ID: {category_id}, User: {request.user}")
            return redirect('click32_admin:category_list')
        logger.info(f"Category delete confirmation - Category: {category.name}, ID: {category_id}, User: {request.user}")
        return render(request, 'click32_admin/category_confirm_delete.html', {'category': category})
    except Category.DoesNotExist:
        logger.error(f"Category not found for deletion - Category ID: {category_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in category_delete - Category ID: {category_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

# API views for data
@check_permission(lambda u: u.is_superuser)
def total_clicks_by_link_type_api(request):
    logger.debug(f"Total clicks API accessed - User: {request.user}")
    data = get_total_clicks_by_link_type()
    return JsonResponse(data)

@check_permission(lambda u: u.is_superuser)
def timeline_data_api(request):
    logger.debug(f"Timeline data API accessed - User: {request.user}")
    data = get_timeline_data()
    return JsonResponse(data)

# User management views
@check_permission(lambda u: u.is_superuser)
def user_list(request):
    logger.info(f"User list accessed - User: {request.user}")
    users = User.objects.all()
    logger.debug(f"Users loaded - Count: {users.count()}")
    return render(request, 'click32_admin/user_list.html', {'users': users})

@check_permission(lambda u: u.is_superuser)
def user_create(request):
    try:
        if request.method == 'POST':
            logger.info(f"User creation attempted - User: {request.user}")
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                logger.info(f"User created successfully - Username: {user.username}, ID: {user.id}, By: {request.user}")
                return redirect('click32_admin:user_list')
            else:
                logger.warning(f"User creation form invalid - Errors: {form.errors}, By: {request.user}")
        else:
            form = UserCreationForm()
        return render(request, 'click32_admin/user_form.html', {'form': form, 'title': 'Criar Usuário'})
    except Exception as e:
        logger.error(f"Error in user_create - By: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def user_edit(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        logger.info(f"User edit accessed - Target: {user.username}, ID: {user_id}, By: {request.user}")

        if request.method == 'POST':
            form = UserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                logger.info(f"User updated successfully - Target: {user.username}, ID: {user_id}, By: {request.user}")
                return redirect('click32_admin:user_list')
            else:
                logger.warning(f"User edit form invalid - Target: {user.username}, Errors: {form.errors}, By: {request.user}")
        else:
            form = UserChangeForm(instance=user)
        return render(request, 'click32_admin/user_form.html', {'form': form, 'title': 'Editar Usuário', 'user': user})
    except User.DoesNotExist:
        logger.error(f"User not found for edit - User ID: {user_id}, By: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in user_edit - User ID: {user_id}, By: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def user_delete(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        if request.method == 'POST':
            username = user.username
            user.delete()
            logger.info(f"User deleted successfully - Username: {username}, ID: {user_id}, By: {request.user}")
            return redirect('click32_admin:user_list')
        logger.info(f"User delete confirmation - Target: {user.username}, ID: {user_id}, By: {request.user}")
        return render(request, 'click32_admin/user_confirm_delete.html', {'user': user})
    except User.DoesNotExist:
        logger.error(f"User not found for deletion - User ID: {user_id}, By: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in user_delete - User ID: {user_id}, By: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def user_change_password(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        logger.info(f"Password change accessed - Target: {user.username}, ID: {user_id}, By: {request.user}")

        if request.method == 'POST':
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                logger.info(f"Password changed successfully - Target: {user.username}, ID: {user_id}, By: {request.user}")
                return redirect('click32_admin:user_list')
            else:
                logger.warning(f"Password change form invalid - Target: {user.username}, By: {request.user}")
        else:
            form = PasswordChangeForm(user)
        return render(request, 'click32_admin/user_change_password.html', {'form': form, 'user': user})
    except User.DoesNotExist:
        logger.error(f"User not found for password change - User ID: {user_id}, By: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in user_change_password - User ID: {user_id}, By: {request.user}, Error: {str(e)}", exc_info=True)
        raise

# Group management views
@check_permission(lambda u: u.is_superuser)
def group_list(request):
    logger.info(f"Group list accessed - User: {request.user}")
    groups = Group.objects.all()
    logger.debug(f"Groups loaded - Count: {groups.count()}")
    return render(request, 'click32_admin/group_list.html', {'groups': groups})

@check_permission(lambda u: u.is_superuser)
def group_create(request):
    try:
        if request.method == 'POST':
            logger.info(f"Group creation attempted - User: {request.user}")
            form = GroupForm(request.POST)
            if form.is_valid():
                group = form.save()
                logger.info(f"Group created successfully - Group: {group.name}, ID: {group.id}, User: {request.user}")
                return redirect('click32_admin:group_list')
            else:
                logger.warning(f"Group creation form invalid - Errors: {form.errors}, User: {request.user}")
        else:
            form = GroupForm()
        return render(request, 'click32_admin/group_form.html', {'form': form, 'title': 'Criar Grupo'})
    except Exception as e:
        logger.error(f"Error in group_create - User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def group_edit(request, group_id):
    try:
        group = get_object_or_404(Group, pk=group_id)
        logger.info(f"Group edit accessed - Group: {group.name}, ID: {group_id}, User: {request.user}")

        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                logger.info(f"Group updated successfully - Group: {group.name}, ID: {group_id}, User: {request.user}")
                return redirect('click32_admin:group_list')
            else:
                logger.warning(f"Group edit form invalid - Group: {group.name}, Errors: {form.errors}, User: {request.user}")
        else:
            form = GroupForm(instance=group)
        return render(request, 'click32_admin/group_form.html', {'form': form, 'title': 'Editar Grupo', 'group': group})
    except Group.DoesNotExist:
        logger.error(f"Group not found for edit - Group ID: {group_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in group_edit - Group ID: {group_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def group_delete(request, group_id):
    try:
        group = get_object_or_404(Group, pk=group_id)
        if request.method == 'POST':
            group_name = group.name
            group.delete()
            logger.info(f"Group deleted successfully - Group: {group_name}, ID: {group_id}, User: {request.user}")
            return redirect('click32_admin:group_list')
        logger.info(f"Group delete confirmation - Group: {group.name}, ID: {group_id}, User: {request.user}")
        return render(request, 'click32_admin/group_confirm_delete.html', {'group': group})
    except Group.DoesNotExist:
        logger.error(f"Group not found for deletion - Group ID: {group_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in group_delete - Group ID: {group_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise

@check_permission(lambda u: u.is_superuser)
def _generate_report_data(request, store_id, start_date, end_date):
    """
    Gera report_data pronto para o template
    """
    try:
        logger.info(f"Generating report data - Store ID: {store_id}, Period: {start_date} to {end_date}, User: {request.user}")
        
        clicks_data = get_clicks_data(store_id=store_id, start_date=start_date, end_date=end_date)
        if not clicks_data:
            logger.warning(f"No clicks data found for report - Store ID: {store_id}, Period: {start_date} to {end_date}")
            return None

        store_data = clicks_data[0]
        store = store_data['store']

        timeline_raw = get_timeline_data(store_id=store_id, start_date=start_date, end_date=end_date)
        link_clicks_full = get_total_clicks_by_link_type(store_id=store_id, start_date=start_date, end_date=end_date)
        engagement = get_engagement_rate(store_id=store_id, start_date=start_date, end_date=end_date)
        profile_accesses = get_profile_accesses(store_id=store_id, start_date=start_date, end_date=end_date)
        total_clicks = get_global_clicks(store_id=store_id, start_date=start_date, end_date=end_date)

        # map de links configuráveis
        link_map = {
            'whatsapp_1': {'label': 'WhatsApp 1', 'field': store.whatsapp_link_1},
            'whatsapp_2': {'label': 'WhatsApp 2', 'field': store.whatsapp_link_2},
            'phone': {'label': 'Telefone', 'field': store.phone_link},
            'instagram': {'label': 'Instagram', 'field': store.instagram_link},
            'facebook': {'label': 'Facebook', 'field': store.facebook_link},
            'youtube': {'label': 'YouTube', 'field': store.youtube_link},
            'x_link': {'label': 'X Link', 'field': store.x_link},
            'google_maps': {'label': 'Google Maps', 'field': store.google_maps_link},
            'anota_ai': {'label': 'Anota Ai', 'field': store.anota_ai_link},
            'ifood': {'label': 'iFood', 'field': store.ifood_link},
            'flyer': {'label': 'Flyer', 'field': store.flyer_pdf},
        }

        # origem dos totais por tipo de link
        full_labels = link_clicks_full.get('labels', [])
        full_data = link_clicks_full.get('data', [])

        # monta lista de links configurados
        link_keys = ['whatsapp_1', 'whatsapp_2', 'phone', 'instagram', 'facebook', 'youtube', 'x_link', 'google_maps', 'anota_ai', 'ifood', 'flyer']
        configured_links = []
        for key in link_keys:
            info = link_map.get(key)
            if not info:
                continue
            if info['field']:
                idx = link_keys.index(key)
                val = full_data[idx] if idx < len(full_data) else 0
                configured_links.append({'key': key, 'label': info['label'], 'data': int(val)})

        # soma total de cliques em links
        total_links_sum = sum(l['data'] for l in configured_links)

        # Ordena os items por data desc
        configured_links_sorted = sorted(configured_links, key=lambda x: x['data'], reverse=True)

        # Cria labels/data consistentes
        link_clicks = {
            'labels': [l['label'] for l in configured_links_sorted],
            'data': [l['data'] for l in configured_links_sorted]
        }

        # timeline_raw -> timeline_list
        labels = timeline_raw.get('labels', [])
        links_dict = timeline_raw.get('links', {})

        timeline_list = []
        for i, label in enumerate(labels):
            day_total = 0
            day_top_link = None
            day_top_value = 0
            for key, arr in links_dict.items():
                if key not in link_map or not link_map[key]['field']:
                    continue
                value = arr[i] if i < len(arr) else 0
                day_total += int(value)
                if int(value) > day_top_value:
                    day_top_value = int(value)
                    day_top_link = link_map[key]['label']
            timeline_list.append({
                'label': label,
                'total': day_total,
                'top_link': day_top_link or 'Nenhum'
            })

        # non_zero_days
        non_zero_days = sum(1 for d in timeline_list if d['total'] > 0)

        # peak day
        if timeline_list and any(d['total'] > 0 for d in timeline_list):
            peak_day = max(timeline_list, key=lambda d: d['total'])
            peak_day_label = peak_day['label']
            peak_day_total = peak_day['total']
            peak_percent_links = round((peak_day_total / total_links_sum * 100) if total_links_sum > 0 else 0, 1)
        else:
            peak_day_label = None
            peak_day_total = 0
            peak_percent_links = 0.0

        # Monta items já ordenados
        items = []
        for l in configured_links_sorted:
            pct = round((l['data'] / total_links_sum * 100) if total_links_sum > 0 else 0, 1)
            items.append({'label': l['label'], 'data': l['data'], 'percent': pct})
        
        # Buscar compartilhamentos do mês
        shares_count = ShareTrack.objects.filter(
            store_id=store_id,
            shared_at__date__gte=start_date,
            shared_at__date__lte=end_date
        ).count()

        report_data = {
            'store_name': store.name,
            'period': {'start': start_date.strftime('%Y-%m-%d'), 'end': end_date.strftime('%Y-%m-%d')},
            'overview': {
                'total_clicks': total_clicks,
                'profile_accesses': profile_accesses,
                'secondary_clicks': store_data.get('secondary_clicks', 0),
                'engagement_rate': f"{engagement}%",
            },
            'timeline': timeline_list,
            'timeline_raw': timeline_raw,
            'links_distribution': {
                'labels': link_clicks['labels'],
                'data': link_clicks['data'],
                'items': items
            },
            'last_activity': store_data.get('last_clicked').strftime('%d/%m/%Y %H:%M') if store_data.get('last_clicked') else None,
            'peak_day': peak_day_label,
            'peak_day_total': peak_day_total,
            'peak_day_percent_links': peak_percent_links,
            'non_zero_days': non_zero_days,
            'warning': 'Nenhum link configurado.' if not configured_links else None,
            'shares_count': shares_count,
        }

        logger.info(f"Report data generated successfully - Store: {store.name}, Total clicks: {total_clicks}, Timeline days: {len(timeline_list)}")
        return report_data

    except Exception as e:
        logger.error(f"Error generating report data - Store ID: {store_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        return None

@check_permission(lambda u: u.is_superuser)
def monthly_report_api(request, store_id):    
    try:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        logger.info(f"Monthly report API accessed - Store ID: {store_id}, User: {request.user}")
        
        report_data = _generate_report_data(request, store_id, start_date, end_date)
        if not report_data:
            logger.warning(f"No report data found for API - Store ID: {store_id}")
            return JsonResponse({'error': 'Loja não encontrada ou sem dados'}, status=404)
        
        return JsonResponse(report_data)
        
    except Exception as e:
        logger.error(f"Error in monthly_report_api - Store ID: {store_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)

@check_permission(lambda u: u.is_superuser)
def monthly_report_view(request, store_id):
    try:
        store = get_object_or_404(Store, id=store_id)
        logger.info(f"Monthly report view accessed - Store: {store.name}, ID: {store_id}, User: {request.user}")

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        report_data = _generate_report_data(request, store_id, start_date, end_date)
        if not report_data:
            logger.warning(f"No report data found for view - Store: {store.name}, ID: {store_id}")
            context = {'store_name': store.name, 'error': 'Sem dados para este período.'}
            return render(request, 'click32_admin/monthly_report.html', context)
        
        context = {
            'store_id': store_id,
            'store_name': store.name,
            'report_data': report_data,
            'now': timezone.now(),
        }
        
        logger.info(f"Monthly report rendered successfully - Store: {store.name}, User: {request.user}")
        return render(request, 'click32_admin/monthly_report.html', context)
        
    except Store.DoesNotExist:
        logger.error(f"Store not found for monthly report - Store ID: {store_id}, User: {request.user}")
        raise
    except Exception as e:
        logger.error(f"Error in monthly_report_view - Store ID: {store_id}, User: {request.user}, Error: {str(e)}", exc_info=True)
        raise