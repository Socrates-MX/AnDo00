from analyzers import image_analyzer
import google.generativeai as genai
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

    # Consolidate text data for context
    full_text_context = ""
    for p in pages_data:
        full_text_context += f"--- PÁGINA {p['page_number']} ---\n{p['text_content']}\n\n"

    # Multimodal Payload
    prompt_items = []
    
    if file_path and os.path.exists(file_path):
        try:
            # Upload PDF to Gemini
            doc_file = genai.upload_file(path=file_path, display_name="Documento_Auditoria")
            prompt_items.append(doc_file)
        except Exception as e:
            print(f"Fallback to text-only: {e}")

    main_prompt = f"""
    Eres un asistente de auditoría de ALTA PRECISIÓN. Tu tarea es generar la sección 'Análisis Detallado'.
    
    CRÍTICO: Observa visualmente las tablas de 'REVISADO Y APROBADO' o 'FIRMAS' en el PDF. 
    Sigue estrictamente estas reglas:

    REGLA DE LA COLUMNA 'FIRMA' (Sección 3):
    - NO muestres nombres propios ni el texto que aparece dentro de la firma.
    - CLASIFICA el tipo de firma en una de estas 3 categorías:
        1. 'Firma Electrónica': Si detectas nombre digitado (no trazo), leyendas de 'Aprobado/Firmado electrónicamente' o timestamps (fecha/hora) con formato digital automático junto a la firma.
        2. 'Firma Manual Escrita': Si detectas un trazo manuscrito (rúbrica), firma escaneada manual o ausencia de metadatos digitales.
        3. 'Tipo de firma no identificable': Si no puedes determinar la categoría.

    REGLAS GENERALES:
    1. FUENTE ÚNICA: Usa el PDF proporcionado y el texto de apoyo debajo.
    2. NO INVENTAR: Si un dato no existe, responde 'No identificado en el documento'.
    3. TRANSCRIPCIÓN LITERAL: Sé fiel al texto original para objetivos, alcances y políticas.

    --- TEXTO DE APOYO (OCR INICIAL) ---
    {full_text_context}
    --- FIN DATOS ---

    ESTRUCTURA JSON OBLIGATORIA:
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
            "nombre": "Nombre exacto del PDF", 
            "puesto": "Puesto exacto del PDF", 
            "firma": "Firma Electrónica / Firma Manual Escrita / Tipo de firma no identificable", 
            "fecha": "Timestamp completo del PDF" 
        }}
      ],
      "objetivo_completo": "...",
      "alcance_completo": "...",
      "interpretacion_diagrama_flujo": "Interpretación íntegra describiendo pasos y roles.",
      "politicas": {{
        "texto_completo": "Transcripción literal de las políticas.",
        "identificacion_participantes_ia": ["Lista de roles"],
        "resumen_politica_ia": "Resumen fiel"
      }},
      "procedimientos": {{
        "texto_completo": "Transcripción íntegra.",
        "lista_responsables": ["Lista de responsables"]
      }}
    }}
    """
    prompt_items.append(main_prompt)

    try:
        response = model.generate_content(prompt_items)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        return clean_response
    except Exception as e:
        return f"Error en extracción detallada: {str(e)}"


