
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def get_raw_for_doc(doc_id):
    client = get_supabase_client()
    if not client: return

    res = client.table("analysis_detallado").select("ConsolidacionRAW_completo").eq("document_id", doc_id).limit(1).execute()
    
    if res.data and len(res.data) > 0:
        raw_data = res.data[0].get("ConsolidacionRAW_completo")
        print(json.dumps(raw_data, ensure_ascii=False))

if __name__ == "__main__":
    get_raw_for_doc("3ab01f9a-056c-494c-895a-82c4261456f2")
