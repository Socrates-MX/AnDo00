
import os
import sys
import json

# Set up paths
sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def get_titles_from_raw():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    
    if not target_path:
        print(f"File {file_name} not found in temp_uploads")
        return

    # print(f"Analizando {target_path}...")
    
    # scan for raw files
    pdf_res = pdf_analyzer.analyze_pdf(target_path)
    if not pdf_res:
        print("Error in OCR")
        return
        
    pages_data, meta = pdf_res

    titles = []
    for page in pages_data:
        content = page['text_content'].strip()
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if lines:
            titles.append({
                "pagina": page['page_number'],
                "titulo": lines[0]
            })

    print("\n--- TÍTULOS IDENTIFICADOS EN CONSOLIDACIÓN RAW ---")
    for t in titles:
        print(f"Página {t['pagina']}: {t['titulo']}")

if __name__ == "__main__":
    get_titles_from_raw()
