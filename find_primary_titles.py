
import os
import sys
import re

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def find_primary_numbered_titles():
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

    # Regex logic: 
    # ^[ \t]* -> start of line with optional whitespace
    # (\d+)\. -> digit(s) followed by exactly one dot
    # (?!\d) -> NOT followed by another digit (this avoids 1.1)
    # [ \t]+ -> followed by whitespace
    # (.*) -> the rest of the title
    pattern = r'^[ \t]*(\d+)\.[ \t]+(?![\d])(.*)$'
    
    matches = re.findall(pattern, full_text, re.MULTILINE)
    
    results = []
    for m in matches:
        num, title = m
        results.append(f"{num}. {title.strip()}")
            
    print("\n--- TÍTULOS NUMERADOS PRIMARIOS DETECTADOS (RAW) ---")
    if not results:
        print("No se encontraron títulos con el formato 'X.' (sin sub-números)")
    else:
        # Deduplicate and sort
        for r in sorted(list(set(results)), key=lambda x: int(x.split('.')[0])):
            print(f"- {r}")

if __name__ == "__main__":
    find_primary_numbered_titles()
