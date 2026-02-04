import hashlib
from utils.supabase_client import get_supabase_client


def calculate_pdf_hash(file_bytes):
    """
    Calculates the SHA-256 hash of the file bytes to identify uniqueness.
    """
    return hashlib.sha256(file_bytes).hexdigest()

def check_document_existence(file_hash, org_id=None):
    """
    Queries Supabase to check if a document with the same hash already exists.
    If org_id is provided, checks within that organization context.
    Returns the document data if found, else None.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
        
    query = supabase.table("documents").select("*").eq("hash_documento", file_hash)
    if org_id:
        query = query.eq("organization_id", org_id)
        
    response = query.execute()
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
        # 1. Insert into 'documents'
        # Mapping to SQL Schema schema
        db_doc = {
            "nombre_archivo": doc_data.get("filename", "Unknown"),
            "hash_documento": doc_data.get("file_hash"),
            "numero_paginas": doc_data.get("page_count", 0),
            "estado": "revisado",
            "version_actual": 1,
            "organization_id": doc_data.get("organization_id")
        }
        
        doc_res = supabase.table("documents").insert(db_doc).execute()
        
        # Check for RLS issues or empty return
        if not doc_res.data:
            err_detail = getattr(doc_res, 'error', 'Ninguno')
            return f"Error de Persistencia: Supabase no devolvió datos. Causa probable: Bloqueo RLS. Detalle: {err_detail}"
            
        doc_id = doc_res.data[0]['id']
        
        # 2. Insert into 'analysis_detallado'
        analysis_data = {
            "document_id": doc_id,
            "payload_completo": analysis_payload,
            "version": 1
        }
        ver_res = supabase.table("analysis_detallado").insert(analysis_data).execute()
        
        if not ver_res.data:
            return f"Error al guardar detalle: {getattr(ver_res, 'error', 'N/A')}"

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
        
    response = supabase.table("analysis_detallado") \
        .select("*") \
        .eq("document_id", doc_id) \
        .order("version", desc=True) \
        .limit(1) \
        .execute()
        
    # Map payload_completo to full_analysis_payload for compatibility
    if response.data:
        record = response.data[0]
        record['full_analysis_payload'] = record.get('payload_completo')
        return record
        
    return None

def update_document_version(doc_id, new_version, analysis_payload):
    supabase = get_supabase_client()
    if not supabase:
        return "Error: Cliente Supabase no inicializado."
    
    try:
        # 1. Update master document version
        upd_res = supabase.table('documents').update({'version_actual': new_version, 'fecha_actualizacion': 'now()'}).eq('id', doc_id).execute()
        if not upd_res.data:
            return f"Error al actualizar documento maestro: {getattr(upd_res, 'error', 'RLS o ID no encontrado')}"

        # 2. Insert new analysis version
        analysis_data = {
            'document_id': doc_id, 
            'payload_completo': analysis_payload, 
            'version': new_version
        }
        ins_res = supabase.table('analysis_detallado').insert(analysis_data).execute()
        
        if not ins_res.data:
             return f"Error al insertar nueva versión de análisis: {getattr(ins_res, 'error', 'Error desconocido')}"

        return True
    except Exception as e:
        return f"Excepción al actualizar versión: {str(e)}"

def register_revision(doc_id, v_old, v_new, diff_payload):
    supabase = get_supabase_client()
    if not supabase: return False
    
    revision_data = {
        'document_id': doc_id, 
        'version_anterior': v_old, 
        'version_nueva': v_new, 
        'cambios_detectados': diff_payload
    }
    supabase.table('revisiones_documento').insert(revision_data).execute()
    return True
