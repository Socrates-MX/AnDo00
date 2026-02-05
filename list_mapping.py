
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def list_mapping():
    client = get_supabase_client()
    if not client: return

    res = client.table("documents").select("id, nombre_archivo").execute()
    print("DOCS:", res.data)
    
    res2 = client.table("analysis_detallado").select("id, document_id").execute()
    print("ANALYSIS:", res2.data)

if __name__ == "__main__":
    list_mapping()
