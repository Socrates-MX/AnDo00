import os
import json
from datetime import datetime
from typing import Dict, Any
from core.supabase_client import supabase

# In-memory state
tasks_db: Dict[str, Dict[str, Any]] = {}

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
        if detail and 0 <= step_index - 1 < len(tasks_db[task_id]["steps"]):
             tasks_db[task_id]["steps"][step_index - 1]["detail"] = detail
             tasks_db[task_id]["current_detail"] = detail

def consume_credit(org_id: str, amount: int, concept: str) -> bool:
    if not supabase or not org_id: return True
    try:
        res = supabase.rpc("consume_tokens", {
            "p_org_id": org_id, "p_amount": amount, "p_app": "ANDO", "p_concept": concept
        }).execute()
        return res.data is True
    except Exception as e:
        print(f"❌ Error credit consumption: {e}")
        return False

def log_audit(org_id: str, user_id: str, action: str, doc_id: str = None, res_name: str = None, metadata: dict = {}):
    if not supabase: return
    try:
        supabase.rpc("log_action_system", {
            "p_org_id": org_id, "p_user_id": user_id, "p_action": action,
            "p_app": "ANDO", "p_doc_id": doc_id, "p_res_name": res_name, "p_metadata": metadata
        }).execute()
    except Exception as e:
        print(f"⚠️ Audit Log failed: {e}")

async def run_analysis_task(task_id: str, file_path: str):
    # This involves heavy imports from ..src.
    # To avoid circular imports or issues, we can keep the logic here but call it from main.
    # Actually, it's better to keep it here.
    from analyzers import pdf_analyzer, detailed_analyzer, congruence_analyzer, process_cross_analyzer, image_analyzer
    from generators import report_generator
    
    try:
        tasks_db[task_id]["status"] = "processing"
        
        # Phase 1
        config = tasks_db[task_id].get("config", {})
        def p1_prog(c, t): update_task_progress(task_id, 1, "Digitalizando...", detail=f"Pág {c} de {t}...")
        extraction_result = pdf_analyzer.analyze_pdf(file_path, progress_callback=p1_prog, config=config)
        if not extraction_result: raise Exception("Failed extraction")
        pages_data, pdf_meta = extraction_result
        
        # Phase 2: Images
        serialized_pages = []
        for p in pages_data:
            clean_imgs = []
            for i_idx, img in enumerate(p.get("images", [])):
                if "image_bytes" in img and img["image_bytes"]:
                    update_task_progress(task_id, 2, "Imágenes...", detail=f"Pág {p['page_number']}: Imagen {i_idx+1}")
                    desc, _ = image_analyzer.generate_image_description(img["image_bytes"])
                else: desc = "[No data]"
                img_copy = img.copy(); img_copy["description"] = desc; img_copy.pop("image_bytes", None)
                clean_imgs.append(img_copy)
            pc = p.copy(); pc["images"] = clean_imgs; serialized_pages.append(pc)
        pages_data = serialized_pages

        # Phase 3: Detailed
        update_task_progress(task_id, 3, "Informe estructural...")
        detailed_json_raw, detailed_usage = detailed_analyzer.extract_detailed_analysis(pages_data, file_path=file_path)
        print(f"RAW DETAILED JSON OUTPUT: {repr(detailed_json_raw)}")
        detailed_report = json.loads(detailed_json_raw)
        # Phase 4 & 5 (Omitidos en Vercel por timeout, delegado a ARC00)
        update_task_progress(task_id, 4, "Finalizando Extracción (Omitiendo Cruces en Vercel)...")
        congruence_report = {}
        process_cross_report = {}
        index_card = {}
        
        # Token usage aggregation
        total_tokens = detailed_usage.get("total_token_count", 0) if detailed_usage else 0
        usage_stats = {
            "total_tokens": total_tokens
        }

        # Result construction
        final_result = {
            "metadata": pdf_meta, "pages": serialized_pages, "detailed_report": detailed_report,
            "congruence_report": congruence_report, "process_cross_report": process_cross_report,
            "index_card": index_card, "page_count": len(serialized_pages),
            "usage_stats": usage_stats
        }

        # PERSISTENCE (Supabase)
        doc_db_id = None
        if supabase:
            try:
                org_id = tasks_db[task_id].get("org_id")
                filename = tasks_db[task_id].get("filename")
                file_hash = tasks_db[task_id].get("hash")
                
                # 1. Upsert ando_documents
                doc_data = {
                    "organization_id": org_id,
                    "file_name": filename,
                    "file_hash": file_hash,
                    "page_count": len(serialized_pages),
                    "status": "extracted"
                }
                res_doc = supabase.table("ando_documents").upsert(doc_data, on_conflict="file_hash").execute()
                
                if res_doc.data:
                    doc_db_id = res_doc.data[0]['id']
                    
                    # 2. Insert payload into ando_analysis_versions
                    version_data = {
                        "document_id": doc_db_id,
                        "version_number": 1,
                        "full_analysis_payload": final_result
                    }
                    supabase.table("ando_analysis_versions").insert(version_data).execute()
                    
            except Exception as e:
                print(f"Supabase Insert Error: {e}")

        final_result["document_db_id"] = doc_db_id
        tasks_db[task_id]["result"] = final_result
        tasks_db[task_id]["status"] = "completed"
        update_task_progress(task_id, 6, "Completado")

    except Exception as e:
        print(f"🚨 Background Task Error: {e}")
        import traceback
        traceback.print_exc()
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
    finally:
        if os.path.exists(file_path): os.remove(file_path)
