
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def check_ando():
    client = get_supabase_client()
    if not client: return

    print("--- ANDO DOCUMENTS ---")
    res = client.table("ando_documents").select("*").order("created_at", desc=True).limit(5).execute()
    print(res.data)

if __name__ == "__main__":
    check_ando()
