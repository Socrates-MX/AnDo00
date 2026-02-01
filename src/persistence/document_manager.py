import hashlib
from utils.supabase_client import get_supabase_client


def calculate_pdf_hash(file_bytes):
    """
    Calculates the SHA-256 hash of the file bytes to identify uniqueness.
    """
    return hashlib.sha256(file_bytes).hexdigest()

def check_document_existence(file_hash):
    """
    Queries Supabase to check if a document with the same hash already exists.
    Returns the document data if found, else None.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
        
    response = supabase.table("ando_documents").select("*").eq("file_hash", file_hash).execute()
    if response.data:
        return response.data[0]
    return None

def save_new_document(doc_data, analysis_payload):
    """
    Persists a new document and its initial detailed analysis in Supabase.
    Returns True on success, or a string error message on failure.
    """
    supabase = get_supabase_client()
    if not supabase:
        return "Error: Cliente Supabase no inicializado (Revise credenciales .env)"
        
    try:
        # 1. Insert into ando_documents
        # doc_data must contain 'organization_id' provided by the frontend/session
        doc_res = supabase.table("ando_documents").insert(doc_data).execute()
        
        # Check for RLS issues or empty return
        if not doc_res.data:
            err_detail = getattr(doc_res, 'error', 'Ninguno')
            return f"Error de Persistencia: Supabase no devolvió datos. Causa probable: Bloqueo RLS (Row Level Security) o Organization ID inválido. Detalle Técnico: {err_detail}"
            
        doc_id = doc_res.data[0]['id']
        
        # 2. Insert into ando_analysis_versions
        analysis_data = {
            "document_id": doc_id,
            "full_analysis_payload": analysis_payload,
            "version_number": 1
        }
        ver_res = supabase.table("ando_analysis_versions").insert(analysis_data).execute()
        
        if not ver_res.data:
            return f"Error al guardar versión: {getattr(ver_res, 'error', 'N/A')}"

        return True
    except Exception as e:
        return f"Excepción Crítica: {str(e)}"

def get_latest_analysis(doc_id):
    """
    Retrieves the most recent analysis for a given document.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
        
    response = supabase.table("ando_analysis_versions") \
        .select("*") \
        .eq("document_id", doc_id) \
        .order("version_number", desc=True) \
        .limit(1) \
        .execute()
        
    return response.data[0] if response.data else None

def update_document_version(doc_id, new_version, analysis_payload):
    supabase = get_supabase_client()
    if not supabase:
        return "Error: Cliente Supabase no inicializado."
    
    try:
        # 1. Update master document current_version
        upd_res = supabase.table('ando_documents').update({'current_version': new_version}).eq('id', doc_id).execute()
        if not upd_res.data:
            return f"Error al actualizar documento maestro: {getattr(upd_res, 'error', 'Error desconocido o RLS')}"

        # 2. Insert new analysis version
        analysis_data = {
            'document_id': doc_id, 
            'full_analysis_payload': analysis_payload, 
            'version_number': new_version
        }
        ins_res = supabase.table('ando_analysis_versions').insert(analysis_data).execute()
        
        if not ins_res.data:
             return f"Error al insertar nueva versión de análisis: {getattr(ins_res, 'error', 'Error desconocido')}"

        return True
    except Exception as e:
        return f"Excepción al actualizar versión: {str(e)}"

def register_revision(doc_id, v_old, v_new, diff_payload):
    supabase = get_supabase_client()
    if not supabase: return False
    revision_data = {'document_id': doc_id, 'version_from': v_old, 'version_to': v_new, 'diff_payload': diff_payload}
    supabase.table('ando_revisions').insert(revision_data).execute()
    return True
