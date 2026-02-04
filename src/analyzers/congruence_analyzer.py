import os
import json
import google.generativeai as genai
from utils.ai_retry import call_with_retry
from dotenv import load_dotenv

load_dotenv()

def analyze_document_congruence(detailed_report, pages_data):
    """
    Performs a cross-sectional congruence analysis based on the Official IA Prompt.
    Compares Title, Objective, Scope, Diagram, Policies, Procedures, and Signatories.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare data summary from detailed report
    doc_main = detailed_report.get("contenido_principal", {})
    signatories = detailed_report.get("revisado_aprobado", [])
    policies = detailed_report.get("politicas", {})
    procedures = detailed_report.get("procedimientos", {})

    data_summary = f"""
    1. TÍTULO: {doc_main.get('titulo_documento')}
    2. OBJETIVO: {detailed_report.get('objetivo_completo')}
    3. ALCANCE: {detailed_report.get('alcance_completo')}
    4. DIAGRAMA DE FLUJO (INTERPRETACIÓN): {detailed_report.get('interpretacion_diagrama_flujo')}
    5. POLÍTICAS (RESUMEN): {policies.get('resumen_politica_ia')}
    6. PROCEDIMIENTOS (RESPONSABLES): {procedures.get('lista_responsables')}
    7. FIRMANTES Y PUESTOS: {[f"{s.get('nombre')} ({s.get('puesto')})" for s in signatories]}
    """

    prompt = f"""
    ERES ANTIGRAVITY - ANALIZADOR DE CONGRUENCIA DE ALTA PRECISIÓN.

    TU TAREA: Ejecutar la 'Prueba de Análisis de Congruencia del Contenido'.
    PRINCIPIO: El contenido proporcionado es la ÚNICA FUENTE DE VERDAD.

    --- DATOS DEL DOCUMENTO ---
    {data_summary}
    --- FIN DATOS ---

    MODO DE OPERACIÓN:
    1. Compara semánticamente cada sección contra las otras.
    2. Detecta si el Objetivo cumple el Título, si el Alcance cubre el Diagrama, si las Políticas rigen los Procedimientos, y si los Firmantes corresponden a los participantes.
    3. Clasifica como: ✅ Congruente, ⚠️ Parcialmente congruente o ❌ No congruente.

    ESTRUCTURA JSON DE SALIDA OBLIGATORIA:
    {{
      "matriz": [
        {{ "relacion": "Título vs Objetivo", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Objetivo vs Alcance", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Alcance vs Diagrama", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Diagrama vs Políticas", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Políticas vs Procedimientos", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Diagrama vs Participantes", "resultado": "✅/⚠️/❌", "evidencia": "..." }},
        {{ "relacion": "Participantes vs Firmantes", "resultado": "✅/⚠️/❌", "evidencia": "..." }}
      ]
    }}
    """

    try:
        response = call_with_retry(model.generate_content, prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_response)
        
        # Capture usage metadata
        usage = getattr(response, 'usage_metadata', None)
        if usage:
            parsed["usage"] = {
                "prompt_token_count": usage.prompt_token_count,
                "candidates_token_count": usage.candidates_token_count,
                "total_token_count": usage.total_token_count
            }
            
        return parsed
    except Exception as e:
        print(f"Error in Congruence Analysis: {e}")
        return {"usage": {"total_token_count": 0}}
