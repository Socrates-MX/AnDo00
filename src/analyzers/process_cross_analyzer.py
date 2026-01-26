import os
import json
import google.generativeai as genai
from utils.ai_retry import call_with_retry
from dotenv import load_dotenv

load_dotenv()

def analyze_process_crossing(detailed_report, pages_data):
    """
    Performs a cross-check between Flowchart and Procedures.
    Evaluates: Activities, Roles, Areas, Decisions, and Timings.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare input summary
    data_summary = f"""
    1. OBJETIVO: {detailed_report.get('objetivo_completo')}
    2. DIAGRAMA DE FLUJO (INTERPRETACIÓN): {detailed_report.get('interpretacion_diagrama_flujo')}
    3. PROCEDIMIENTOS (TEXTO COMPLETO): {detailed_report.get('procedimientos', {}).get('texto_completo')}
    4. ROLES/RESPONSABLES: {detailed_report.get('procedimientos', {}).get('lista_responsables')}
    """

    prompt = f"""
    ERES ANTIGRAVITY - AUDITOR TÉCNICO DE PROCESOS.
    
    TAREA: Ejecutar la prueba 'Cruce — Diagrama de Flujo vs. Procedimientos'.
    REGLA: Solo usa la información proporcionada. No inventes pasos.

    --- DATOS DE AUDITORÍA ---
    {data_summary}
    --- FIN DATOS ---

    MODO DE ANÁLISIS:
    1. Cruza cada paso del Diagrama con los Procedimientos escritos.
    2. Valida si los Puestos y Áreas son los mismos en ambos.
    3. Verifica si los puntos de decisión en el diagrama tienen reglas en el procedimiento.
    4. Cruza los 'Cuándo' (Tiempos).

    ESTRUCTURA JSON DE SALIDA OBLIGATORIA:
    {{
      "matriz": [
        {{ "elemento": "Actividades Diagrama vs Procedimientos", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "elemento": "Participantes (puestos)", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "elemento": "Áreas participantes", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "elemento": "Toma de decisiones", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "elemento": "Tiempos (cuándo)", "resultado": "✅/⚠️/❌", "evidencia": "..." }}
      ],
      "conclusion_operativa": {{
        "estado": "Operativamente congruente / Parcialmente congruente / No congruente",
        "hallazgos": ["hallazgo 1", "hallazgo 2"],
        "riesgos": ["riesgo 1", "riesgo 2"],
        "impacto": "Impacto potencial en operación o control interno."
      }}
    }}
    """

    try:
        response = call_with_retry(model.generate_content, prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error in Process Cross Analysis: {e}")
        return None
