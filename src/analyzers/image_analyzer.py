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
    """
    Sends image bytes to OpenAI for real description.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[ERROR] API Key no configurada en .env.", {}
    
    client = OpenAI(api_key=api_key)

    try:
        # Detect MIME type using PIL
        img = Image.open(io.BytesIO(image_bytes))
        mime_type = Image.MIME.get(img.format, "image/png")
        
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_url = f"data:{mime_type};base64,{base64_image}"
        
        prompt_text = (
            "Analiza esta imagen con rigor forense para auditoría.\\n"
            "ESCRUTINIO DE TIPO:\\n"
            "1. Si es LOGOTIPO, MARCA DE AGUA o elemento decorativo: Responde EXACTAMENTE: [SKIP]\\n"
            "2. Si es un DIAGRAMA DE FLUJO, PROCESO o TABLA DE DECISIÓN (CRÍTICO):\\n"
            "   Debes transcribir el flujo COMPLETO a texto lógico estructurado.\\n"
            "   FORMATO DE SALIDA:\\n"
            "   **TIPO:** [Diagrama de Flujo / Tabla / Gráfico]\\n"
            "   **PROCESO:** [Nombre inferido del proceso]\\n"
            "   **ROLES VISIBLES:** [Lista de carriles/actores si existen]\\n"
            "   **FLUJO LÓGICO PASO A PASO:**\\n"
            "   1. [Inicio] Descripción...\\n"
            "   2. [Actividad] ...\\n"
            "   3. [Decisión] ¿Condición? (Si -> Paso X, No -> Paso Y)\\n"
            "   ...\\n"
            "   [Fin] Conclusión.\\n"
            "   Asegura que NINGÚN paso visible sea omitido."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
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
        return f"[ERROR] Falló OpenAI (Imagen): {str(e)}", {}

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
            model="gpt-4o-mini",
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
