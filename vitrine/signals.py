# stores/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Store

@receiver([post_save, post_delete], sender=Store)
def clear_home_cache(sender, instance, **kwargs):
    print(f"Signal disparado para Store: {instance.name}")
    cache.clear()  # limpa todo o cache do Django
