from analyzers import image_analyzer
import google.generativeai as genai
from utils.ai_retry import call_with_retry
import os

def extract_detailed_analysis(pages_data, file_path=None):
    """
    Generates the Detailed Analysis report.
    Uses consolidated truth (Text + AI Interpreted Images).
    Follows Official Prompt V1.02 - Ajuste Clasificación Tipo de Firma.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return None, {}

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
    
    CRÍTICO - REGLAS DE EXTRACCIÓN AVANZADA DE CARÁTULA (PÁGINA 1):
    Para los campos de 'contenido_principal' (Tipo, Revisión, Fecha, Título, Elaborador), aplica estas reglas infalibles en la Hoja 1:

    1. ANCLAJE ESPACIAL (Spatial Mapping): Trata la Página 1 como un plano cartesiano. Si detectas una etiqueta clave (ej. "Revisión") en una coordenada, busca su valor numérico o texto en el radio de proximidad inmediata (derecha o abajo). Esto funciona aunque no existan "líneas" de tabla visibles.
    2. NORMALIZACIÓN DE ETIQUETAS (Synonym Mapping):
       - TIPO/NO. DOCTO: Busca "Tipo / No. de documento", "Código", "Cve", "Identificador".
       - REVISIÓN: Busca "Número de Revisión", "Rev", "Versión", "Edición", "Control".
       - FECHA: Busca "Fecha de efectividad", "Emisión", "Vigencia", "Fecha". Formato esperado: (dd-mm-yyyy).
       - TÍTULO: Busca "Título del documento", "Nombre del proceso".
       - ELABORADO POR: Busca "Elaborado por", "Autor", "Preparado por".
    3. AUDITORÍA DE ZONA DE PODER (Header): Los primeros 250 píxeles verticales de la Página 1 se declaran "Zona de Datos Maestros". Tienes prohibido leer texto fluido aquí; debes buscar únicamente pares Etiqueta -> Valor.
    4. VALIDACIÓN CRUZADA (OCR vs. Texto Directo): Si el flujo de texto devuelve una cadena incoherente (etiquetas mezcladas por el logo), ignora el orden del texto y reconstruye la tabla basándote en la posición física de las palabras en la hoja.
    5. REDUNDANCIA VISUAL: Si los datos maestros están en una imagen compuesta con el LOGO (ej. Enerser), no te confundas. Separa el elemento gráfico del dato alfanumérico. Los datos están ahí, búscalos con rigor forense.

    CRÍTICO - SOBERANÍA DE DATOS:
    1. Si en la 'GUÍA DE DATOS PREVIOS' ya existe un [HALLAZGO VISUAL PREVIO] que describa un DIAGRAMA DE FLUJO, UTILÍZALO para el campo 'interpretacion_diagrama_flujo'. No intentes re-interpretarlo, sintetiza lo que ya se detectó.
    2. Lo mismo aplica para Firmas, Sellos y Tablas. Confía 100% en las interpretaciones previas proporcionadas.

    INSTRUCCIONES DE ESTRUCTURA:
    - REVISADO Y APROBADO: Busca activamente tablas con encabezados como "Nombe", "Puesto", "Firma", "Fecha" o "REVISADO Y APROBADO ELECTRÓNICAMENTE".
    - IMPORTANTE CLASIFICACIÓN DE FIRMA: Mira el contenido visual de la celda 'Firma':
      - Si es TEXTO legible (ej. nombre repetido, hash, texto de certificado): Escribe "Firmado Electrónicamente por: " seguido del texto extraído.
      - Si es un Garabato/Rúbrica/Imagen hecha a mano: Escribe "Firmado Manualmente: firma autógrafa (imagen)".
    - IMPORTANTE: En la columna 'Fecha', captura el timestamp completo (fecha y hora si existe).
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
      "mermaid_graph": "graph TD;\nStart((Inicio)) --> B[Paso 1: ...];\n... (Sintaxis completa y válida de MermaidJS que represente el flujo operativo)",
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

    prompt_parts = [main_prompt]
    
    # MULTIMODAL SOURCE: 
    # If file_path is provided, we upload it to Gemini to allow visual inspection
    # of Page 1 Master Data (Rule 5: Redundancy).
    if file_path and os.path.exists(file_path):
        try:
            # Upload file to Gemini API (File API)
            doc_file = genai.upload_file(path=file_path, display_name="Documento Auditoría")
            prompt_parts.append(doc_file)
            
            # Additional instruction for multimodality
            vision_instruction = """
            ADJUNTO: Tienes el archivo original disponible. 
            PARA LA HOJA 1: Ignora el ruido del OCR si es necesario. Observa la IMAGEN DE LA PRIMERA PÁGINA para extraer con precisión los Datos Generales (Tipo, Revisión, Fecha, Título, Elaborador).
            Busca la tabla de carátula, incluso si está pegada al logo de la empresa.
            """
            prompt_parts.append(vision_instruction)
        except Exception as vision_err:
            print(f"Vision analysis unavailable (upload failed): {vision_err}")

    try:
        response = call_with_retry(model.generate_content, prompt_parts)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        
        # Capture usage metadata
        usage = getattr(response, 'usage_metadata', None)
        usage_data = {}
        if usage:
            usage_data = {
                "prompt_token_count": usage.prompt_token_count,
                "candidates_token_count": usage.candidates_token_count,
                "total_token_count": usage.total_token_count
            }
        
        return clean_response, usage_data
    except Exception as e:
        return f"Error en síntesis detallada: {str(e)}", {}
