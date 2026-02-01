import pypdf

def analyze_pdf(file_path):
    """
    Analyzes a PDF file to extract text and basic metadata.
    Returns a list of page objects.
    """
    results = []
    try:
        reader = pypdf.PdfReader(file_path)
        num_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
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

            # Image Extraction Logic
            images_found = []
            if len(page.images) > 0:
                for img in page.images:
                    images_found.append({
                        "name": img.name,
                        "data_size": len(img.data),
                        "image_bytes": img.data,
                        "description": "[Pendiente de análisis IA]" 
                    })
            
            page_card = {
                "page_number": i + 1,
                "text_content": full_text,
                "token_count_est": len(full_text.split()),
                "images": images_found,
                "annots": annots_found
            }
            results.append(page_card)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    return results
