from analyzers import image_analyzer
import google.generativeai as genai
from utils.ai_retry import call_with_retry
import os

def extract_detailed_analysis(pages_data, file_path=None):
    """
    Generates the Detailed Analysis report.
    Uses MULTIMODAL PDF analysis (if file_path provided) to ensure 
    precision in signatures and timestamps.
    Follows Official Prompt V1.02 - Ajuste Clasificación Tipo de Firma.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Consolidate text data and image descriptions for context (PRIMARY SOURCE)
    full_document_context = ""
    visual_evidence_summary = ""
    
    for p in pages_data:
        full_document_context += f"--- PÁGINA {p['page_number']} ---\n"
        full_document_context += f"[TEXTO OCR]:\n{p['text_content']}\n"
        
        # Recuperar interpretaciones ya ejecutadas en el Análisis Inicial
        images = p.get('images', [])
        if images:
            for img in images:
                desc = img.get('description', '')
                if desc and "[SKIP]" not in desc.upper():
                    findings = f"- Pág {p['page_number']} | Imagen {img['name']}: {desc}\n"
                    full_document_context += f"[HALLAZGO VISUAL PREVIO]: {findings}"
                    visual_evidence_summary += findings
        full_document_context += "\n"

    main_prompt = f"""
    Eres ANTIGRAVITY - ORQUESTADOR DE SÍNTESIS DE AUDITORÍA.
    
    TU MISIÓN: Generar el 'Informe de Auditoría Detallado' consolidando la información de la 'GUÍA DE DATOS PREVIOS'.
    
    CRÍTICO - SOBERANÍA DE DATOS:
    1. Si en la 'GUÍA DE DATOS PREVIOS' ya existe un [HALLAZGO VISUAL PREVIO] que describa un DIAGRAMA DE FLUJO, UTILÍZALO para el campo 'interpretacion_diagrama_flujo'. No intentes re-interpretarlo, sintetiza lo que ya se detectó.
    2. Lo mismo aplica para Firmas, Sellos y Tablas. Confía 100% en las interpretaciones previas proporcionadas.

    INSTRUCCIONES DE ESTRUCTURA:
    - REVISADO Y APROBADO: Extrae nombres y puestos de forma literal. Clasifica la firma como 'Firma Electrónica' o 'Manual' basándote en el OCR y evidencias visuales previas.
    - POLÍTICAS Y PROCEDIMIENTOS: Transcripción íntegra y resumen ejecutivo.
    - Si un dato no existe en la guía, responde 'No identificado en el documento'.

    --- GUÍA DE DATOS PREVIOS (SOBERANÍA DE ANÁLISIS) ---
    {full_document_context}
    --- FIN GUÍA ---

    GENERAR JSON ESTRUCTURADO:
    {{
      "contenido_principal": {{
        "tipo_no_documento": "...",
        "numero_revision": "...",
        "fecha_efectividad": "...",
        "titulo_documento": "...",
        "elaborado_por": "...",
        "razon_cambio": "..."
      }},
      "revisado_aprobado": [
        {{ 
            "nombre": "Nombre exacto", 
            "puesto": "Puesto exacto", 
            "firma": "...", 
            "fecha": "Timestamp completo" 
        }}
      ],
      "objetivo_completo": "...",
      "alcance_completo": "...",
      "interpretacion_diagrama_flujo": "SÍNTESIS MAESTRA de los diagramas descritos en la guía previa.",
      "politicas": {{
        "texto_completo": "...",
        "identificacion_participantes_ia": ["..."],
        "resumen_politica_ia": "..."
      }},
      "procedimientos": {{
        "texto_completo": "...",
        "lista_responsables": ["..."]
      }}
    }}
    """

    try:
        # Nota: Ya no adjuntamos el archivo visual (multimodal) por defecto para ahorrar tokens y forzar el uso de la guía.
        # Solo se enviaría si fuera estrictamente necesario, pero la guía ya es rica en contenido.
        response = call_with_retry(model.generate_content, main_prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        return clean_response
    except Exception as e:
        return f"Error en síntesis detallada: {str(e)}"


