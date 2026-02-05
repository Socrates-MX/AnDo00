
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def inspect_all():
    client = get_supabase_client()
    if not client: return

    res = client.table("analysis_detallado").select("*").execute()
    for i, row in enumerate(res.data):
        print(f"\n--- RECORD {i} ---")
        print("KEYS:", row.keys())
        payload = row.get("payload_completo", {})
        print("PAYLOAD KEYS:", payload.keys())
        # If pages exist, print page count and first page titles
        if "pages" in payload:
            print(f"PAGES FOUND: {len(payload['pages'])}")
            for p in payload['pages']:
                print(f"P{p.get('page_number')}: {p.get('text_content', '')[:100]}...")

if __name__ == "__main__":
    inspect_all()
