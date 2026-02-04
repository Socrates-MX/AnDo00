import unicodedata

def clean_text(t):
    if not t: return ""
    return "".join(c for c in t if c.isalnum()).replace(" ", "").lower()

def get_tokens(text):
    if not text: return set()
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    except: pass
    text = "".join(c if c.isalnum() else " " for c in text.lower())
    return set(text.split())

def analyze_impersonation(pages_data, detailed_report):
    """
    Análisis de suplantación desactivado por solicitud del usuario.
    Retorna una lista vacía para evitar alertas de falsos positivos en sellos digitales.
    """
    return []
