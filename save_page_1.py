
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def save_page_1():
    file_name = "TRA-P-01 Administración de Proveedores Estratégicos de Combustible Fase I.pdf"
    target_path = None
    for f in os.listdir("temp_uploads"):
        if file_name in f:
            target_path = os.path.join("temp_uploads", f)
            break
    if not target_path: return

    res, meta = pdf_analyzer.analyze_pdf(target_path)
    with open("page_1_raw.txt", "w", encoding="utf-8") as f:
        f.write(res[0]['text_content'])

if __name__ == "__main__":
    save_page_1()
