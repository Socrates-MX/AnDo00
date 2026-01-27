import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def check():
    client = get_supabase_client()
    if not client: return

    for table in ["documents", "analysis_detallado", "revisiones_documento"]:
        print(f"\n--- {table.upper()} ---")
        res = client.table(table).select("*").execute()
        if res.error:
            print(f"Error: {res.error}")
        elif not res.data:
            print("Vacio")
        else:
            for item in res.data:
                print(item)

if __name__ == "__main__":
    check()
