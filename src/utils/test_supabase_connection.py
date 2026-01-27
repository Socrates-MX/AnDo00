
import os
import sys
from dotenv import load_dotenv

# Añadir src al path para importar el cliente
sys.path.append(os.path.join(os.getcwd(), 'src'))
from utils.supabase_client import get_supabase_client

def test_connection():
    load_dotenv()
    client = get_supabase_client()
    if not client:
        print("[ERROR] No se pudo obtener el cliente Supabase. Verifica el archivo .env")
        return

    print(f"Probando conexión a: {client.url}")
    
    # Intentar listar documentos (tabla maestra)
    try:
        res = client.table("documents").select("id").limit(1).execute()
        if res.error:
            if "relation \"documents\" does not exist" in res.error:
                print("[WARNING] La tabla 'documents' no existe. Es necesario ejecutar docs/sql_init_supabase.sql")
            else:
                print(f"[ERROR] Error al consultar 'documents': {res.error}")
        else:
            print("[SUCCESS] Conexión establecida y tabla 'documents' detectada.")
            print(f"Datos encontrados: {len(res.data)} registros.")
            
    except Exception as e:
        print(f"[FATAL] Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_connection()
