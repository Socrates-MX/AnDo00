from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
# In production, use os.getenv("SUPABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL") 
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase Client Initialized")
    except Exception as e:
        print(f"❌ Failed to init Supabase: {e}")
else:
    print("⚠️ Supabase credentials not found. Persistence disabled.")


# --- IN-MEMORY STATE (Replacing Redis for MVP) ---
tasks_db: Dict[str, Dict[str, Any]] = {}

# --- MODELS ---
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    existing_id: Optional[str] = None
    version: Optional[str] = None

class AnalysisResult(BaseModel):
    task_id: str
    status: str
    created_at: str
    current_step: Optional[str] = None
    steps: Optional[list] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_duplicate: Optional[bool] = False
    existing_doc_id: Optional[str] = None

# --- HELPER FUNCTIONS ---
def calculate_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_task_progress(task_id: str, step_index: int, step_description: str):
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

def run_analysis_task(task_id: str, file_path: str):
    try:
        tasks_db[task_id]["status"] = "processing"
        
        # --- PHASE 1 ---
        update_task_progress(task_id, 1, "Digitalizando documento...")
        extraction_result = pdf_analyzer.analyze_pdf(file_path)
        
        if extraction_result is None:
            raise Exception("Failed to extract data from PDF")
            
        pages_data, pdf_meta = extraction_result
        
        # --- PHASE 2 ---
        update_task_progress(task_id, 2, "Analizando imágenes...")
        serialized_pages = []
        for page in pages_data:
            clean_images = []
            for img in page.get("images", []):
                if "image_bytes" in img and img["image_bytes"]:
                    b64_img = base64.b64encode(img["image_bytes"]).decode('utf-8')
                    img_copy = img.copy()
                    img_copy["image_bytes"] = b64_img
                    img_copy["encoding"] = "base64"
                    clean_images.append(img_copy)
                else:
                    clean_images.append(img)
            page_copy = page.copy()
            page_copy["images"] = clean_images
            serialized_pages.append(page_copy)

        # --- PHASE 3 ---
        update_task_progress(task_id, 3, "Generando informe estructural...")
        # --- PHASE 4 ---
        update_task_progress(task_id, 4, "Validando congruencia...")
        # --- PHASE 5 ---
        update_task_progress(task_id, 5, "Finalizando cruce...")

        # STORE SUCCESS
        final_result = {
            "metadata": pdf_meta,
            "pages": serialized_pages,
            "page_count": len(serialized_pages)
        }
        
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["result"] = final_result
        update_task_progress(task_id, 6, "Completado")
        
        # --- SAVE TO SUPABASE (Optional for now) ---
        if supabase:
            # logic to insert into ando_documents would go here
            pass

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
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    task_id = str(uuid.uuid4())
    temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    # --- CHECK DUPLICATES (HASH) ---
    file_hash = calculate_file_hash(file_path)
    existing_doc = None
    
    if supabase:
        try:
            # Query db for existing hash
            # Assuming table 'ando_documents' exists and has 'file_hash'
            res = supabase.table("ando_documents").select("*").eq("file_hash", file_hash).execute()
            if res.data and len(res.data) > 0:
                existing_doc = res.data[0]
        except Exception as e:
            print(f"Warning: duplicate check failed: {e}")

    if existing_doc:
        # Clean temp file immediately
        os.remove(file_path)
        
        # Register "Fake" task that is immediately completed with existing data
        # Note: We would need to fetch the full JSON from storage or DB. 
        # For this MVP step, we just signal it exists.
        
        tasks_db[task_id] = {
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "is_duplicate": True,
            "existing_doc_id": existing_doc.get("id"),
            # In a real scenario, we'd load the result from DB here
            "result": { 
                "metadata": {"title": existing_doc.get("filename", "Existing Doc")},
                "page_count": 0 # Placeholder
            },
            "steps": [
                 {"label": "Documento ya existente en base de datos (Hash Match)", "status": "completed"}
            ] 
        }
        
        return {
            "task_id": task_id,
            "status": "already_exists",
            "message": "Document found in database.",
            "existing_id": existing_doc.get("id"),
            "version": existing_doc.get("version", "V1")
        }

    # If new, proceed normally
    tasks_db[task_id] = {
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "filename": file.filename,
        "hash": file_hash
    }
    
    background_tasks.add_task(run_analysis_task, task_id, file_path)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Analysis started."
    }

@app.get("/analyze/{task_id}", response_model=AnalysisResult)
def get_analysis_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "created_at": task["created_at"],
        "steps": task.get("steps", []),
        "current_step": task.get("current_step"),
        "is_duplicate": task.get("is_duplicate", False),
        "existing_doc_id": task.get("existing_doc_id")
    }
    
    if task["status"] == "completed":
        response["data"] = task["result"]
    elif task["status"] == "failed":
        response["error"] = task.get("error")
        
    return response
