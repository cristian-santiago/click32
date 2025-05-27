import logging
from django.shortcuts import get_object_or_404
from .models import Store, ClickTrack

logger = logging.getLogger(__name__)

class ClickTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se a requisição contém parâmetros de clique
        store_id = request.GET.get('store_id')
        element_type = request.GET.get('element_type')
        valid_elements = [
            'main_banner', 'whatsapp_link', 'instagram_link', 'facebook_link',
            'youtube_link', 'x_link', 'google_maps_link', 'website_link'
        ]

        if store_id and element_type in valid_elements:
            try:
                store = get_object_or_404(Store, id=store_id)
                click_track, created = ClickTrack.objects.get_or_create(
                    store=store,
                    element_type=element_type,
                    defaults={'click_count': 1}
                )
                if not created:
                    click_track.click_count += 1
                    click_track.save()
                logger.info(f"Click tracked: {store.name} - {element_type}")
            except Exception as e:
                logger.error(f"Error tracking click: {e}")

        response = self.get_response(request)
        return response