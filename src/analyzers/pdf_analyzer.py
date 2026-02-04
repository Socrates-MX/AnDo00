import pypdf
import re

def analyze_pdf(file_path, progress_callback=None):
    """
    Analyzes a PDF file to extract text and basic metadata.
    Returns a list of page objects.
    """
    results = []
    try:
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            if progress_callback:
                progress_callback(i + 1, num_pages)

            text = page.extract_text() or ""
            
            # Annotation Extraction (Electronic Signatures / Stamps)
            annots_found = []
            annot_text = ""
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    obj = annot.get_object()
                    content = obj.get("/Contents")
                    user_title = obj.get("/T")
                    
                    if content or user_title:
                        # Extraer de Appearance Streams (común en sellos electrónicos)
                        detail = ""
                        if "/AP" in obj:
                            ap = obj["/AP"]
                            if "/N" in ap:
                                appearance = ap["/N"].get_object()
                                if hasattr(appearance, "extract_text"):
                                    detail = appearance.extract_text() or ""
                        
                        annots_found.append({
                            "content": str(content) if content else "",
                            "user": str(user_title) if user_title else "",
                            "detail": detail.strip()
                        })
                        
                        # Mantener texto para compatibilidad con prompt de IA
                        if content: annot_text += f"\n[Annot]: {content}"
                        if detail: annot_text += f" (Detail: {detail.strip()})"
                        if user_title: annot_text += f" (User: {user_title})"
            
            full_text = text + annot_text

            # --- STRUCTURAL HEURISTICS (Page-by-Page) ---
            structure_data = {
                "titles_detected": [],
                "footer_validation": {"valid": True, "issues": []},
                "has_images": len(page.images) > 0
            }

            # 1. Title Detection (Simple Uppercase Heuristic)
            lines = full_text.split('\n')
            for line in lines[:10]: # Check header area
                clean_line = line.strip()
                if clean_line.isupper() and len(clean_line) > 5 and len(clean_line) < 100:
                    structure_data["titles_detected"].append(clean_line)
            
            # 2. Integrity Check (Page X of Y)
            # Regex for "Página X de Y", "Page X of Y", "X / Y"
            pg_match = re.search(r"(?:P[áa]gina|Page)\s*(\d+)\s*(?:de|of|\/)\s*(\d+)", full_text, re.IGNORECASE)
            if pg_match:
                try:
                    pg_current = int(pg_match.group(1))
                    pg_total = int(pg_match.group(2))
                    
                    if pg_current != (i + 1):
                        structure_data["footer_validation"]["valid"] = False
                        structure_data["footer_validation"]["issues"].append(f"Num. Pág. no coincide (Texto: {pg_current} vs Real: {i+1})")
                    
                    if pg_total != num_pages:
                        structure_data["footer_validation"]["valid"] = False
                        structure_data["footer_validation"]["issues"].append(f"Total Páginas no coincide (Texto: {pg_total} vs Real: {num_pages})")
                except:
                    pass
            
            # Image Extraction Logic (Existing)
            images_found = []
            if len(page.images) > 0:
                for img in page.images:
                    images_found.append({
                        "name": img.name,
                        "data_size": len(img.data),
                        "image_bytes": img.data,
                        "description": "[Pendiente de análisis]" 
                    })
            
            page_card = {
                "page_number": i + 1,
                "text_content": full_text,
                "token_count_est": len(full_text.split()),
                "images": images_found,
                "annots": annots_found,
                "structure": structure_data
            }
            results.append(page_card)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    # Extraer metadatos extendidos y estado de encriptación
    meta_dict = {}
    if reader.metadata:
        meta_dict = {k.replace("/", ""): v for k, v in reader.metadata.items()}
    
    # Agregar estado de seguridad
    meta_dict["is_encrypted"] = reader.is_encrypted
    
    return results, meta_dict
