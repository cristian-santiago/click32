import os
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


def store_image_path(instance, filename):
    #create a path like: stores/store_id/banner.img
    
    store_slug = slugify(instance.name or "no-name")
    return f"stores/{store_slug}/{filename}"

class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    # Image section
    #image  = models.ImageField(upload_to='stores/', blank=True, null=True) 
    main_banner = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_2 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_3 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_4 = models.ImageField(upload_to=store_image_path, blank=True, null=True)

    # Customer premium section
    highlight = models.BooleanField(default=False)
    
    # filter the store by tags
    tags = models.ManyToManyField(Tag, blank=True)

    # external links
    #external_link = models.URLField(help_text="Link para WPP, iFood")
    whatsapp_link = models.URLField("WhatsApp", blank=True, null=True)
    instagram_link = models.URLField("Instagram", blank=True, null=True)
    facebook_link = models.URLField("Facebook", blank=True, null=True)
    youtube_link = models.URLField("Youtube", blank=True, null=True)
    website_link = models.URLField("Site Oficial", blank=True, null=True)
    
    def __str__(self):
        return self.name
    
   
    