import os
import shutil
import logging
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.db.models import Sum
from django.utils.text import slugify

from .models import Store, Tag, ClickTrack
from .admin_site import click32_admin_site

logger = logging.getLogger(__name__)

class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'highlight', 'display_tags')
    filter_horizontal = ('tags',)
    search_fields = ('name',)
    readonly_fields = (
        'main_banner_preview',
        'carousel_2_preview',
        'carousel_3_preview',
        'carousel_4_preview',
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'highlight', 'tags')
        }),
        ('Links de Contato', {
            'fields': (
                'whatsapp_link',
                'instagram_link',
                'facebook_link',
                'youtube_link', 
                'x_link',
                'google_maps_link',     
                'website_link',
            ),
            'description': 'Preencha apenas os contatos disponíveis.'
        }),
        ('Imagens', {
            'fields': (
                'main_banner',
                'main_banner_preview',
                'carousel_2',
                'carousel_2_preview',
                'carousel_3',
                'carousel_3_preview',
                'carousel_4',
                'carousel_4_preview',
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clicks-dashboard/', self.admin_site.admin_view(self.clicks_dashboard), name='clicks_dashboard'),
        ]
        return custom_urls + urls

    def clicks_dashboard(self, request):
        clicks_data = (
            ClickTrack.objects
            .values('store__name', 'element_type')
            .annotate(total_clicks=Sum('click_count'))
            .order_by('-total_clicks')
        )
        context = {
            'clicks_data': clicks_data,
            'title': 'Clicks Dashboard',
        }
        return render(request, 'admin/clicks_dashboard.html', context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('tags')

    def display_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'

    # Image preview helpers
    def main_banner_preview(self, obj):
        if obj.main_banner:
            return format_html('<img src="{}" width="200" />', obj.main_banner.url)
        return "No image"
    main_banner_preview.short_description = "Main banner preview"

    def carousel_2_preview(self, obj):
        if obj.carousel_2:
            return format_html('<img src="{}" width="200" />', obj.carousel_2.url)
        return "No image"
    carousel_2_preview.short_description = "Carousel 2 preview"

    def carousel_3_preview(self, obj):
        if obj.carousel_3:
            return format_html('<img src="{}" width="200" />', obj.carousel_3.url)
        return "No image"
    carousel_3_preview.short_description = "Carousel 3 preview"

    def carousel_4_preview(self, obj):
        if obj.carousel_4:
            return format_html('<img src="{}" width="200" />', obj.carousel_4.url)
        return "No image"
    carousel_4_preview.short_description = "Carousel 4 preview"

    def delete_model(self, request, obj):
        # Delete image files from disk when the store is deleted
        for image_field in [obj.main_banner, obj.carousel_2, obj.carousel_3, obj.carousel_4]:
            if image_field and os.path.exists(image_field.path):
                try:
                    os.remove(image_field.path)
                    logger.info(f"Deleted image: {image_field.path}")
                except Exception as e:
                    logger.error(f"Error deleting image {image_field.path}: {e}")
        
        # Delete store's directory (slugified store name)
        store_dir = os.path.join('media', f'stores/{slugify(obj.name)}')
        if os.path.isdir(store_dir):
            try:
                shutil.rmtree(store_dir)
                logger.info(f"Deleted store directory: {store_dir}")
            except Exception as e:
                logger.error(f"Error deleting store directory {store_dir}: {e}")
        super().delete_model(request, obj)

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Store.objects.get(pk=obj.pk)
            for field_name in ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4']:
                old_file = getattr(old_obj, field_name)
                new_file = getattr(obj, field_name)
                if old_file and old_file != new_file and os.path.exists(old_file.path):
                    try:
                        os.remove(old_file.path)
                        logger.info(f"Deleted old file: {old_file.path}")
                    except Exception as e:
                        logger.error(f"Error deleting old file {old_file.path}: {e}")
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        dashboard_url = reverse('click32_admin:clicks_dashboard')
        extra_context['clicks_dashboard_link'] = mark_safe(
            f'<a class="button" href="{dashboard_url}">Dashboard</a>'
        )
        return super().changelist_view(request, extra_context=extra_context)


class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

class ClickTrackAdmin(admin.ModelAdmin):
    list_display = ('store', 'element_type', 'click_count', 'last_clicked')
    list_filter = ('element_type', 'store')
    search_fields = ('store__name', 'element_type')


# Register models with the custom admin site
click32_admin_site.register(Store, StoreAdmin)
click32_admin_site.register(Tag, TagAdmin)
click32_admin_site.register(ClickTrack, ClickTrackAdmin)
click32_admin_site.register(User, UserAdmin)
click32_admin_site.register(Group, GroupAdmin)