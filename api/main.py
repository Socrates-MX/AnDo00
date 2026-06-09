from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form, Response, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os, uuid, shutil, json, base64
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Local Core Imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.supabase_client import supabase
from core.auth import verify_token
from core.utils import check_rate_limit, calculate_file_hash, normalize_filename
from core.tasks import consume_credit, log_audit
from analyzers import pdf_analyzer, detailed_analyzer
from generators.pdf_report_generator import create_full_report_pdf

load_dotenv()

app = FastAPI(title="AnDo API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://getauditup.com",
        "https://app.getauditup.com",
        "https://www.getauditup.com",
        "https://ando.getauditup.com",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    scenario: Optional[str] = None
    existing_id: Optional[str] = None
    version: Optional[str] = None
    conflict_details: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

class AnalysisConfirmRequest(BaseModel):
    task_id: str
    action: str 
    org_id: Optional[str] = None

@app.get("/")
def read_root(): return {"status": "online", "service": "AnDo API"}

@app.post("/analyze/preview")
async def preview_document(
    file: UploadFile = File(...),
    auth_user: dict = Depends(verify_token)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo PDF.")
    try:
        import pypdf
        reader = pypdf.PdfReader(file.file)
        num_pages = len(reader.pages)
        return {
            "status": "success",
            "filename": file.filename,
            "page_count": num_pages
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al leer el PDF.")


@app.post("/analyze/upload", response_model=TaskResponse)
async def upload_document(
    file: UploadFile = File(...), 
    org_id: Optional[str] = Form(None),
    selected_pages: Optional[str] = Form(None),
    extract_images: Optional[str] = Form("true"),
    force_ocr: Optional[str] = Form("false"),
    auth_user: dict = Depends(verify_token)
):
    try:
        if not org_id and auth_user.get("organization_id"):
            org_id = str(auth_user["organization_id"])
            
        if org_id: check_rate_limit(org_id)
        if auth_user.get("organization_id") and org_id != str(auth_user["organization_id"]):
            raise HTTPException(status_code=403, detail="No autorizado.")
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo PDF.")
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase no está configurado.")
            
        task_id = str(uuid.uuid4())
        temp_dir = '/tmp'
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Validations and OCR Check
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            num_pages = len(reader.pages)
            if num_pages > 20:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="El documento excede el límite permitido de 20 páginas.")
            
            sample_text = ""
            for i in range(min(3, num_pages)):
                sample_text += reader.pages[i].extract_text() or ""
            if len(sample_text.strip()) < 50:
                os.remove(file_path)
                try:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI()
                    prompt = f"El usuario subió un documento PDF '{file.filename}'. Detectamos que es escaneado. Menciona que requiere OCR y de qué trata brevemente."
                    completion = await client.chat.completions.create(
                        model=os.getenv("OPENAI_REASONING_MODEL", "gpt-4o-mini"),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    ocr_msg = completion.choices[0].message.content
                except:
                    ocr_msg = f"El documento '{file.filename}' requiere OCR."
                return {"task_id": task_id, "status": "ocr_required", "message": ocr_msg}
                
            token_cost = 3 if num_pages > 10 else 1
            warning_msg = "Procesando. (Aviso: Documento >10 págs, consume 3 tokens)." if num_pages > 10 else "Procesando"
        except Exception as e:
            if isinstance(e, HTTPException): raise e
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Error al validar estructura del PDF.")
        
        file_hash = calculate_file_hash(file_path)
        scenario = "NEW"
        conflict_details = None
        
        docs = supabase.table("ando_documents").select("*").eq("organization_id", org_id).eq("file_hash", file_hash).execute().data
        if docs:
            scenario = "MATCH"
            conflict_details = docs[0]
            
        # VERCEL STATELESS REFACTOR: Run Phase 1 (PDF OCR) inline!
        config = {
            "selected_pages": [int(x.strip()) for x in selected_pages.split(",") if x.strip()] if selected_pages else None,
            "extract_images": extract_images.lower() == "true",
            "force_ocr": force_ocr.lower() == "true",
        }
        
        extraction_result = pdf_analyzer.analyze_pdf(file_path, config=config)
        if not extraction_result:
             os.remove(file_path)
             raise HTTPException(status_code=500, detail="Fallo en la extracción de texto del PDF.")
             
        pages_data, pdf_meta = extraction_result
        
        # Serialize pages for Supabase (Drop image bytes to prevent 413 Payload Too Large)
        serialized_pages = []
        for p in pages_data:
            clean_imgs = []
            for i_idx, img in enumerate(p.get("images", [])):
                img_copy = img.copy()
                img_copy["description"] = "[SKIP] Análisis visual deshabilitado"
                img_copy.pop("image_bytes", None)
                clean_imgs.append(img_copy)
            pc = p.copy()
            pc["images"] = clean_imgs
            serialized_pages.append(pc)
            
        # Save to DB to maintain state across Vercel requests
        status_to_save = "pending_decision" if scenario != "NEW" else "pending_ai"
        
        if scenario == "NEW":
            if not consume_credit(org_id, token_cost, f"Análisis ({num_pages} págs): {file.filename}"):
                os.remove(file_path)
                raise HTTPException(status_code=402, detail="Créditos insuficientes.")
                
            doc_data = {
                "organization_id": org_id,
                "file_name": file.filename,
                "file_hash": file_hash,
                "page_count": len(serialized_pages),
                "status": status_to_save
            }
                
            res_doc = supabase.table("ando_documents").insert(doc_data).execute()
            if not res_doc.data:
                os.remove(file_path)
                raise HTTPException(status_code=500, detail="Fallo al guardar el documento en la base de datos.")
            doc_db_id = res_doc.data[0]['id']
            version_number = 1
        else:
            doc_db_id = conflict_details["id"]
            version_res = supabase.table("ando_analysis_versions").select("version_number").eq("document_id", doc_db_id).order("version_number", desc=True).limit(1).execute()
            version_number = (version_res.data[0]["version_number"] + 1) if version_res.data else 1
        
        # Save payload
        version_data = {
            "document_id": doc_db_id,
            "version_number": version_number,
            "full_analysis_payload": {
                "metadata": pdf_meta,
                "pages": serialized_pages,
                "status": status_to_save
            }
        }
        supabase.table("ando_analysis_versions").insert(version_data).execute()
        
        # Cleanup
        os.remove(file_path)
        
        return {
            "task_id": str(doc_db_id), # We use the DB id as task_id now
            "status": status_to_save if status_to_save == "pending_decision" else "pending", 
            "message": warning_msg if scenario == "NEW" else "Procesando", 
            "scenario": scenario,
            "existing_id": conflict_details.get("id") if conflict_details else None,
            "version": str(conflict_details.get("current_version", "1")) if conflict_details else None,
            "conflict_details": conflict_details,
            "data": None
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        import traceback
        trace_str = traceback.format_exc()
        print(f"🚨 Unhandled Error in upload_document: {trace_str}")
        raise HTTPException(status_code=500, detail=trace_str)

@app.post("/analyze/confirm")
async def confirm_analysis(req: AnalysisConfirmRequest):
    doc_id = req.task_id
    if not supabase: raise HTTPException(status_code=500)
    
    res = supabase.table("ando_documents").select("*").eq("id", doc_id).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Task not found")
    
    if req.action == "cancel":
        supabase.table("ando_documents").update({"status": "cancelled"}).eq("id", doc_id).execute()
        return {"status": "cancelled"}
    
    if req.action == "full_analysis":
        # Just advance state machine, frontend poll will pick it up
        supabase.table("ando_documents").update({"status": "pending_ai"}).eq("id", doc_id).execute()
        
        version_res = supabase.table("ando_analysis_versions").select("*").eq("document_id", doc_id).order("version_number", desc=True).limit(1).execute()
        if version_res.data:
             payload = version_res.data[0]["full_analysis_payload"]
             payload["status"] = "pending_ai"
             supabase.table("ando_analysis_versions").update({"full_analysis_payload": payload}).eq("id", version_res.data[0]["id"]).execute()
        
        return {
            "task_id": doc_id,
            "status": "pending",
            "data": None
        }
    
    return {"status": "unknown_action"}

@app.get("/analyze/{task_id}")
def get_status(task_id: str, auth_user: dict = Depends(verify_token)):
    if not supabase: raise HTTPException(status_code=500)
    res = supabase.table("ando_documents").select("*").eq("id", task_id).execute()
    if not res.data: raise HTTPException(status_code=404)
    doc = res.data[0]
    
    # State Machine: Phase 2
    if doc["status"] == "pending_ai":
        # Lock row to prevent parallel executions if polling is too aggressive
        lock_res = supabase.table("ando_documents").update({"status": "processing_ai"}).eq("id", task_id).eq("status", "pending_ai").execute()
        if not lock_res.data:
            return {"task_id": task_id, "status": "pending"} # Someone else took the lock
            
        try:
            version_res = supabase.table("ando_analysis_versions").select("*").eq("document_id", task_id).order("version_number", desc=True).limit(1).execute()
            version = version_res.data[0]
            payload = version["full_analysis_payload"]
            pages_data = payload["pages"]
            pdf_meta = payload["metadata"]
            
            # Image bytes were dropped in Phase 1, no need to reconstruct
            
            detailed_json_raw, detailed_usage = detailed_analyzer.extract_detailed_analysis(pages_data)
            detailed_report = json.loads(detailed_json_raw)
            
            final_result = {
                "metadata": pdf_meta,
                "pages": payload["pages"], # keep base64 strings for db
                "detailed_report": detailed_report,
                "congruence_report": {},
                "process_cross_report": {},
                "index_card": {},
                "page_count": len(pages_data),
                "usage_stats": detailed_usage,
                "document_db_id": task_id
            }
            
            supabase.table("ando_analysis_versions").update({"full_analysis_payload": final_result}).eq("id", version["id"]).execute()
            supabase.table("ando_documents").update({"status": "completed"}).eq("id", task_id).execute()
            
            return {"task_id": task_id, "status": "completed", "data": final_result}
            
        except Exception as e:
            supabase.table("ando_documents").update({"status": "failed"}).eq("id", task_id).execute()
            print(f"🚨 AI Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {"task_id": task_id, "status": "failed", "error": str(e)}
            
    elif doc["status"] == "completed":
        version_res = supabase.table("ando_analysis_versions").select("*").eq("document_id", task_id).order("version_number", desc=True).limit(1).execute()
        if version_res.data:
            return {"task_id": task_id, "status": "completed", "data": version_res.data[0]["full_analysis_payload"]}
            
    elif doc["status"] == "failed":
        return {"task_id": task_id, "status": "failed", "error": "Analysis encountered an internal error."}
        
    # Still processing or pending
    return {"task_id": task_id, "status": "pending"}

@app.get("/documents")
def list_docs(auth_user: dict = Depends(verify_token)):
    if not supabase: return []
    return supabase.table("ando_documents").select("*").eq("organization_id", auth_user["organization_id"]).order("updated_at", desc=True).execute().data

@app.get("/documents/{document_id}")
def get_document_details(document_id: str, auth_user: dict = Depends(verify_token)):
    """
    Fetch full analysis from 'ando_analysis_versions'.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
        
    try:
        # 1. Get header
        doc_res = supabase.table("ando_documents").select("*").eq("id", document_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        doc = doc_res.data[0]
        
        # SECURITY CHECK
        if str(doc.get("organization_id")) != str(auth_user["organization_id"]):
             raise HTTPException(status_code=403, detail="No autorizado para ver este documento.")
        
        # 2. Get latest analysis for this specific doc record
        analysis_res = supabase.table("ando_analysis_versions")\
            .select("*")\
            .eq("document_id", document_id)\
            .order("version_number", desc=True)\
            .limit(1)\
            .execute()
            
        if not analysis_res.data:
            return {"status": "error", "message": "No analysis versions found for this document."}
            
        analysis_payload = analysis_res.data[0].get("full_analysis_payload")
        
        # Combine meta
        return {
            "status": "completed",
            "data": analysis_payload,
            "metadata": doc
        }

    except Exception as e:
        print(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/report")
def generate_report(document_id: str, auth_user: dict = Depends(verify_token)):
    """
    Generates a PDF report for the given document ID on the fly.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # Fetch meta from ando_documents
        doc_res = supabase.table("ando_documents").select("*").eq("id", document_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        doc = doc_res.data[0]

        # SECURITY CHECK
        if str(doc.get("organization_id")) != str(auth_user["organization_id"]):
             raise HTTPException(status_code=403, detail="No autorizado para descargar este reporte.")

        # LOG AUDIT
        log_audit(
            org_id=doc["organization_id"],
            user_id=auth_user["id"],
            action="DOWNLOAD_REPORT",
            doc_id=document_id,
            res_name=doc["file_name"]
        )

        # Fetch analysis from ando_analysis_versions
        analysis_res = supabase.table("ando_analysis_versions") \
            .select("*") \
            .eq("document_id", document_id) \
            .order("version_number", desc=True) \
            .limit(1) \
            .execute()
            
        if not analysis_res.data:
             raise HTTPException(status_code=404, detail="Analysis payload not found")
        
        payload = analysis_res.data[0].get("full_analysis_payload", {})
        
        # --- PDF GENERATION LOGIC ---
        pdf_bytes = create_full_report_pdf(payload)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{document_id[:8]}.pdf"}
        )

    except Exception as e:
        print(f"PDF Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/{document_id}/version")
async def update_document_version(
    document_id: str, 
    payload: Dict[str, Any],
    auth_user: dict = Depends(verify_token)
):
    """
    Creates a new version of the analysis for a document after manual edits.
    Uses 'ando_documents' and 'ando_analysis_versions'.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # 1. Get current version info
        doc_res = supabase.table("ando_documents").select("*").eq("id", document_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        current_doc = doc_res.data[0]

        # SECURITY CHECK
        if str(current_doc.get("organization_id")) != str(auth_user["organization_id"]):
             raise HTTPException(status_code=403, detail="No autorizado para editar este documento.")
        new_v = (current_doc.get("current_version") or 1) + 1

        # 2. Insert new analysis version record
        analysis_record = {
            "document_id": document_id,
            "version_number": new_v,
            "full_analysis_payload": payload
        }
        
        ins_res = supabase.table("ando_analysis_versions").insert(analysis_record).execute()
        
        if not ins_res.data:
             raise HTTPException(status_code=500, detail="Failed to insert new analysis version")

        # 3. Update master document record
        upd_res = supabase.table("ando_documents") \
            .update({
                "current_version": new_v, 
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("id", document_id) \
            .execute()
            
        # LOG AUDIT
        log_audit(
            org_id=auth_user["organization_id"],
            user_id=auth_user["id"],
            action="SAVE_VERSION",
            doc_id=document_id,
            res_name=current_doc["file_name"],
            metadata={"new_version": new_v}
        )

        return {
            "status": "success",
            "message": f"Version updated to V{new_v}",
            "new_version": new_v
        }

    except Exception as e:
        print(f"Update Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/documents/{document_id}/assignment")
async def update_document_assignment(
    document_id: str,
    assignment: Dict[str, Any],
    auth_user: dict = Depends(verify_token)
):
    """
    Updates the legal_entity_id for a document.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")

    legal_entity_id = assignment.get("legal_entity_id")
    
    try:
        # 1. Security Check
        doc_res = supabase.table("ando_documents").select("*").eq("id", document_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = doc_res.data[0]
        if str(doc.get("organization_id")) != str(auth_user["organization_id"]):
             raise HTTPException(status_code=403, detail="No autorizado para editar este documento.")

        # 2. Update
        res = supabase.table("ando_documents") \
            .update({"legal_entity_id": legal_entity_id}) \
            .eq("id", document_id) \
            .execute()
            
        # LOG AUDIT
        log_audit(
            org_id=auth_user["organization_id"],
            user_id=auth_user["id"],
            action="ASSIGN_ENTITY",
            doc_id=document_id,
            res_name=doc["file_name"],
            metadata={"legal_entity_id": legal_entity_id}
        )

        return {"status": "success", "message": "Document assignment updated"}
    except Exception as e:
        print(f"Assignment Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
def delete_document(document_id: str, auth_user: dict = Depends(verify_token)):
    """
    Deletes a document and all its associated analysis versions from official tables.
    """
    print(f"🗑️ [DELETE REQUEST] Deleting document: {document_id} by User: {auth_user['id']}")

    if not supabase:
        print("❌ Database not connected")
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # 1. Security Check before delete
        doc_res = supabase.table("ando_documents").select("*").eq("id", document_id).execute()
        
        if not doc_res.data:
             print(f"❌ Document {document_id} not found in DB")
             raise HTTPException(status_code=404, detail="Document not found")
        
        doc = doc_res.data[0]
        
        if str(doc.get("organization_id")) != str(auth_user["organization_id"]):
             print(f"🚫 Unauthorized delete attempt by {auth_user['id']} (Org {auth_user['organization_id']}) on Doc {document_id} (Org {doc.get('organization_id')})")
             raise HTTPException(status_code=403, detail="No autorizado para eliminar este documento.")

        # LOG AUDIT
        try:
            log_audit(
                org_id=doc["organization_id"],
                user_id=auth_user["id"],
                action="DELETE",
                doc_id=document_id,
                res_name=doc["file_name"]
            )
        except Exception as audit_err:
            print(f"⚠️ Audit log failed (non-critical): {audit_err}")

        # 2. Delete versions first (Manual Cascade just in case)
        print(f"🗑️ Deleting versions for doc: {document_id}")
        vers_res = supabase.table("ando_analysis_versions").delete().eq("document_id", document_id).execute()
        print(f"✅ Versions deleted: {vers_res}")

        # 3. Delete master document
        print(f"🗑️ Deleting master record: {document_id}")
        res = supabase.table("ando_documents").delete().eq("id", document_id).execute()
        
        print(f"✅ Delete success for {document_id}: {res}")
        return {"status": "success", "message": f"Document {document_id} and history deleted"}

    except Exception as e:
        print(f"❌ Delete Error Trace: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

