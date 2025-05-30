import os
from django.db import models
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=50)

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
    tags = models.ManyToManyField(Tag, blank=True)
    whatsapp_link = models.URLField("WhatsApp", blank=True, null=True)
    instagram_link = models.URLField("Instagram", blank=True, null=True)
    facebook_link = models.URLField("Facebook", blank=True, null=True)
    x_link = models.URLField("X", blank=True, null=True)
    google_maps_link = models.URLField("Google Maps", max_length=300, blank=True, null=True)
    youtube_link = models.URLField("YouTube", blank=True, null=True)
    website_link = models.URLField("Site Oficial", blank=True, null=True)

    def __str__(self):
        return self.name

class ClickTrack(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='clicktrack')
    element_type = models.CharField(max_length=50, choices=[
        ('main_banner', 'Main Banner'),
        ('whatsapp_link', 'WhatsApp Link'),
        ('instagram_link', 'Instagram Link'),
        ('facebook_link', 'Facebook Link'),
        ('youtube_link', 'YouTube Link'),
        ('x_link', 'X Link'),
        ('google_maps_link', 'Google Maps Link'),
        ('website_link', 'Website Link'),
    ])
    click_count = models.PositiveIntegerField(default=0)
    last_clicked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'element_type')

    def __str__(self):
        return f"{self.store.name} - {self.element_type} - {self.click_count} clicks"