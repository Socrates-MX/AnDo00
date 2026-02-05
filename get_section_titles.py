
import os
import sys
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def get_section_titles():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    pages_data, meta = pdf_analyzer.analyze_pdf(target_path)
    
    full_text = ""
    for p in pages_data:
        full_text += p['text_content'] + "\n"

    # Common section titles in uppercase
    import re
    # Look for lines that are primarily uppercase and stand alone
    titles = re.findall(r'^[ \t]*([A-ZÁÉÍÓÚ\s]{4,})[ \t]*$', full_text, re.MULTILINE)
    
    # Filter out common headers/footers
    ignore = ["GRUPO ENERSER", "PÁGINA", "DE", "ESTE DOCUMENTO", "TEXTO", "DOCUMENTO", "REVISIÓN", "FECHA", "TIPO"]
    clean_titles = []
    for t in titles:
        t = t.strip()
        if len(t) > 3 and not any(ign in t for ign in ignore):
            clean_titles.append(t)
            
    print("\n--- TÍTULOS DE SECCIÓN DETECTADOS (RAW) ---")
    for t in sorted(list(set(clean_titles))):
        print(f"- {t}")

if __name__ == "__main__":
    get_section_titles()
