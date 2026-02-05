
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def get_raw_titles(doc_id):
    client = get_supabase_client()
    if not client: return

    res = client.table("analysis_detallado").select("*").eq("document_id", doc_id).execute()
    
    if res.data and len(res.data) > 0:
        row = res.data[0]
        raw_json = row.get("ConsolidacionRAW_completo")
        if not raw_json:
            # Maybe it's inside payload_completo?
            payload = row.get("payload_completo", {})
            raw_json = payload.get("raw_congruence_report", {}) # This is the report, not the source
        
        if raw_json:
            # Extract content_raw_pdf titles or just scan for titles
            titles = []
            pages = raw_json.get("documento", {}).get("analisis_raw", [])
            for p in pages:
                # Based on the code, it uses 'contenido_raw_pdf'
                content = p.get("contenido_raw_pdf", "")
                # Simple extraction: first lines or lines that look like titles
                lines = content.split('\n')
                if lines:
                    titles.append(f"Pág {p.get('pagina')}: {lines[0].strip()}")
            
            if not titles:
                print("No titles found in RAW data. Dumping keys for debug.")
                print(raw_json.keys())
            else:
                for t in titles:
                    print(t)
        else:
            print("No ConsolidacionRAW_completo field found in record.")

if __name__ == "__main__":
    get_raw_titles("3ab01f9a-056c-494c-895a-82c4261456f2")
