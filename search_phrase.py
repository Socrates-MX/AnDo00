
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def search_phrase():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    pages_data, meta = pdf_analyzer.analyze_pdf(target_path)
    
    for i, p in enumerate(pages_data):
        content = p['text_content']
        if "REVISADO" in content.upper() and "APROBADO" in content.upper():
            print(f"--- MATCH EN PÁGINA {i+1} ---")
            print(content)
            
        # Also check for the specific term "REVISADO Y APROBADO ELECTRÓNICAMENTE"
        if "REVISADO Y APROBADO ELECTRÓNICAMENTE" in content.upper():
            print(f"--- MATCH EXACTO EN PÁGINA {i+1} ---")

if __name__ == "__main__":
    search_phrase()
