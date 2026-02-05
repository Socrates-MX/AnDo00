
import os
import sys
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def inspect_raw_text():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    
    if not target_path: return

    pdf_res = pdf_analyzer.analyze_pdf(target_path)
    pages_data, meta = pdf_res

    print("--- PÁGINA 1 PRIMERAS 20 LÍNEAS ---")
    content = pages_data[0]['text_content']
    lines = content.split('\n')
    for i, line in enumerate(lines[:20]):
        print(f"{i}: {line}")

if __name__ == "__main__":
    inspect_raw_text()
