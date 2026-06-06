from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form, Response, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os, uuid, shutil, json
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Local Core Imports
# Add src to path so we can import from ..src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.supabase_client import supabase
from core.auth import verify_token
from core.utils import check_rate_limit, calculate_file_hash, normalize_filename
from core.tasks import tasks_db, run_analysis_task, consume_credit, log_audit

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

@app.get("/")
def read_root(): return {"status": "online", "service": "AnDo API"}

@app.post("/analyze/upload", response_model=TaskResponse)
async def upload_document(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    org_id: Optional[str] = Form(None),
    auth_user: dict = Depends(verify_token)
):
    if org_id: check_rate_limit(org_id)
    if auth_user["organization_id"] and org_id != str(auth_user["organization_id"]):
        raise HTTPException(status_code=403, detail="No autorizado.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo PDF.")
    
    task_id = str(uuid.uuid4())
    temp_dir = '/tmp'
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # --- Control de Páginas y Facturación Dinámica ---
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
        if num_pages > 20:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="El documento excede el límite permitido de 20 páginas por razones de rentabilidad y seguridad.")
        
        token_cost = 3 if num_pages > 10 else 1
        warning_msg = "Procesando. (Aviso: Documento >10 págs, consume 3 tokens)." if num_pages > 10 else "Procesando"
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Error al validar estructura del PDF.")
    # -------------------------------------------------
    
    file_hash = calculate_file_hash(file_path)
    scenario = "NEW"
    conflict_details = None
    
    if supabase and org_id:
        docs = supabase.table("ando_documents").select("*").eq("organization_id", org_id).eq("file_hash", file_hash).execute().data
        if docs:
            scenario = "MATCH"
            conflict_details = docs[0]

    tasks_db[task_id] = {
        "status": "pending_decision" if scenario != "NEW" else "pending",
        "filename": file.filename, "hash": file_hash, "org_id": org_id,
        "user_id": auth_user["id"], "file_path": file_path, "scenario": scenario,
        "created_at": datetime.now().isoformat()
    }

    if scenario == "NEW" and org_id:
        if not consume_credit(org_id, token_cost, f"Análisis ({num_pages} págs): {file.filename}"):
            raise HTTPException(status_code=402, detail="Créditos insuficientes.")
        await run_analysis_task(task_id, file_path)
    
    return {
        "task_id": task_id, 
        "status": tasks_db[task_id]["status"], 
        "message": warning_msg if scenario == "NEW" else "Procesando", 
        "scenario": scenario,
        "existing_id": conflict_details["id"] if conflict_details else None,
        "version": conflict_details["current_version"] if conflict_details else None,
        "conflict_details": conflict_details,
        "data": tasks_db[task_id].get("result")
    }

@app.post("/analyze/confirm")
async def confirm_analysis(req: AnalysisConfirmRequest, org_id: Optional[str] = Form(None)):
    task_id = req.task_id
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if req.action == "cancel":
        tasks_db[task_id]["status"] = "cancelled"
        return {"status": "cancelled"}
    
    if req.action == "full_analysis":
        tasks_db[task_id]["status"] = "processing"
        file_path = tasks_db[task_id]["file_path"]
        await run_analysis_task(task_id, file_path)
        return {
            "task_id": task_id,
            "status": tasks_db[task_id]["status"],
            "data": tasks_db[task_id].get("result")
        }
    
    return {"status": "unknown_action"}

@app.get("/analyze/{task_id}")
def get_status(task_id: str, auth_user: dict = Depends(verify_token)):
    if task_id not in tasks_db: raise HTTPException(status_code=404)
    task = tasks_db[task_id]
    return {"task_id": task_id, "status": task["status"], "data": task.get("result") if task["status"] == "completed" else None}

@app.get("/documents")
def list_docs(auth_user: dict = Depends(verify_token)):
    if not supabase: return []
    return supabase.table("ando_documents").select("*").eq("organization_id", auth_user["organization_id"]).order("updated_at", desc=True).execute().data

# ... more endpoints can be moved to routers ...
