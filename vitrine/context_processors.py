from django.conf import settings

def static_version(request):  # Precisa receber request
    return {
        'STATIC_VERSION': settings.STATIC_VERSION,
    }