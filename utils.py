import re

def get_social_network(url):
    """
    Determina la red social a partir de una URL.
    """
    if not url:
        return "Desconocido"
    
    url_lower = url.lower()
    
    if "twitter.com" in url_lower or "x.com" in url_lower:
        return "X (Twitter)"
    elif "instagram.com" in url_lower:
        return "Instagram"
    elif "facebook.com" in url_lower or "fb.com" in url_lower:
        return "Facebook"
    elif "tiktok.com" in url_lower:
        return "TikTok"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube"
    else:
        # Intenta extraer un nombre de dominio más genérico si no es uno conocido
        match = re.search(r'https?://(?:www\.)?([^/]+)', url_lower)
        if match:
            return match.group(1)
        return "Desconocido"
