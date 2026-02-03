
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
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    generation_config = {"response_mime_type": "application/json"}
    model = genai.GenerativeModel('gemini-2.0-flash', generation_config=generation_config)
    
    # Construir el contexto RAW puro
    raw_text_context = ""
    pages = raw_consolidation_json.get("documento", {}).get("analisis_raw", [])
    
    for p in pages:
        raw_text_context += f"\n--- PÁGINA {p.get('pagina')} ---\n"
        raw_content = p.get('contenido_raw_pdf', '')
        # Escape curly braces to prevent f-string errors
        raw_content = raw_content.replace('{', '{{').replace('}', '}}')
        raw_text_context += raw_content + "\n"
        
        # Inyectar interpretaciones de imágenes
        imgs = p.get('contenido_raw_imagenes', [])
        if imgs:
            raw_text_context += "--- ELEMENTOS VISUALES (RAW) ---\n"
            for img in imgs:
                raw_text_context += f"[Imagen {img.get('imagen_id')}: {img.get('tipo')} -> {img.get('texto_interpretado')}]\n"

    # Prompt estricto sobre fuente RAW
    prompt = f"""
    ERES ANTIGRAVITY - AUDITOR FORENSE DE DATOS CRUDOS (RAW).

    TU MISIÓN: Generar la tabla "RAW - Desviaciones Normativas Detectadas".
    FUENTE DE VERDAD: ÚNICAMENTE el texto crudo proporcionado abajo. No uses conocimiento externo.

    INSTRUCCIONES:
    1. Lee el texto corrido y las descripciones de imágenes.
    2. Identifica mentalmente: Título, Objetivo, Alcance, Diagramas de Flujo (descritos en texto visual) y Firmantes.
    3. Cruza la información para detectar discrepancias lógicas.

    --- INICIO CONTENIDO RAW ---
    {raw_text_context[:25000]} 
    --- FIN CONTENIDO RAW ---
    (Nota: El texto puede estar truncado por límites, prioriza lo visible)

    GENERAR JSON DE SALIDA (Matriz de Congruencia RAW + Desviaciones):
    {{
      "raw_matriz": [
        {{ "relacion": "Título vs Objetivo", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Objetivo vs Alcance", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Alcance vs Diagrama", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Diagrama vs Políticas", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Políticas vs Procedimientos", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Diagrama vs Participantes", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Participantes vs Firmantes", "resultado": "✅/⚠️/❌", "evidencia": "..." }}
      ],
      "raw_desviaciones": [
        {{ 
           "requisito": "Alcance vs Diagrama", 
           "hallazgo": "Descripción detallada...", 
           "estado": "Cumple / No Cumple / Parcial" 
        }}
      ],
      "raw_matriz_02": [
        {{ "relacion": "1. Título vs Contenido", "resultado": "✅/⚠️/❌", "evidencia": "¿El Título es congruente con el contenido del documento?" }},
        {{ "relacion": "2. Objetivo vs Información", "resultado": "✅/⚠️/❌", "evidencia": "¿El Objetivo es congruente con la información contenida?" }},
        {{ "relacion": "3. Análisis de Alcance", "resultado": "✅/⚠️/❌", "evidencia": "¿Menciona empresa/unidad/segmento específico o es para toda la organización? ¿Es congruente?" }},
        {{ "relacion": "4. Existencia D-P-P", "resultado": "✅/⚠️/❌", "evidencia": "¿El documento contiene Diagrama, Políticas y Procedimientos?" }},
        {{ "relacion": "5. Congruencia D-P-P", "resultado": "✅/⚠️/❌", "evidencia": "¿El Diagrama, Políticas y Procedimientos son congruentes entre sí?" }},
        {{ "relacion": "6. Lista de Participantes", "resultado": "ℹ️", "evidencia": "Genera lista de Puestos y Responsabilidades hallados a lo largo del documento." }},
        {{ "relacion": "7. Congruencia Participantes", "resultado": "✅/⚠️/❌", "evidencia": "¿Los participantes son congruentes para este documento?" }},
        {{ "relacion": "8. Congruencia Responsabilidades", "resultado": "✅/⚠️/❌", "evidencia": "¿Las responsabilidades establecidas son congruentes?" }},
        {{ "relacion": "9. Participantes vs Firmantes", "resultado": "✅/⚠️/❌", "evidencia": "¿Los participantes identificados son los que firman?" }}
      ],
      "raw_cruce_operativo": [
        {{
           "paso_diagrama": "Descripción del paso visual identificado en el diagrama RAW",
           "procedimiento_escrito": "Texto correspondiente encontrado en la narrativa",
           "coincidencia": "Total / Parcial / No Encontrado",
           "comentario": "Explicación breve de la alineación."
        }}
      ],
      "raw_diagrama_flujo": [
        {{
           "paso": "Ej. 1",
           "descripcion": "Acción realizada en este paso",
           "responsable": "Rol encargado",
           "es_decision": "Sí/No (¿Es un rombo?)"
        }}
      ],
      "raw_mermaid_code": "graph TD\\nA[Inicio] --> B{Decisión}\\nB -- Sí --> C[Acción]\\n...",
      "raw_inconsistencias_operativas": [
        {{
           "etapa_actividad": "Ej. 'Fase de Evaluación' o 'Paso 3'",
           "inconsistencia": "Detectar si el diagrama muestra pasos/decisiones que el texto NO menciona, o viceversa. O si los responsables difieren en la operación.",
           "severidad": "Alta (Ruptura de flujo) / Media (Ambigüedad) / Baja (Detalle menor)"
        }}
      ]
    }}
    """


    try:
        response = call_with_retry(model.generate_content, prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Error en RAW Congruence: {e}")
        return {"raw_desviaciones": []}
