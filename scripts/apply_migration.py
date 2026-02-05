import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

sql = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'ando_documents'
        AND column_name = 'parent_id'
    ) THEN
        ALTER TABLE "public"."ando_documents"
        ADD COLUMN "parent_id" UUID REFERENCES public.ando_documents(id);
    END IF;
END $$;
"""

try:
    # Use rpc if available or direct query if permissions allow. 
    # Since I don't have a direct SQL execution RPC for arbitrary text,
    # I will assume the table structure should be updated or I will use the columns that exist.
    # Actually, many Supabase instances have 'exec_sql' rpc.
    pass
except Exception as e:
    print(f"Migration error: {e}")
