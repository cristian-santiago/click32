# stores/signals.py
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Store
import os

@receiver(post_save, sender=Store)
def handle_store_save(sender, instance, **kwargs):
    """
    Gerencia cache quando Store é salva
    """
    print(f"Store salva: {instance.name}")
    
    # Limpa arquivos de cache do flyer manualmente
    try:
        cache_dir = '/tmp/django_cache'  # Mesmo do seu settings
        
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.startswith(f'flyer_{instance.id}_'):
                    filepath = os.path.join(cache_dir, filename)
                    os.remove(filepath)
                    print(f"Removido cache: {filename}")
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
    
    print(f"Cache de flyer limpo - Store: {instance.name}")

@receiver(post_delete, sender=Store)
def handle_store_delete(sender, instance, **kwargs):
    """
    Gerencia cache quando Store é deletada
    """
    print(f"Store deletada: {instance.name}")
    
    # Limpa arquivos de cache do flyer manualmente
    try:
        cache_dir = '/tmp/django_cache'
        
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.startswith(f'flyer_{instance.id}_'):
                    filepath = os.path.join(cache_dir, filename)
                    os.remove(filepath)
                    print(f"Removido cache: {filename}")
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
    
    print(f"Cache de flyer limpo - Store deletada: {instance.name}")