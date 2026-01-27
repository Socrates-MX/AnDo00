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
        
    response = supabase.table("documents").select("*").eq("hash_documento", file_hash).execute()
    if response.data:
        return response.data[0]
    return None

def save_new_document(doc_data, analysis_payload):
    """
    Persists a new document and its initial detailed analysis in Supabase.
    """
    supabase = get_supabase_client()
    if not supabase:
        return False
        
    try:
        # 1. Insert into documents
        doc_res = supabase.table("documents").insert(doc_data).execute()
        if not doc_res.data:
            return False
            
        doc_id = doc_res.data[0]['id']
        
        # 2. Insert into analysis_detallado
        analysis_data = {
            "document_id": doc_id,
            "payload_completo": analysis_payload,
            "version": 1
        }
        supabase.table("analysis_detallado").insert(analysis_data).execute()
        return True
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        return False

def get_latest_analysis(doc_id):
    """
    Retrieves the most recent analysis for a given document.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
        
    response = supabase.table("analysis_detallado") \
        .select("*") \
        .eq("document_id", doc_id) \
        .order("version", desc=True) \
        .limit(1) \
        .execute()
        
    return response.data[0] if response.data else None

def update_document_version(doc_id, new_version, analysis_payload):
    supabase = get_supabase_client()
    if not supabase: return False
    try:
        supabase.table('documents').update({'version_actual': new_version}).eq('id', doc_id).execute()
        analysis_data = {'document_id': doc_id, 'payload_completo': analysis_payload, 'version': new_version}
        supabase.table('analysis_detallado').insert(analysis_data).execute()
        return True
    except Exception: return False

def register_revision(doc_id, v_old, v_new, diff_payload):
    supabase = get_supabase_client()
    if not supabase: return False
    revision_data = {'document_id': doc_id, 'version_anterior': v_old, 'version_nueva': v_new, 'cambios_detectados': diff_payload, 'aceptado_por_usuario': True}
    supabase.table('revisiones_documento').insert(revision_data).execute()
    return True
