import sys
import os
import json
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.supabase_client import get_supabase_client

def delete_doc():
    supabase = get_supabase_client()
    if not supabase:
        print("Error: No se pudo conectar a Supabase via get_supabase_client (revisar .env)")
        return

    filename_query = "COM-P-01 Gestión de proveedores"
    print(f"Buscando documentos que contengan: '{filename_query}'...")

    table = "documents"
    print(f"--- Checando tabla: {table} ---")
    
    try:
        # Fetch without order, just limit
        res = supabase.table(table).select("*").limit(50).execute()
        
        if res.error:
            print(f"Error al leer {table}: {res.error}")
            return
            
        docs = res.data
        if not docs:
            print(f"Tabla {table} vacía o sin resultados.")
            return

        # Print columns for debug
        print(f"Columnas detectadas: {list(docs[0].keys())}")
        
        found_ids = []
        for doc in docs:
            fname = doc.get("nombre_archivo", "") or doc.get("name", "") or ""
            if filename_query.lower() in fname.lower():
                found_ids.append((doc['id'], fname))
        
        if found_ids:
            print(f"Encontrados {len(found_ids)} registros en {table}:")
            for doc_id, fname in found_ids:
                print(f" - Eliminando: {fname} (ID: {doc_id})")
                del_res = supabase.table(table).delete().eq("id", doc_id).execute()
                if del_res.error:
                    print(f"   Error al eliminar: {del_res.error}")
                else:
                    print(f"   Eliminado correctamente.")
        else:
            print(f"No se encontraron coincidencias en {table}.")

    except Exception as e:
        print(f"Excepción procesando {table}: {e}")

if __name__ == "__main__":
    delete_doc()
