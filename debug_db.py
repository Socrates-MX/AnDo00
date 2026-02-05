
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def debug_db():
    client = get_supabase_client()
    if not client: 
        print("No supabase client")
        return

    print("--- DOCUMENTS ---")
    res_docs = client.table("documents").select("id, nombre_archivo").execute()
    print(res_docs.data)

    print("\n--- ANALYSIS DETALLADO ---")
    res_analysis = client.table("analysis_detallado").select("id, document_id, version").execute()
    print(res_analysis.data)

if __name__ == "__main__":
    debug_db()
