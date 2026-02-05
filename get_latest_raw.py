
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def get_latest_raw():
    client = get_supabase_client()
    if not client: 
        print("No supabase client")
        return

    # Get latest analysis with raw data
    res = client.table("analysis_detallado").select("ConsolidacionRAW_completo").order("fecha_analisis", desc=True).limit(1).execute()
    
    if res.data and len(res.data) > 0:
        raw_data = res.data[0].get("ConsolidacionRAW_completo")
        if raw_data:
            print(json.dumps(raw_data, indent=2))
        else:
            print("No raw data found in latest analysis record")
    else:
        print("No analysis found")

if __name__ == "__main__":
    get_latest_raw()
