import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

def analyze_images_on_page(page_content):
    """
    Analyzes images on a page.
    Currently a placeholder for extraction logic, but connected to generation.
    """
    return []

def generate_image_description(image_bytes):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[ERROR] API Key no configurada en .env.", {}
    
    # gpt-3.5-turbo no soporta Vision, por lo tanto saltamos el análisis de imágenes
    return "[SKIP] Análisis visual deshabilitado (Modelo gpt-3.5-turbo no soporta Vision)", {}

def generate_text_interpretation(text_content):
    """
    Sends raw page text to OpenAI for an executive interpretation.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[ERROR] API Key no configurada.", {}
    
    client = OpenAI(api_key=api_key)

    if not text_content or len(text_content.strip()) < 10:
        return "No hay suficiente texto para interpretar.", {}

    try:
        prompt = (
            "Analiza el siguiente texto extraído de una página de un documento corporativo.\\n"
            "TAREA: Proporciona una INTERPRETACIÓN ejecutiva y concreta de este contenido.\\n"
            "Enfócate en obligaciones, hallazgos, riesgos o datos clave para una auditoría.\\n"
            "Evita introducciones innecesarias. Sé directo y profesional.\\n\\n"
            f"TEXTO A ANALIZAR:\\n{text_content}"
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Capture usage data
        usage = response.usage
        usage_data = {}
        if usage:
            usage_data = {
                "prompt_token_count": usage.prompt_tokens,
                "candidates_token_count": usage.completion_tokens,
                "total_token_count": usage.total_tokens
            }
            
        return response.choices[0].message.content.strip(), usage_data
    except Exception as e:
        return f"[ERROR] Falló OpenAI (Texto): {str(e)}", {}
