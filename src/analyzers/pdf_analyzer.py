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
            # Placeholder for image extraction logic
            
            page_card = {
                "page_number": i + 1,
                "text_content": text,
                "token_count_est": len(text.split()),
                "images": [] # To be filled by image analyzer
            }
            results.append(page_card)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    return results
