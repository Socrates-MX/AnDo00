
import os
import sys
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def dump_text():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    pages_data, meta = pdf_analyzer.analyze_pdf(target_path)
    
    for i, p in enumerate(pages_data):
        print(f"--- PÁGINA {i+1} ---")
        print(p['text_content'])
        if i >= 1: break # Just first 2 pages

if __name__ == "__main__":
    dump_text()
