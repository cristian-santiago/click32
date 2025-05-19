import os
import shutil
from django.contrib import admin
from django.utils.html import format_html
from .models import Store, Tag
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name','highlight', 'display_tags')
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
            'fields':('name', 'description', 'highlight', 'tags')
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
            'description': 'Fill only with the available contacts.'
        }),
        ('Images', {
            'fields':(
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

    # TAGS DISPLAYED
    def get_queryset(self, request):
        
        qs = super().get_queryset(request)
        return qs.prefetch_related('tags') # improve performance
    
    def display_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all()) 
    display_tags.short_description = 'Tags' # column name


    #BANNERS & CAROUSEL
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

    # WHEN DELETE DELETE THE STORE
    def delete_model(self, request, obj):
        # Delete images from file system
        for image_field in [obj.main_banner, obj.carousel_2, obj.carousel_3, obj.carousel_4]:
            if image_field and os.path.isfile(image_field.path):
                try:
                    os.remove(image_field.path)
                    logger.info(f"Deleted image: {image_field.path}")
                except Exception as e:
                    logger.error(f"Error deleting image {image_field.path}: {e}")

        # Delete the store directory if it exists
        store_dir = os.path.join('media', f'stores/{slugify(obj.name)}')
        if os.path.isdir(store_dir):
            try:
                shutil.rmtree(store_dir)
                logger.info(f"Deleted store directory: {store_dir}")
            except Exception as e:
                logger.error(f"Error deleting store directory {store_dir}: {e}")

        # Delete the object from the database
        super().delete_model(request, obj)

    # DELETE OLD IMGs WHEN UPLOADIN NEW ONES
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Store.objects.get(pk=obj.pk)
            for field_name in ['main_banner', 'carousel_2', 'carousel_3', 'carousel_4']:
                old_file = getattr(old_obj, field_name)
                new_file = getattr(obj, field_name)

                if old_file and old_file != new_file:
                    if os.path.isfile(old_file.path):
                        try:
                            os.remove(old_file.path)
                            logger.info(f"Deleted old file: {old_file.path}")
                        except Exception as e:
                            logger.error(f"Error deleting old file {old_file.path}: {e}")
                        
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']