import os
import json
import google.generativeai as genai
from utils.ai_retry import call_with_retry
from dotenv import load_dotenv

load_dotenv()

def extract_index_and_congruence(pages_data):
    """
    Analyzes the full document text to build a Smart Index and 
    evaluate the semantic congruence between titles and content.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare context for the AI
    full_context = ""
    for p in pages_data:
        full_context += f"--- PÁGINA {p['page_number']} ---\n{p['text_content']}\n\n"

    prompt = f"""
    Eres un auditor experto en análisis documental. Tu tarea es generar un ÍNDICE INTELIGENTE del documento y evaluar su CONGRUENCIA.

    TAREAS:
    1. Identifica las secciones principales, apartados o títulos del documento.
    2. Asocia cada sección con su número de página.
    3. Evalúa la 'Congruencia Semántica': ¿El título del apartado refleja realmente lo que se discute en el texto de esas páginas? 
    4. Asigna un Score de Congruencia de 0 a 100 y una breve observación.

    --- CONTENIDO DEL DOCUMENTO ---
    {full_context}
    --- FIN DEL CONTENIDO ---

    SALIDA OBLIGATORIA (JSON):
    {{
        "title": "Título detectado del documento",
        "sections": [
            {{ "title": "Nombre de la sección", "page": 1, "observation": "Breve nota si aplica" }}
        ],
        "congruence": {{
            "score": 85,
            "analysis": "Explicación breve de la consistencia entre el índice y el contenido real."
        }}
    }}
    """

    try:
        response = call_with_retry(model.generate_content, prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error in Index Analysis: {e}")
        return None
