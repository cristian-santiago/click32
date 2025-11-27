from django import template

register = template.Library()

@register.filter
def deep_link(web_url, platform):
    """
    Tenta converter URL web para deep link.
    Se não conseguir ou plataforma não suportar, mantém URL original.
    """
    if not web_url:
        return ''
    
    # WhatsApp: sempre mantém URL web (já funciona perfeitamente)
    if platform == 'whatsapp':
        return web_url
    
    # Plataformas que suportam deep links
    deep_link_map = {
        'instagram': f"instagram://user?username={web_url.split('/')[-1]}",
        'youtube': f"youtube://{web_url.split('//')[-1]}",  # youtube://www.youtube.com/...
        'facebook': f"fb://page/{web_url.split('/')[-1]}",
        'x': f"twitter://user?screen_name={web_url.split('/')[-1].lstrip('@')}",
        'ifood': f"ifood://store/{web_url.split('/')[-1]}",
        'google_maps': f"comgooglemaps://{web_url.split('?')[-1]}"
    }
    
    # Retorna deep link se a plataforma estiver no mapa, senão URL original
    return deep_link_map.get(platform, web_url)