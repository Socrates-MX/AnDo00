import os
from typing import Optional
from dotenv import load_dotenv
try:
    from supabase import create_client, Client
except ImportError:
    Client = None

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase Client Initialized ({'Service Role' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'Anon Key'})")
    except Exception as e:
        print(f"❌ Failed to init Supabase: {e}")
else:
    print("⚠️ Supabase credentials not found.")
