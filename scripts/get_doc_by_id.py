
import os
import sys
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno (URL y KEY de Supabase)
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Faltan credenciales SUPABASE_URL o SUPABASE_KEY en .env")
    sys.exit(1)

supabase: Client = create_client(url, key)

def get_document(doc_id):
    print(f"🔍 Buscando documento ID: {doc_id} ...")
    
    # 1. Consultar Metadatos (Tabla 'documents')
    res_meta = supabase.table("documents").select("*").eq("id", doc_id).execute()
    
    if not res_meta.data:
        print("❌ Documento no encontrado en tabla 'documents'.")
        return

    print("\n--- 📄 METADATOS PRINCIPALES (Tabla 'documents') ---")
    print(json.dumps(res_meta.data[0], indent=2, ensure_ascii=False))

    # 2. Consultar Payload Completo (Tabla 'analysis_results')
    # Nota: Ajusta 'analysis_results' o 'analysis_detallado' según tu esquema real.
    # En el código vimos 'analysis_results' primero y luego un intento a 'analysis_detallado'.
    # Probaremos ambas por si acaso.
    
    table_name = "analysis_results"
    res_payload = supabase.table(table_name).select("*").eq("document_id", doc_id).execute()
    
    if not res_payload.data:
        table_name = "analysis_detallado"
        res_payload = supabase.table(table_name).select("*").eq("document_id", doc_id).execute()

    if res_payload.data:
        print(f"\n--- 📦 PAYLOAD COMPLETO (Tabla '{table_name}') ---")
        record = res_payload.data[0]
        # Mostrar solo claves de primer nivel para no inundar la pantalla
        payload = record.get("payload_completo", {})
        print("Claves disponibles en el JSON Blob:")
        print(list(payload.keys()))
        
        # Opcional: Mostrar alertas de seguridad específicas si existen
        if "impersonation_alerts" in payload:
            print("\n🚨 Alertas de Suplantación guardadas:")
            print(json.dumps(payload["impersonation_alerts"], indent=2, ensure_ascii=False))
            
    else:
        print("\n❌ No se encontró el payload detallado en ninguna tabla de análisis.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/get_doc_by_id.py <UUID>")
        sys.exit(1)
    
    doc_uuid = sys.argv[1]
    get_document(doc_uuid)
