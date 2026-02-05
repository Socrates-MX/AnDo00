
import os
import sys
import re

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def find_primary_titles_with_pages():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    pages_data, meta = pdf_analyzer.analyze_pdf(target_path)
    
    # Regex logic for primary titles (X.)
    pattern = r'^[ \t]*(\d+)\.[ \t]+(?![\d])(.*)$'
    
    results = []
    
    for page in pages_data:
        text = page['text_content']
        matches = re.findall(pattern, text, re.MULTILINE)
        for m in matches:
            num, title = m
            results.append({
                "line": f"{num}. {title.strip()}",
                "page": page['page_number']
            })
            
    print("\n--- UBICACIÓN DE TÍTULOS PRIMARIOS (RAW) ---")
    if not results:
        print("No se encontraron títulos.")
    else:
        # Show in order
        for item in results:
            print(f"- {item['line']} (Página {item['page']})")

if __name__ == "__main__":
    find_primary_titles_with_pages()
