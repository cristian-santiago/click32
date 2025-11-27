
from django import template
from urllib.parse import urlparse
import re

register = template.Library()

@register.filter
def deep_link(web_url, platform):
    
    #Gera deep link a partir de URL web, baseado na plataforma.
    #Ex.: deep_link:"https://www.instagram.com/click32.app/":"instagram" -> "instagram://user?username=click32.app"
    
    if not web_url:
        return ''
    
    # Parse básico pra extrair path
    parsed = urlparse(web_url)
    path = parsed.path.strip('/').split('/')  # Ex.: ['click32.app'] pra Instagram
    
    if platform == 'instagram':
        username = path[0] if path else ''  # Assume /username/
        return f"instagram://user?username={username}"
    
    elif platform == 'whatsapp':
        return web_url  # ← NÃO altera WhatsApp
    
    elif platform == 'youtube':
        # Assume /channel/UC... ou /watch?v=ID
        if 'watch?v=' in web_url:
            video_id = re.search(r'v=([^&]+)', web_url).group(1)
            return f"youtube://watch?v={video_id}"
        else:
            channel_id = path[-1] if path else ''
            return f"youtube://channel/{channel_id}"
    
    elif platform == 'facebook':
        page_name = path[1] if len(path) > 1 else ''  # /page_name
        return f"fb://page/{page_name}"
    
    elif platform == 'x':  # Twitter
        username = path[0].lstrip('@') if path else ''
        return f"twitter://user?screen_name={username}"
    
    elif platform == 'google_maps':
        # Assume https://maps.google.com/?q=lat,lng ou place
        query = parsed.query
        return f"google.navigation:q={query}" if query else web_url # Fallback
    
    elif platform == 'ifood':
        # iFood usa web app, mas se tiver deep: ifood://
        return f"ifood://store/{path[-1]}" if path else web_url  #
    
    # Adicionar mais plataformas aqui (anota_ai, etc.)
    else:
        return web_url  # Fallback pra web se plataforma desconhecida

    