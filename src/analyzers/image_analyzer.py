import os
import google.generativeai as genai
from utils.ai_retry import call_with_retry
from dotenv import load_dotenv

load_dotenv()

# genai configuration will be handled inside functions to ensure fresh API keys

def analyze_images_on_page(page_content):
    """
    Analyzes images on a page.
    Currently a placeholder for extraction logic, but connected to generation.
    """
    # In a real scenario, we would extract image bytes here.
    # For this prototype, we return an empty list or mock data to valid integration.
    return []

from PIL import Image
import io

def generate_image_description(image_bytes):
    """
    Sends image bytes to Google Gemini for real description.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return "[ERROR] API Key no configurada en .env."
    
    genai.configure(api_key=api_key)

    try:
        # Detect MIME type using PIL instead of deprecated imghdr
        img = Image.open(io.BytesIO(image_bytes))
        mime_type = Image.MIME.get(img.format, "image/png")
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        response = call_with_retry(model.generate_content, [
            "Analiza esta imagen extraída de un documento PDF para una auditoría.\n"
            "REGLAS:\n"
            "1. Si es LOGOTIPO o MARCA DE AGUA decorativa, responde: [SKIP]\n"
            "2. Si es sustantiva (gráficos, tablas, firmas): Extrae texto (OCR) e interpreta "
            "de manera CONCRETA el significado para el negocio/auditoría.",
            image_part
        ])
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] Falló Gemini (Imagen): {str(e)}"

def generate_text_interpretation(text_content):
    """
    Sends raw page text to Gemini for an executive interpretation.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return "[ERROR] API Key no configurada."
    
    genai.configure(api_key=api_key)

    if not text_content or len(text_content.strip()) < 10:
        return "No hay suficiente texto para interpretar."

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = call_with_retry(model.generate_content, [
            "Analiza el siguiente texto extraído de una página de un documento corporativo.\n"
            "TAREA: Proporciona una INTERPRETACIÓN ejecutiva y concreta de este contenido.\n"
            "Enfócate en obligaciones, hallazgos, riesgos o datos clave para una auditoría.\n"
            "Evita introducciones innecesarias. Sé directo y profesional.\n\n"
            f"TEXTO A ANALIZAR:\n{text_content}"
        ])
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] Falló Gemini (Texto): {str(e)}"
