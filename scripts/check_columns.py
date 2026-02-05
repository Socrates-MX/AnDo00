import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("documents").select("*").limit(1).execute()
if res.data:
    print("Columns in 'documents':", res.data[0].keys())
else:
    print("No data in 'documents'")
