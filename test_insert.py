import os, sys
from dotenv import load_dotenv

load_dotenv()
os.environ["SUPABASE_URL"] = os.getenv("VITE_SUPABASE_URL")
os.environ["SUPABASE_KEY"] = os.getenv("VITE_SUPABASE_ANON_KEY")

sys.path.append(os.path.abspath('api'))
from core.supabase_client import supabase

doc_data = {
    "organization_id": "7a6eb435-3cdb-4e05-a463-736c2fade086",
    "file_name": "test.pdf",
    "file_hash": "testhash123",
    "page_count": 1,
    "status": "pending_ai"
}

try:
    print("Inserting...")
    res = supabase.table("ando_documents").insert(doc_data).execute()
    print("Result data:", res.data)
except Exception as e:
    print("Error:", e)
