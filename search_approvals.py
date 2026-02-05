
import os
import sys
import json

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def extract_approvals():
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
        full_text += f"\n--- PÁGINA {p['page_number']} ---\n"
        full_text += p['text_content']

    # Search specifically for the approval section
    # Look for keywords: "REVISADO", "APROBADO", "FIRMA", "PUESTO"
    print("\n--- BÚSQUEDA DE BLOQUE DE APROBACIÓN ---")
    
    # We'll look for the last pages usually
    approval_found = False
    for p in reversed(pages_data):
        content = p['text_content']
        if "REVISADO" in content.upper() or "APROBADO" in content.upper() or "FECHA" in content.upper():
             print(f"Posible bloque en Página {p['page_number']}:")
             print(content[-1000:]) # Show tail of page
             approval_found = True
             break
    
    if not approval_found:
        print("No se detectó el encabezado explícito en el texto OCR.")

if __name__ == "__main__":
    extract_approvals()
