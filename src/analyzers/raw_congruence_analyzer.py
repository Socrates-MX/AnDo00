
import os
import json
import google.generativeai as genai
from utils.ai_retry import call_with_retry
from dotenv import load_dotenv

load_dotenv()

def analyze_raw_congruence(raw_consolidation_json):
    """
    Realiza un análisis de congruencia basándose EXCLUSIVAMENTE en el contenido RAW
    (Texto plano + Interpretaciones de Imágenes), sin estructuras intermedias.
    """
    print("--- STARTING RAW CONGRUENCE ANALYSIS ---", flush=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY missing in environment")
        return {
            "raw_matriz": [],
            "raw_desviaciones": [],
            "raw_matriz_02": [],
            "raw_cruce_operativo": [],
            "raw_diagrama_flujo": [],
            "raw_inconsistencias_operativas": [],
            "error": "Missing API Key"
        }
    
    print("✅ API Key found. Configuring Gemini...")
    genai.configure(api_key=api_key)
    generation_config = {"response_mime_type": "application/json"}
    model = genai.GenerativeModel('gemini-2.0-flash', generation_config=generation_config)
    
    # Construir el contexto RAW puro estructurado
    # Usamos directamente la estructura "Consolidación de Contenido (RAW)" como fuente
    raw_source_data = json.dumps(raw_consolidation_json, ensure_ascii=False, indent=2)

    prompt = f"""
    ERES ANTIGRAVITY - AUDITOR FORENSE DE DATOS CRUDOS (RAW).

    TU MISIÓN: Generar el "RAW02 - Análisis de Coherencia Normativa" (9 Puntos de Control).
    
    FUENTE DE VERDAD (INPUT): 
    Analizarás EXCLUSIVAMENTE el siguiente objeto JSON que contiene la "Consolidación de Contenido (RAW)". 
    
    --- INICIO FUENTE RAW (JSON) ---
    {raw_source_data}
    --- FIN FUENTE RAW ---

    INSTRUCCIONES:
    1. Reconstruye el documento y valida los 9 puntos de control listados abajo.
    2. Cruza información entre texto y descripciones de imágenes.
    3. Si algo no existe, márcalo como ❌ y explica por qué.

    RESPONDE ÚNICAMENTE CON ESTE FORMATO JSON:
    {{
      "raw_matriz_02": [
        {{ "relacion": "1. Título vs Contenido", "resultado": "✅/⚠️/❌", "evidencia": "Análisis de si el título refleja el contenido real." }},
        {{ "relacion": "2. Objetivo vs Información", "resultado": "✅/⚠️/❌", "evidencia": "Análisis de congruencia del objetivo." }},
        {{ "relacion": "3. Análisis de Alcance", "resultado": "✅/⚠️/❌", "evidencia": "Menciona empresa/unidad/segmento específico." }},
        {{ "relacion": "4. Existencia D-P-P", "resultado": "✅/⚠️/❌", "evidencia": "¿Contiene Diagrama, Políticas y Procedimientos?" }},
        {{ "relacion": "5. Congruencia D-P-P", "resultado": "✅/⚠️/❌", "evidencia": "Alineación entre los 3 elementos." }},
        {{ "relacion": "6. Lista de Participantes", "resultado": "ℹ️", "evidencia": "Lista de puestos hallados." }},
        {{ "relacion": "7. Congruencia Participantes", "resultado": "✅/⚠️/❌", "evidencia": "¿Son lógicos para este proceso?" }},
        {{ "relacion": "8. Congruencia Responsabilidades", "resultado": "✅/⚠️/❌", "evidencia": "Análisis de las tareas asignadas." }},
        {{ "relacion": "9. Participantes vs Firmantes", "resultado": "✅/⚠️/❌", "evidencia": "¿Los que operan son los que firman?" }}
      ],
      "raw_desviaciones": [
        {{ "requisito": "Nombre del Requisito", "hallazgo": "Descripción", "estado": "Cumple/No Cumple/Parcial" }}
      ],
      "raw_cruce_operativo": [
        {{ "paso_diagrama": "...", "procedimiento_escrito": "...", "coincidencia": "Total/Parcial/No", "comentario": "..." }}
      ],
      "raw_diagrama_flujo": [
        {{ "paso": "1", "descripcion": "...", "responsable": "...", "es_decision": "No" }}
      ],
      "raw_mermaid_code": "graph TD; ...",
      "raw_inconsistencias_operativas": [
        {{ "etapa_actividad": "...", "inconsistencia": "...", "severidad": "Baja/Media/Alta" }}
      ]
    }}
    """

    try:
        response = call_with_retry(model.generate_content, prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)
        
        # Estructura por defecto para asegurar compatibilidad con Frontend
        defaults = {
            "raw_matriz": [],
            "raw_desviaciones": [],
            "raw_matriz_02": [],
            "raw_cruce_operativo": [],
            "raw_diagrama_flujo": [],
            "raw_inconsistencias_operativas": []
        }
        
        # Capture usage metadata
        usage = getattr(response, 'usage_metadata', None)
        if usage:
            parsed["usage"] = {
                "prompt_token_count": usage.prompt_token_count,
                "candidates_token_count": usage.candidates_token_count,
                "total_token_count": usage.total_token_count
            }

        if not isinstance(parsed, dict):
            print(f"⚠️ IA Response is not a dict ({type(parsed)}). Returning defaults.", flush=True)
            return defaults
            
        # Asegurar que todas las llaves existan
        for key, default_val in defaults.items():
            if key not in parsed or parsed[key] is None:
                parsed[key] = default_val
                
        return parsed
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error CRÍTICO en RAW Congruence: {e}")
        # Retornar estructura vacía segura para evitar pantalla blanca
        return {
            "raw_matriz": [],
            "raw_desviaciones": [],
            "raw_matriz_02": [],
            "raw_cruce_operativo": [],
            "raw_diagrama_flujo": [],
            "raw_inconsistencias_operativas": [],
            "usage": {"total_token_count": 0}
        }
