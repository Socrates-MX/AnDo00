
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def inspect_record(doc_id):
    client = get_supabase_client()
    if not client: return

    res = client.table("analysis_detallado").select("*").eq("document_id", doc_id).execute()
    
    if res.data and len(res.data) > 0:
        row = res.data[0]
        print("KEYS:", row.keys())
        payload = row.get("payload_completo", {})
        print("PAYLOAD KEYS:", payload.keys())
        if "detailed_report" in payload:
            print("TITLE FROM DETAILED:", payload["detailed_report"].get("contenido_principal", {}).get("titulo_documento"))

if __name__ == "__main__":
    inspect_record("3ab01f9a-056c-494c-895a-82c4261456f2")
