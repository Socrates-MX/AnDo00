import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer

def debug_text_with_annots():
    pdf_path = "data/archivo_maestro.pdf"
    pages = pdf_analyzer.analyze_pdf(pdf_path)
    print(f"--- TEXT CONTENT PAGE 1 ---")
    print(pages[0]['text_content'])

if __name__ == "__main__":
    debug_text_with_annots()
