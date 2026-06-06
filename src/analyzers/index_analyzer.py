import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_index_and_congruence(pages_data):
    """
    Analyzes the full document text to build a Smart Index and 
    evaluate the semantic congruence between titles and content.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)

    # Prepare context for the AI
    full_context = ""
    for p in pages_data:
        full_context += f"--- PÁGINA {p['page_number']} ---\\n{p['text_content']}\\n\\n"

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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        clean_response = response.choices[0].message.content
        parsed = json.loads(clean_response)
        
        # Capture usage metadata
        usage = response.usage
        if usage:
            parsed["usage"] = {
                "prompt_token_count": usage.prompt_tokens,
                "candidates_token_count": usage.completion_tokens,
                "total_token_count": usage.total_tokens
            }
            
        return parsed
    except Exception as e:
        print(f"Error in Index Analysis: {e}")
        return {"usage": {"total_token_count": 0}}
