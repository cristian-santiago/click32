import os
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='fa-th')
    tags = models.ManyToManyField(Tag, blank=True, related_name='categories')

    def __str__(self):
        return self.name

def store_image_path(instance, filename):
    store_slug = slugify(instance.name or "no-name")
    return f"stores/{store_slug}/{filename}"

class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    main_banner = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_2 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_3 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_4 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    highlight = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    whatsapp_link = models.URLField("WhatsApp", blank=True, null=True)
    instagram_link = models.URLField("Instagram", blank=True, null=True)
    facebook_link = models.URLField("Facebook", blank=True, null=True)
    x_link = models.URLField("X", blank=True, null=True)
    google_maps_link = models.URLField("Google Maps", max_length=300, blank=True, null=True)
    youtube_link = models.URLField("YouTube", blank=True, null=True)
    website_link = models.URLField("Site Oficial", blank=True, null=True)
    flyer_pdf = models.FileField(upload_to='flyers/', blank=True, null=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    def __str__(self):
        return self.name

class ClickTrack(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='clicktrack', null=True, blank=True)
    element_type = models.CharField(max_length=50, choices=[
        ('main_banner', 'Main Banner'),
        ('whatsapp_link', 'WhatsApp Link'),
        ('instagram_link', 'Instagram Link'),
        ('facebook_link', 'Facebook Link'),
        ('youtube_link', 'YouTube Link'),
        ('x_link', 'X Link'),
        ('google_maps_link', 'Google Maps Link'),
        ('website_link', 'Website Link'),
        ('home_access', 'Home Access'),
        ('flyer_pdf', 'flyer PDF'),
    ])
    click_count = models.PositiveIntegerField(default=0)
    last_clicked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'element_type')

    def __str__(self):
        store_name = self.store.name if self.store else 'No Store'
        return f"{store_name} - {self.element_type} - {self.click_count} clicks"