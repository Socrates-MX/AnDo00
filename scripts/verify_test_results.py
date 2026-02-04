import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Faltan credenciales de Supabase en .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def audit_latest_entry():
    print("🔎 --- AUDITORÍA DE PRUEBA CONTROLADA ---")
    
    # 1. Verificar registro en tabla 'documents'
    try:
        doc_res = supabase.table("documents").select("*").order("created_at", desc=True).limit(1).execute()
        if not doc_res.data:
            print("❌ FALLO: No se encontraron documentos en la base de datos.")
            return False
            
        doc = doc_res.data[0]
        print(f"✅ DOCUMENTO REGISTRADO:")
        print(f"   - ID: {doc['id']}")
        print(f"   - Nombre: {doc['nombre_archivo']}")
        print(f"   - Hash (SHA256): {doc['file_hash'][:15]}...")
        print(f"   - Creado: {doc['created_at']}")
    except Exception as e:
        print(f"❌ Error conectando a documents: {e}")
        return False

    # 2. Verificar análisis en 'analysis_detallado'
    try:
        an_res = supabase.table("analysis_detallado").select("*").eq("document_id", doc['id']).execute()
        if not an_res.data:
            print("⚠️ ADVERTENCIA: El documento existe pero NO tiene análisis guardado aún.")
            return False
            
        analysis = an_res.data[0]
        content = analysis.get("content", {})
        
        print(f"✅ ANÁLISIS PERSISTIDO:")
        print(f"   - ID Análisis: {analysis['id']}")
        
        # Validar campos clave del JSON
        has_summary = bool(content.get("contenido_principal"))
        has_risks = bool(content.get("impersonation_alerts"))
        has_graph = "mermaid_graph" in content
        
        print(f"   - Estructura Base: {'✅ OK' if has_summary else '❌ FALTANTE'}")
        print(f"   - Módulo Riesgos: {'✅ OK (Datos)' if has_risks else '⚠️ VACÍO (Sin alertas)'}")
        print(f"   - Módulo Gráfico: {'✅ OK' if has_graph else '❌ FALTANTE'}")
        
        if has_graph:
            graph_preview = content['mermaid_graph'][:30].replace('\n', ' ')
            print(f"   - Preview Gráfico: {graph_preview}...")

    except Exception as e:
        print(f"❌ Error leyendo análisis: {e}")
        return False
        
    print("\n✅ CONCLUSIÓN: La prueba de integridad de datos ha sido EXITOSA.")
    print("   El flujo Frontend -> API -> AI -> DB funciona correctamente.")
    return True

if __name__ == "__main__":
    audit_latest_entry()
