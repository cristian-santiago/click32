from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid

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
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            # Evita duplicidade de slug
            while Store.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    main_banner = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_2 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_3 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    carousel_4 = models.ImageField(upload_to=store_image_path, blank=True, null=True)
    highlight = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    is_deactivated = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    # Links 
    whatsapp_link_1 = models.URLField("WhatsApp_1", blank=True, null=True)
    whatsapp_link_2 = models.URLField("WhatsApp_2", blank=True, null=True)
    phone_link = models.CharField(max_length=20, blank=True, null=True)
    instagram_link = models.URLField("Instagram", blank=True, null=True)
    facebook_link = models.URLField("Facebook", blank=True, null=True)
    x_link = models.URLField("X", blank=True, null=True)
    google_maps_link = models.URLField("Google Maps", max_length=300, blank=True, null=True)
    youtube_link = models.URLField("YouTube", blank=True, null=True)
    anota_ai_link = models.URLField("Anota Ai", blank=True, null=True)
    ifood_link = models.URLField("iFood", blank=True, null=True)
    flyer_pdf = models.FileField(upload_to='flyers/', blank=True, null=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    def __str__(self):
        return self.name

class StoreOpeningHour(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='opening_hours')
    day_range = models.CharField(max_length=50)  # Ex: "Seg–Sex", "Sáb", "Dom"
    time_range = models.CharField(max_length=50) # Ex: "09h–19h"

    def __str__(self):
        return f"{self.day_range} {self.time_range}"

class ClickTrack(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='clicktrack', null=True, blank=True)
    element_type = models.CharField(max_length=50, choices=[
        ('main_banner', 'Main Banner'),
        ('whatsapp_link_1', 'WhatsApp Link 1'),
        ('whatsapp_link_2', 'WhatsApp Link 2'),
        ('instagram_link', 'Instagram Link'),
        ('facebook_link', 'Facebook Link'),
        ('youtube_link', 'YouTube Link'),
        ('x_link', 'X Link'),
        ('google_maps_link', 'Google Maps Link'),
        ('anota_ai_link', 'Anota Ai Link'),
        ('ifood_link', 'iFood Link'),
        ('phone_link', 'Phone Link'),
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

class ShareTrack(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shares')
    shared_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        indexes = [
            models.Index(fields=['store', 'shared_at']),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.shared_at.strftime('%d/%m/%Y %H:%M')}"
    
class PWADownloadClick(models.Model):
    ACTION_CHOICES = [
        ('clicked', 'Botão Clicado'),
        ('accepted', 'Instalação Aceita'),
        ('dismissed', 'Instalação Cancelada'),
    ]
    
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='clicked')
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "PWA Download Click"
        verbose_name_plural = "PWA Download Clicks"

    def __str__(self):
        return f"PWA {self.get_action_display()} - {self.clicked_at.strftime('%d/%m/%Y %H:%M')}"
    
class ActiveSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['last_activity']),
        ]
        verbose_name = "Sessão Ativa"
        verbose_name_plural = "Sessões Ativas"

    def __str__(self):
        return f"Sessão {self.session_id} - {self.last_activity.strftime('%H:%M')}"
    
    def is_active(self, minutes=5):
        """Verifica se a sessão está ativa nos últimos X minutos"""
        return (timezone.now() - self.last_activity).total_seconds() < (minutes * 60)