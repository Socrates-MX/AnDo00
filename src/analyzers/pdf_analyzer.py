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
            annot_text = ""
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    obj = annot.get_object()
                    # Capturamos contenidos de notas, sellos y campos de texto libre
                    content = obj.get("/Contents")
                    if content:
                        annot_text += f"\n[Annot]: {content}"
                    
                    # Extraer de Appearance Streams (común en sellos electrónicos)
                    if "/AP" in obj:
                        ap = obj["/AP"]
                        if "/N" in ap:
                            appearance = ap["/N"].get_object()
                            if hasattr(appearance, "extract_text"):
                                ap_text = appearance.extract_text()
                                if ap_text:
                                    annot_text += f" (Detail: {ap_text.strip()})"
                    
                    # Título del anotador (usualmente el usuario que firmó)
                    title = obj.get("/T")
                    if title:
                        annot_text += f" (User: {title})"
            
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
                "images": images_found
            }
            results.append(page_card)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    return results
