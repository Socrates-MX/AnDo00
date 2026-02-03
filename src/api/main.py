import shutil
import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Import Analyzers
from analyzers import (
    pdf_analyzer,
    image_analyzer,
    detailed_analyzer,
    congruence_analyzer,
    process_cross_analyzer,
    index_analyzer
)
from generators import pdf_report_generator, report_generator
from persistence import document_manager
from utils.supabase_client import get_supabase_client

app = FastAPI(title="AnDo Headless API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY TASK STORE ---
TASKS: Dict[str, Dict[str, Any]] = {}

# --- MODELS ---
class TaskResponse(BaseModel):
    task_id: str
    status: str
    existing_id: Optional[str] = None
    version: Optional[int] = None
    message: Optional[str] = None

# --- BACKGROUND WORKER ---
def run_analysis_task(task_id: str, file_path: str, org_id: Optional[str] = None):
    try:
        TASKS[task_id]["status"] = "processing"
        TASKS[task_id]["steps"] = []
        
        def update_step(label, status, detail=""):
            TASKS[task_id]["steps"].append({
                "label": label, 
                "status": status, 
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            })

        # 1. OCR & Extraction
        update_step("Fase 1/5: Digitalizando documento y extrayendo texto (OCR)...", "processing")
        pages_data = pdf_analyzer.analyze_pdf(file_path)
        
        if not pages_data:
            raise Exception("No se pudo extraer contenido del PDF.")
        
        update_step("Fase 1/5: Digitalizando documento y extrayendo texto (OCR)...", "completed")

        # 2. Image Analysis
        update_step("Fase 2/5: Analizando elementos visuales e imágenes...", "processing")
        for page in pages_data:
            # Text Interpretation
            page['text_interpret'] = image_analyzer.generate_text_interpretation(page['text_content'])
            
            # Image Description
            for img in page.get('images', []):
                img['description'] = image_analyzer.generate_image_description(img['image_bytes'])
        
        update_step("Fase 2/5: Analizando elementos visuales e imágenes...", "completed")

        # 3. Structural Analysis
        update_step("Fase 3/5: Generando Informe Estructural...", "processing")
        detailed_json_raw = detailed_analyzer.extract_detailed_analysis(pages_data, file_path)
        try:
            detailed_report = json.loads(detailed_json_raw)
        except:
            detailed_report = {"error": "Failed to parse detailed analysis JSON", "raw": detailed_json_raw}
        
        update_step("Fase 3/5: Generando Informe Estructural...", "completed")

        # 4. Index & Congruence
        update_step("Fase 4/5: Construyendo Índice Lógico...", "processing")
        index_card = report_generator.generate_index_card(pages_data)
        congruence_report = congruence_analyzer.analyze_document_congruence(detailed_report, pages_data)
        update_step("Fase 4/5: Construyendo Índice Lógico...", "completed")

        # 5. Process Cross
        update_step("Fase 5/5: Ejecutando Cruce Diagrama vs Procedimientos...", "processing")
        process_cross_report = process_cross_analyzer.analyze_process_crossing(detailed_report, pages_data)
        update_step("Fase 5/5: Ejecutando Cruce Diagrama vs Procedimientos...", "completed")

        # RAW REPORT (Extra)
        raw_congruence_report = {
             "raw_matriz_02": [], # Placeholder, logic could be moved here if needed
             "raw_desviaciones": []
        }

        # 6. PERSISTENCE (Supabase)
        doc_db_id = None
        supabase = get_supabase_client()
        if supabase:
            # Prepare payload
            full_payload = {
                "pages_data": filter_bytes_for_json(pages_data), # Remove bytes
                "detailed_report": detailed_report,
                "congruence_report": congruence_report,
                "process_cross_report": process_cross_report,
                "index_card": index_card,
                "metadata": {
                    "Author": "AI Extracted",
                    "is_encrypted": False,
                    "title": os.path.basename(file_path)
                }
            }
            
            # Insert Logic
            # Check hash again just in case
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            file_hash = document_manager.calculate_pdf_hash(file_bytes)
            
            doc_data = {
                "nombre_archivo": os.path.basename(file_path),
                "hash_documento": file_hash,
                "numero_paginas": len(pages_data),
                "estado": "analizado",
                "version_actual": 1,
                "payload_completo": full_payload,
                # "org_id": org_id # If table supports it
            }
            
            # Use document_manager to save
            try:
                # We need to adapt save_new_document to accept payload directly if possible
                # Or just call INSERT directly here
                res = supabase.table("ando_documents").insert(doc_data).execute()
                if res.data:
                    doc_db_id = res.data[0]['id']
            except Exception as e:
                print(f"Persistence Error: {e}")

        # Final Result
        TASKS[task_id]["data"] = {
            "page_count": len(pages_data),
            "pages": filter_bytes_for_json(pages_data),
            "detailed_report": detailed_report,
            "congruence_report": congruence_report,
            "process_cross_report": process_cross_report,
            "index_card": index_card,
            "raw_congruence_report": raw_congruence_report,
            "document_db_id": doc_db_id
        }
        TASKS[task_id]["status"] = "completed"

    except Exception as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["error"] = str(e)
        import traceback
        traceback.print_exc()

def filter_bytes_for_json(pages_data):
    # Deep copy to avoid modifying original if still needed
    import copy
    clean_data = copy.deepcopy(pages_data)
    for page in clean_data:
        for img in page.get('images', []):
            if 'image_bytes' in img:
                del img['image_bytes']
            if 'data' in img: # sometimes pypdf uses this
                del img['data']
    return clean_data

# --- ENDPOINTS ---

@app.post("/analyze/upload")
async def analyze_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    org_id: Optional[str] = Form(None)
):
    # 1. Save File
    temp_dir = "data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2. Check Duplicate
    with open(file_path, "rb") as f:
        content = f.read()
    
    file_hash = document_manager.calculate_pdf_hash(content)
    existing = document_manager.check_document_existence(file_hash)
    
    if existing:
        # Return special status so UI can handle it
        # We also start a "dummy" task that returns the existing data immediately? 
        # Or just tell frontend "Already Exists" and give ID.
        return {
            "status": "already_exists",
            "existing_id": existing['id'],
            "version": existing['version_actual'],
            "task_id": "EXISTING_" + existing['id']
        }

    # 3. Create Task
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "pending", 
        "created_at": datetime.now().isoformat()
    }

    background_tasks.add_task(run_analysis_task, task_id, file_path, org_id)

    return {"task_id": task_id, "status": "queued"}

@app.get("/analyze/{task_id}")
async def get_analysis_status(task_id: str):
    # Special Handling for EXISTING
    if task_id.startswith("EXISTING_"):
        real_id = task_id.replace("EXISTING_", "")
        # Fetch from DB
        doc = document_manager.get_latest_analysis(real_id)
        if doc:
            return {
                "status": "completed",
                "is_duplicate": True,
                "existing_doc_id": real_id,
                "data": doc.get("payload_completo", {})
            }
        else:
            return {"status": "failed", "error": "Document not found in DB"}

    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TASKS[task_id]

@app.get("/documents")
async def list_documents(org_id: Optional[str] = None):
    supabase = get_supabase_client()
    if not supabase:
        return []
    
    query = supabase.table("ando_documents").select("*").order("created_at", desc=True)
    # if org_id: query = query.eq("org_id", org_id) # enable when column exists
    
    res = query.execute()
    return res.data

@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="DB not configured")
        
    res = supabase.table("ando_documents").select("*").eq("id", doc_id).single().execute()
    if not res.data:
         raise HTTPException(status_code=404, detail="Document not found")
         
    return {
        "id": res.data['id'],
        "page_count": res.data['numero_paginas'],
        "data": res.data.get('payload_completo')
    }

@app.get("/documents/{doc_id}/report")
async def get_document_report(doc_id: str):
    # Fetch data
    supabase = get_supabase_client()
    res = supabase.table("ando_documents").select("payload_completo, nombre_archivo").eq("id", doc_id).single().execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Document not found")
        
    payload = res.data['payload_completo']
    filename = res.data['nombre_archivo']
    
    # Generate PDF
    pdf_bytes = pdf_report_generator.create_full_report_pdf(payload)
    
    # Return Stream
    from io import BytesIO
    return StreamingResponse(
        BytesIO(pdf_bytes), 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Reporte_{filename}.pdf"}
    )

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(500, "DB Error")
    
    supabase.table("ando_documents").delete().eq("id", doc_id).execute()
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
