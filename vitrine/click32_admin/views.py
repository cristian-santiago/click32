import os
import shutil
import logging
from django.urls import path
from django.http import JsonResponse
from .forms import StoreForm, TagForm, CategoryForm
from vitrine.models import Store, Tag, Category
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Max, Q
from django.utils.text import slugify
import json
from django.utils.safestring import mark_safe
from .functions import get_site_metrics, get_clicks_data, get_store_count, get_total_clicks_by_link_type, get_global_clicks, get_profile_accesses, get_heatmap_data, get_timeline_data, get_comparison_data, get_store_highlight_data, get_engagement_rate

from .forms import StoreForm

logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'click32_admin/dashboard.html')


def store_list(request):
    stores = Store.objects.all()
    return render(request, 'click32_admin/store_list.html', {'stores': stores})

def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.save()

            # Recebe e associa tags manualmente
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




    
@require_POST
def store_delete(request, store_id):
    store = get_object_or_404(Store, pk=store_id)

    if request.method == 'POST':
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

   # return render(request, 'click32_admin/confirm_delete.html', {'store': store})

def clicks_dashboard(request):
      
    clicks_data = get_clicks_data()
    return render(request, 'click32_admin/clicks_dashboard.html', {
        'clicks_data': clicks_data,
    })



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
#----------

def login_view(request):
    return render(request, 'click32_admin/login.html')


# TAGS VIEWS



def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'click32_admin/tag_list.html', {'tags': tags})

def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('click32_admin:tag_list')
    else:
        form = TagForm()
    return render(request, 'click32_admin/tag_form.html', {'form': form})

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

def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        tag.delete()
        return redirect('click32_admin:tag_list')
    #return render(request, 'click32_admin/tag_confirm_delete.html', {'tag': tag})

# Category view


def category_list(request):
    categories = Category.objects.prefetch_related('tags').all()
    return render(request, 'click32_admin/category_list.html', {'categories': categories})


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return redirect('click32_admin:category_list')
    else:
        form = CategoryForm()
    return render(request, 'click32_admin/category_form.html', {'form': form})


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


def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('click32_admin:category_list')
    return render(request, 'click32_admin/category_confirm_delete.html', {'category': category})

#-----------#
# API

def total_clicks_by_link_type_api(request):
    data = get_total_clicks_by_link_type()
    return JsonResponse(data)

def timeline_data_api(request):
    data = get_timeline_data()
    return JsonResponse(data)