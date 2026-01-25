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
            text = page.extract_text()
            
            # Image Extraction Logic
            images_found = []
            if len(page.images) > 0:
                for img in page.images:
                    # img.data contains bytes, img.name contains filename
                    images_found.append({
                        "name": img.name,
                        "data_size": len(img.data),
                        "description": "[Pendiente de análisis IA]" # Will be updated by main or image_analyzer
                    })
            
            page_card = {
                "page_number": i + 1,
                "text_content": text,
                "token_count_est": len(text.split()),
                "images": images_found
            }
            results.append(page_card)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    return results
