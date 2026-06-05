import os, sys
from supabase import create_client, Client

url = "https://kdjpwknxthfypcmrfzwl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtkanB3a254dGhmeXBjbXJmendsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTg5NDc5NCwiZXhwIjoyMDg1NDcwNzk0fQ.atTOFunPEG--8rkY39cKyNYXtTF6gYTISmKLuguoYbM"
supabase: Client = create_client(url, key)

res = supabase.table("organizations").select("*").eq("id", "7a6eb435-3cdb-4e05-a463-736c2fada006").execute()
print("organizations:", res.data)

res = supabase.table("profiles").select("*").eq("id", "e1822f9a-290f-4a6a-b34c-a77931436db2").execute()
print("profiles:", res.data)
