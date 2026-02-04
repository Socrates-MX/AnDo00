import os
import json
from dotenv import load_dotenv
from utils.supabase_client import SupabaseLightClient

# Load environment variables
load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    exit(1)

client = SupabaseLightClient(URL, KEY)

print("--- VERIFICACIÓN DE PERSISTENCIA SUPABASE ---\n")

# 1. Verificar Documentos
print(">>> Tabla: ando_documents (Últimos 5)")
res_docs = client.table("ando_documents").select("*").order("created_at", desc=True).limit(5).execute()
if res_docs.data:
    for doc in res_docs.data:
        print(f"ID: {doc.get('id')}")
        print(f"File: {doc.get('file_name')}")
        print(f"Version Actual: {doc.get('current_version')}")
        print(f"Creado: {doc.get('created_at')}")
        print("-" * 30)
else:
    print("No se encontraron documentos o error de conexión.")
    if hasattr(res_docs, 'error'): print(f"Error: {res_docs.error}")

print("\n" + "="*50 + "\n")

# 2. Verificar Versiones de Análisis
print(">>> Tabla: ando_analysis_versions (Últimas 5)")
res_vers = client.table("ando_analysis_versions").select("*").order("created_at", desc=True).limit(5).execute()
if res_vers.data:
    for ver in res_vers.data:
        print(f"ID Versión: {ver.get('id')}")
        print(f"Doc ID: {ver.get('document_id')}")
        print(f"Número de Versión: {ver.get('version_number')}")
        
        payload = ver.get('full_analysis_payload', {})
        # Verificar integridad básica del payload
        has_content = "contenido_principal" in payload
        has_signatures = "revisado_aprobado" in payload
        
        print(f"Payload Integrity: {'✅ OK' if has_content and has_signatures else '❌ Incompleto'}")
        print(f"Keys en Payload: {list(payload.keys())}")
        print(f"Creado: {ver.get('created_at')}")
        print("-" * 30)
else:
    print("No se encontraron versiones.")
    if hasattr(res_vers, 'error'): print(f"Error: {res_vers.error}")
