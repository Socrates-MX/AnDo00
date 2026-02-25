from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form, Response, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import uuid
import shutil
import base64
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Try to import Supabase
try:
    from supabase import create_client, Client
except ImportError:
    print("Warning: supabase-py not installed.")
    Client = None

load_dotenv()

# Add src to path so we can import existing logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from analyzers import pdf_analyzer
except ImportError:
    print("Warning: analyzers module not found immediately. Checking path...")

app = FastAPI(
    title="AnDo API",
    description="Backend API for Document Analysis (Headless)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://getauditup.com",
        "https://ando.getauditup.com",
        "https://arc.getauditup.com",
        "https://legado.getauditup.com",
        "https://compliance.getauditup.com",
        "https://getauditup-compliance-web.web.app",
        "https://getauditup-compliance-web.firebaseapp.com",
        "https://getauditupcompliance.web.app", 
        "https://getauditupcompliance.firebaseapp.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL") 
# We prefer SERVICE_ROLE_KEY for headless backend operations to bypass RLS if needed,
# Falling back to the regular key if not present.
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") 
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase Client Initialized ({'Service Role' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'Anon Key'})")
    except Exception as e:
        print(f"❌ Failed to init Supabase: {e}")
else:
    print("⚠️ Supabase credentials not found. Persistence disabled.")


# --- AUTHENTICATION DEPENDENCY ---
async def verify_token(authorization: str = Header(None)):
    """
    Validates the Supabase JWT and retrieves the user's organization.
    """
    if not supabase:
        # If in dev mode without Supabase, we skip check (not recommended for prod)
        return {"id": "dev_user", "organization_id": None}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Se requiere un token de sesión válido (Bearer Token)."
        )

    token = authorization.split(" ")[1]
    try:
        # 1. Validate Token with Supabase
        user_res = supabase.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Sesión expirada o inválida.")
        
        user_id = user_res.user.id
        
        # 2. Get Profile to find organization_id
        # We use the existing supabase client (service role) to fetch the profile
        profile_res = supabase.table("profiles").select("organization_id").eq("id", user_id).single().execute()
        
        if not profile_res.data:
            raise HTTPException(status_code=403, detail="Usuario no tiene un perfil configurado.")
            
        return {
            "id": user_id,
            "organization_id": profile_res.data.get("organization_id")
        }
    except Exception as e:
        print(f"🚨 Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Error en la validación de identidad.")


# --- IN-MEMORY STATE (Replacing Redis for MVP) ---
tasks_db: Dict[str, Dict[str, Any]] = {}

# --- MODELS ---
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    scenario: Optional[str] = None
    conflict_details: Optional[Dict[str, Any]] = None
    existing_id: Optional[str] = None
    version: Optional[str] = None

class AnalysisConfirmRequest(BaseModel):
    task_id: str
    action: str  # 'full_analysis', 'changes_only', 'cancel'
    org_id: Optional[str] = None

class AnalysisResult(BaseModel):
    task_id: str
    status: str
    created_at: str
    current_step: Optional[str] = None
    current_detail: Optional[str] = None
    steps: Optional[list] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_duplicate: Optional[bool] = False
    existing_doc_id: Optional[str] = None
    scenario: Optional[str] = None

# --- HELPER FUNCTIONS ---
def calculate_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def consume_credit(org_id: str, amount: int, concept: str) -> bool:
    """
    Consumes tokens from the organization's wallet via Supabase RPC.
    Returns True if consumption was successful, False otherwise.
    """
    if not supabase:
        print("⚠️ Supabase not connected. Skipping credit consumption.")
        return True
    
    if not org_id:
        print("⚠️ No org_id provided for credit consumption.")
        return False

    try:
        # Call the RPC function defined in supa_saas_schema.sql
        res = supabase.rpc("consume_tokens", {
            "p_org_id": org_id,
            "p_amount": amount,
            "p_app": "ANDO",
            "p_concept": concept
        }).execute()
        
        # res.data should be True if deducted, False if insufficient
        return res.data is True
    except Exception as e:
        print(f"❌ Error during credit consumption: {e}")
        return False

# --- RATE LIMITING ---
from collections import defaultdict
import time

# Simple in-memory rate limiter: max 5 requests per 60 seconds per organization
ORG_RATE_LIMITS = defaultdict(list)
MAX_REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 60

def check_rate_limit(org_id: str):
    if not org_id: return
    
    current_time = time.time()
    # Clean up old timestamps
    ORG_RATE_LIMITS[org_id] = [t for t in ORG_RATE_LIMITS[org_id] if current_time - t < WINDOW_SECONDS]
    
    if len(ORG_RATE_LIMITS[org_id]) >= MAX_REQUESTS_PER_WINDOW:
        print(f"⚠️ Rate Limit Hit for Org: {org_id}")
        raise HTTPException(
            status_code=429, 
            detail=f"Múltiples peticiones detectadas. Límite de {MAX_REQUESTS_PER_WINDOW} análisis por minuto alcanzado."
        )
    
    ORG_RATE_LIMITS[org_id].append(current_time)

def log_audit(org_id: str, user_id: str, action: str, doc_id: str = None, res_name: str = None, metadata: dict = {}):
    """
    Logs an action to the central audit_logs table via Supabase RPC.
    """
    if not supabase: return
    try:
        supabase.rpc("log_action_system", {
            "p_org_id": org_id,
            "p_user_id": user_id,
            "p_action": action,
            "p_app": "ANDO",
            "p_doc_id": doc_id,
            "p_res_name": res_name,
            "p_metadata": metadata
        }).execute()
        print(f"📝 Audit Log: {action} for Org {org_id} by User {user_id}")
    except Exception as e:
        print(f"⚠️ Audit Log failed: {e}")

def normalize_filename(filename: str) -> str:
    """Normaliza el nombre del archivo para comparaciones."""
    import re
    # Quitar extensión, pasar a minúsculas, quitar espacios extra
    name = os.path.splitext(filename)[0].lower().strip()
    name = re.sub(r'\s+', ' ', name)
    # Opcional: quitar sufijos comunes de copias (1), (2), final, v2
    name = re.sub(r'\s*\(\d+\)$', '', name)
    name = re.sub(r'[\s_-]final$', '', name)
    name = re.sub(r'[\s_-]v\d+$', '', name)
    return name

def update_task_progress(task_id: str, step_index: int, step_description: str, detail: str = None):
    if task_id in tasks_db:
        tasks_db[task_id]["current_step_index"] = step_index
        tasks_db[task_id]["current_step"] = step_description
        if "steps" not in tasks_db[task_id]:
            tasks_db[task_id]["steps"] = []
        
        tasks_db[task_id]["steps"] = [
            {"label": "Fase 1/5: Digitalizando documento y extrayendo texto (OCR)...", "status": "completed" if step_index > 1 else "processing" if step_index == 1 else "pending"},
            {"label": "Fase 2/5: Analizando elementos visuales e imágenes...", "status": "completed" if step_index > 2 else "processing" if step_index == 2 else "pending"},
            {"label": "Fase 3/5: Generando Informe Estructural del Análisis (Deep Analysis)...", "status": "completed" if step_index > 3 else "processing" if step_index == 3 else "pending"},
            {"label": "Fase 4/5: Construyendo Índice Lógico y Validando Congruencia...", "status": "completed" if step_index > 4 else "processing" if step_index == 4 else "pending"},
            {"label": "Fase 5/5: Ejecutando Cruce Diagrama vs Procedimientos...", "status": "completed" if step_index > 5 else "processing" if step_index == 5 else "pending"}
        ]
        
        # Inject detail into active step
        if detail and 0 <= step_index - 1 < len(tasks_db[task_id]["steps"]):
             tasks_db[task_id]["steps"][step_index - 1]["detail"] = detail
             tasks_db[task_id]["current_detail"] = detail



async def run_analysis_task(task_id: str, file_path: str):
    """
    Background task to run the full analysis pipeline.
    """
    from analyzers import detailed_analyzer, congruence_analyzer, process_cross_analyzer
    from generators import report_generator
    import json

    try:
        tasks_db[task_id]["status"] = "processing"
        
        # --- PHASE 1 ---
        def phase1_progress(current, total):
             update_task_progress(task_id, 1, "Digitalizando documento...", detail=f"Procesando página {current} de {total}...")

        update_task_progress(task_id, 1, "Digitalizando documento...")
        extraction_result = pdf_analyzer.analyze_pdf(file_path, progress_callback=phase1_progress)
        
        if extraction_result is None:
            raise Exception("Failed to extract data from PDF")
            
        pages_data, pdf_meta = extraction_result
        
        # --- PHASE 1.5: PII SANITIZATION ---
        try:
            from utils.pii_sanitizer import PIISanitizer
            print("🛡️ Applying PII Sanitization...")
            pages_data = PIISanitizer.sanitize_pages_data(pages_data)
        except Exception as pii_err:
            print(f"⚠️ PII Sanitization failed (continuing with raw data): {pii_err}")

        # --- TOKEN TRACKING ---
        usage_stats = {
            "image_analysis": {"total_token_count": 0},
            "detailed_analysis": {"total_token_count": 0},
            "raw_analysis": {"total_token_count": 0},
            "congruence_analysis": {"total_token_count": 0},
            "process_cross_analysis": {"total_token_count": 0},
            "index_analysis": {"total_token_count": 0},
            "total_tokens": 0
        }

        # --- PHASE 2 ---
        update_task_progress(task_id, 2, "Analizando elementos visuales e imágenes...")
        from analyzers import image_analyzer
        
        serialized_pages = []
        for p_idx, page in enumerate(pages_data):
            clean_images = []
            images = page.get("images", [])
            
            for img_idx, img in enumerate(images):
                # 2.1 AI Interpretation
                if "image_bytes" in img and img["image_bytes"]:
                    update_task_progress(task_id, 2, "Analizando imágenes...", detail=f"Pág {page['page_number']}: Interpretando imagen {img_idx+1} de {len(images)}...")
                    try:
                        desc, usage = image_analyzer.generate_image_description(img["image_bytes"])
                        if usage:
                            usage_stats["image_analysis"]["total_token_count"] += usage.get("total_token_count", 0)
                    except Exception as e:
                        print(f"Error interpreting image: {e}")
                        desc = "[Error en análisis de imagen]"
                else:
                    desc = "[No image data]"

                img_copy = img.copy()
                img_copy["description"] = desc
                img_copy.pop("image_bytes", None) # Remove raw bytes/obj to allow strict JSON serialization
                clean_images.append(img_copy)
                
            # Reconstruct page with processed images
            page_copy = page.copy()
            page_copy["images"] = clean_images
            serialized_pages.append(page_copy)
            
        # Update pages_data for next phases (they need the descriptions)
        pages_data = serialized_pages


        # --- PHASE 3: DETAILED ANALYSIS ---
        update_task_progress(task_id, 3, "Generando informe estructural...")
        try:
             detailed_json_raw, usage = detailed_analyzer.extract_detailed_analysis(pages_data, file_path=file_path)
             detailed_report = json.loads(detailed_json_raw)
             if usage:
                 usage_stats["detailed_analysis"] = usage
        except Exception as e:
             print(f"Phase 3 Error: {e}")
             detailed_report = None

        if detailed_report and "mermaid_graph" not in detailed_report:
             detailed_report["mermaid_graph"] = "graph TD;\nStart((Inicio)) --> Process[Análisis Preliminar];\nProcess --> End((Fin));\nstyle Process fill:#ececff,stroke:#9370db,stroke-width:2px;"

        # --- PRE-PHASE 4: RAW CONSOLIDATION & RAW ANALYSIS ---
        update_task_progress(task_id, 4, "Generando análisis paralelo RAW...")
        from analyzers import raw_congruence_analyzer
        
        consolidacion_raw_object = {}
        raw_congruence_report = None
        
        try:
            # Build RAW Object (Server-Side)
            raw_pages_list = []
            for p in serialized_pages:
                p_images = p.get("images", [])
                valid_imgs_data = []
                for img in p_images:
                    desc = img.get("description", "")
                    if desc and "[SKIP]" not in desc and "Pendiente" not in desc:
                        valid_imgs_data.append({
                            "imagen_id": img.get("name", "unknown"),
                            "tipo": "Imagen Interpretada",
                            "texto_interpretado": desc
                        })
                
                raw_pages_list.append({
                    "pagina": p.get("page_number"),
                    "contenido_raw_pdf": p.get("text_content", ""),
                    "contenido_raw_imagenes": valid_imgs_data
                })
            
            consolidacion_raw_object = {
                "documento": {
                    "total_paginas": len(serialized_pages),
                    "analisis_raw": raw_pages_list,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            # Execute RAW Analysis
            if consolidacion_raw_object:
                print(f"✅ RAW Object created with {len(consolidacion_raw_object['documento']['analisis_raw'])} pages. Sending to IA...")
                raw_congruence_report = raw_congruence_analyzer.analyze_raw_congruence(consolidacion_raw_object)
                if raw_congruence_report and "usage" in raw_congruence_report:
                    usage_stats["raw_analysis"] = raw_congruence_report["usage"]
                print(f"✅ RAW Analysis returned type: {type(raw_congruence_report)}")
            else:
                print("❌ RAW Object is empty.")
                
        except Exception as e:
            print(f"Error building/analyzing RAW json: {e}")
            import traceback
            traceback.print_exc()

        # --- PHASE 4: INDEX & CONGRUENCE ---
        update_task_progress(task_id, 4, "Validando congruencia...")
        index_card = None
        congruence_report = None
        
        if detailed_report:
            try:
                index_card = report_generator.generate_index_card(pages_data)
                if index_card and "usage" in index_card:
                    usage_stats["index_analysis"] = index_card["usage"]
                
                congruence_report = congruence_analyzer.analyze_document_congruence(detailed_report, pages_data)
                if congruence_report and "usage" in congruence_report:
                    usage_stats["congruence_analysis"] = congruence_report["usage"]
            except Exception as e:
                print(f"Phase 4 Error: {e}")

        # --- PHASE 5: PROCESS CROSS ---
        update_task_progress(task_id, 5, "Finalizando cruce...")
        process_cross_report = None
        
        if detailed_report:
            try:
                process_cross_report = process_cross_analyzer.analyze_process_crossing(detailed_report, pages_data)
                if process_cross_report and "usage" in process_cross_report:
                    usage_stats["process_cross_analysis"] = process_cross_report["usage"]
            except Exception as e:
                print(f"Phase 5 Error: {e}")

        # --- PHASE 6: IMPERSONATION CHECK ---
        impersonation_alerts = []
        try:
            from analyzers import impersonation_analyzer
            impersonation_alerts = impersonation_analyzer.analyze_impersonation(pages_data, detailed_report)
        except Exception as e:
            print(f"Phase 6 Error: {e}")

        # Calculate total tokens
        usage_stats["total_tokens"] = sum(
            s.get("total_token_count", 0) for k, s in usage_stats.items() if isinstance(s, dict)
        )

        # STORE SUCCESS
        final_result = {
            "metadata": pdf_meta,
            "pages": serialized_pages,
            "detailed_report": detailed_report,
            "congruence_report": congruence_report,
            "process_cross_report": process_cross_report,
            "raw_congruence_report": raw_congruence_report if raw_congruence_report else {}, # NEW
            "impersonation_alerts": impersonation_alerts,
            "index_card": index_card,
            "page_count": len(serialized_pages),
            "usage_stats": usage_stats
        }
        
        tasks_db[task_id]["result"] = final_result
        
        # --- SAVE TO SUPABASE ---
        if supabase:
            try:
                task_data = tasks_db[task_id]
                org_id = task_data.get("org_id")
                filename = task_data.get("filename")
                file_hash = task_data.get("hash")
                
                # 0. Get info if version family exists
                conflict_details = task_data.get("conflict_details")
                version_to_set = 1
                
                if conflict_details:
                    # Increment version based on previous one
                    version_to_set = conflict_details.get("current_version", 1) + 1
                
                # 1. Insert into 'ando_documents' (Master Record for this version)
                doc_header = {
                    "organization_id": org_id,
                    "file_name": filename,
                    "file_hash": file_hash,
                    "page_count": len(serialized_pages),
                    "current_version": version_to_set,
                    "status": "active",
                    "updated_at": datetime.now().isoformat()
                }
                
                # Execute insert
                res_doc = supabase.table("ando_documents").insert(doc_header).execute()
                
                if res_doc.data and len(res_doc.data) > 0:
                    new_doc_id = res_doc.data[0]['id']
                    
                    # INJECT ID back to result for frontend
                    final_result["document_db_id"] = new_doc_id
                    tasks_db[task_id]["result"] = final_result

                    # 2. Insert Analysis version payload
                    version_entry = {
                        "document_id": new_doc_id,
                        "version_number": version_to_set,
                        "full_analysis_payload": final_result
                    }
                    supabase.table("ando_analysis_versions").insert(version_entry).execute()
                    
                    print(f"✅ V{version_to_set} Analysis saved in 'ando_documents' and 'ando_analysis_versions'. ID: {new_doc_id}")
                else:
                    print("❌ Failed to insert document header into 'ando_documents'.")

            except Exception as db_err:
                print(f"❌ Failed to save to Supabase: {db_err}")
            
            # --- LOG AUDIT (SUCCESS) ---
            log_audit(
                org_id=org_id,
                user_id=task_data.get("user_id"),
                action="ANALYZE_COMPLETED",
                doc_id=new_doc_id if 'new_doc_id' in locals() else None,
                res_name=filename,
                metadata={"tokens": usage_stats.get("total_tokens", 0), "version": version_to_set}
            )
        
        # FINAL STATUS UPDATE (after DB attempt)
        tasks_db[task_id]["status"] = "completed"
        update_task_progress(task_id, 6, "Completado")

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
        print(f"Task {task_id} failed: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"status": "online", "service": "AnDo API", "mode": "Headless SaaS + Supabase", "version": "1.1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok", "supabase": supabase is not None}

@app.post("/analyze/upload", response_model=TaskResponse)
async def upload_document(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    org_id: Optional[str] = Form(None),
    auth_user: dict = Depends(verify_token)
):
    print(f"🔥 [ENDPOINT] Received upload request for file: {file.filename}", flush=True)

    # --- RATE LIMIT CHECK ---
    if org_id:
        check_rate_limit(org_id)

    # --- SECURITY CHECK ---
    # Ensure the org_id sent in the form matches the user's authenticated organization
    if auth_user["organization_id"] and org_id != str(auth_user["organization_id"]):
        print(f"🚫 Security Breach Attempt: User {auth_user['id']} tried to upload for Org {org_id}")
        raise HTTPException(
            status_code=403, 
            detail="No tiene permisos para subir documentos a esta organización."
        )
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    task_id = str(uuid.uuid4())
    temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved to temp: {file_path}", flush=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    # --- STEP 1: CALCULATE HINTS ---
    file_hash = calculate_file_hash(file_path)
    filename_original = file.filename
    normalized_name = normalize_filename(file.filename)
    
    scenario = "NEW"
    conflict_details = None
    existing_id = None
    existing_version = "1"
    
    # --- STEP 2: CONSULT SUPABASE (PRIORITIZED) ---
    if supabase and org_id:
        try:
            # Current approach: 1. Search by hash first (covers A and B)
            docs_with_hash = supabase.table("ando_documents").select("*")\
                .eq("organization_id", org_id)\
                .eq("file_hash", file_hash)\
                .eq("status", "active")\
                .execute().data
            
            if docs_with_hash:
                # Check for A (Exact: Hash + Name)
                exact = next((d for d in docs_with_hash if normalize_filename(d['file_name']) == normalized_name), None)
                if exact:
                    scenario = "EXACT_MATCH"
                    conflict_details = exact
                else:
                    # Case B: Contenido idéntico but different name
                    scenario = "CONTENT_ONLY"
                    conflict_details = docs_with_hash[0]
            else:
                # Check for C (Name similar but different hash)
                docs_with_name = supabase.table("ando_documents").select("*")\
                    .eq("organization_id", org_id)\
                    .eq("status", "active")\
                    .execute().data
                
                # Manual name match
                match_name = next((d for d in docs_with_name if normalize_filename(d['file_name']) == normalized_name), None)
                if match_name:
                    scenario = "NAME_ONLY"
                    conflict_details = match_name

            if conflict_details:
                existing_id = conflict_details.get('id')
                existing_version = str(conflict_details.get('current_version', 1))

        except Exception as e:
            print(f"Warning: priority search failed: {e}")

    # Register task in memory with initial metadata
    tasks_db[task_id] = {
        "status": "pending_decision" if scenario != "NEW" else "pending",
        "created_at": datetime.now().isoformat(),
        "filename": filename_original,
        "hash": file_hash,
        "org_id": org_id,
        "user_id": auth_user["id"], # Store for audit logs
        "file_path": file_path,
        "scenario": scenario,
        "conflict_details": conflict_details,
        "normalized_name": normalized_name
    }

    # LOG AUDIT (UPLOAD)
    log_audit(
        org_id=org_id,
        user_id=auth_user["id"],
        action="UPLOAD",
        res_name=filename_original,
        metadata={"scenario": scenario}
    )

    if scenario != "NEW":
        return {
            "task_id": task_id,
            "status": "conflict",
            "message": f"Conflict detected: {scenario}",
            "scenario": scenario,
            "conflict_details": conflict_details,
            "existing_id": existing_id,
            "version": existing_version
        }

    # If new, proceed normally
    if org_id:
        # 🪙 [TOKEN CONSUMPTION]
        print(f"🪙 Attempting to consume 1 token for Org: {org_id}")
        deducted = consume_credit(org_id, 1, f"Análisis de documento: {filename_original}")
        if not deducted:
            print(f"🚫 Insufficient credits for Org: {org_id}")
            raise HTTPException(
                status_code=402, 
                detail="Créditos insuficientes en su organización. Por favor recargue tokens en el Hub."
            )
        print(f"✅ Token consumed successfully for Org: {org_id}")
    else:
        # In strict SaaS mode, we should require org_id. 
        # For now, we'll allow but warn if it's missing (dev mode fallback).
        print("⚠️ Warning: Analysis starting without org_id. Credits not tracked.")

    background_tasks.add_task(run_analysis_task, task_id, file_path)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Analysis started."
    }

@app.post("/analyze/confirm")
async def confirm_analysis(
    req: AnalysisConfirmRequest,
    background_tasks: BackgroundTasks,
    auth_user: dict = Depends(verify_token)
):
    if req.task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[req.task_id]
    
    # SECURITY CHECK: Ensure user belongs to the task's organization
    if auth_user["organization_id"] and str(task.get("org_id")) != str(auth_user["organization_id"]):
         raise HTTPException(status_code=403, detail="No autorizado para confirmar este análisis.")
    if req.action == "cancel":
        if os.path.exists(task["file_path"]):
            os.remove(task["file_path"])
        del tasks_db[req.task_id]
        return {"status": "cancelled"}
    
    # Set choice and start background task
    task["status"] = "pending"
    task["analysis_mode"] = req.action  # 'full_analysis' or 'changes_only'
    
    # 🪙 [TOKEN CONSUMPTION ON CONFIRMATION]
    org_id = task.get("org_id")
    if org_id:
        concept = f"Re-Análisis ({req.action}): {task.get('filename')}"
        deducted = consume_credit(org_id, 1, concept)
        if not deducted:
            raise HTTPException(
                status_code=402, 
                detail="Créditos insuficientes para confirmar el análisis."
            )

    background_tasks.add_task(run_analysis_task, req.task_id, task["file_path"])
    
    return {
        "task_id": req.task_id,
        "status": "pending",
        "message": f"Analysis confirmed as {req.action}."
    }

@app.get("/analyze/{task_id}", response_model=AnalysisResult)
def get_analysis_status(task_id: str, auth_user: dict = Depends(verify_token)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]

    # SECURITY CHECK: Ensure user belongs to the task's organization
    if auth_user["organization_id"] and str(task.get("org_id")) != str(auth_user["organization_id"]):
         raise HTTPException(status_code=403, detail="No autorizado para ver el avance de este análisis.")
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "created_at": task["created_at"],
        "steps": task.get("steps", []),
        "current_step": task.get("current_step"),
        "current_detail": task.get("current_detail"),
        "is_duplicate": task.get("scenario") != "NEW" and task.get("scenario") is not None,
        "existing_doc_id": task.get("conflict_details", {}).get("id") if task.get("conflict_details") else None,
        "scenario": task.get("scenario")
    }
    
    if task["status"] == "completed":
        response["data"] = task["result"]
    elif task["status"] == "failed":
        response["error"] = task.get("error")
        
    return response

@app.get("/documents")
def list_documents(org_id: Optional[str] = None, auth_user: dict = Depends(verify_token)):
    """
    List documents using official 'ando_documents' table.
    Ensures users only see documents from their own organization.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")

    # SECURITY CHECK: Force filter by user's organization if provided, otherwise use theirs
    effective_org_id = auth_user["organization_id"]
    if org_id and str(org_id) != str(effective_org_id):
        raise HTTPException(status_code=403, detail="No tiene permisos para ver documentos de otra organización.")
        
    try:
        query = supabase.table("ando_documents").select("*")
        query = query.eq("organization_id", effective_org_id)
        
        # Optionally filter by parent_id IS NULL to show only families, 
        # but User prompt implies showing all recent versions in the list.
        # We'll just show active versions.
        query = query.eq("status", "active")
        query = query.order("updated_at", desc=True)
        
        res = query.execute()
        return res.data
    except Exception as e:
        print(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
            # Fallback for old data or edge case
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
        
        # --- PDF GENERATION LOGIC (Simplified from Streamlit) ---
        from fpdf import FPDF
        
        class ReportPDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 12)
                self.cell(0, 10, f'Reporte de Auditoría: {doc["file_name"]}', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

        pdf = ReportPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)

        # 1. Metadatos
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, "1. Información General", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 8, f"ID Documento: {doc['id']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Versión: {doc.get('current_version', '1')}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Fecha Análisis: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # 2. Resumen Ejecutivo (Hallazgos)
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, "2. Hallazgos Clave", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        
        hallazgos = payload.get("compliance_report", {}).get("conclusion", {}).get("hallazgos", [])
        if hallazgos:
            for h in hallazgos:
                pdf.multi_cell(0, 8, f"- {h}")
        else:
            pdf.cell(0, 8, "No se reportaron hallazgos específicos.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # 3. Riesgos
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, "3. Riesgos Detectados", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)

        riesgos = payload.get("compliance_report", {}).get("conclusion", {}).get("riesgos", [])
        if riesgos:
            for r in riesgos:
                pdf.multi_cell(0, 8, f"- {r}")
        else:
            pdf.cell(0, 8, "No se detectaron riesgos críticos.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Output to bytes
        pdf_bytes = pdf.output()
        
        return Response(
            content=bytes(pdf_bytes),
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
