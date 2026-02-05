
import os
import sys
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def dump_page_9():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    pages_data, meta = pdf_analyzer.analyze_pdf(target_path)
    if len(pages_data) >= 9:
        print(f"--- PÁGINA 9 ---")
        print(pages_data[8]['text_content'])
    else:
        print(f"Documento solo tiene {len(pages_data)} páginas.")

if __name__ == "__main__":
    dump_page_9()
