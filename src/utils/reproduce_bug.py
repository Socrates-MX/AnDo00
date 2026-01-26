import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'src'))
from analyzers import pdf_analyzer, detailed_analyzer, image_analyzer

load_dotenv()

def reproduce():
    pdf_path = "data/archivo_maestro.pdf"
    print(f"Reproduciendo con: {pdf_path}")
    
    # 1. Análisis Inicial
    pages_data = pdf_analyzer.analyze_pdf(pdf_path)
    
    # Simular lo que hace app.py (llenar descripciones de imágenes)
    for page in pages_data:
        for img in page.get('images', []):
            img['description'] = image_analyzer.generate_image_description(img['image_bytes'])
            print(f"Pág {page['page_number']} - Imagen {img['name']}: {img['description']}")

    # 2. Análisis Detallado (Pass pdf_path for multimodal fix)
    result_json = detailed_analyzer.extract_detailed_analysis(pages_data, pdf_path)
    
    print("\n--- RESULTADO DETALLADO (REVISADO Y APROBADO) ---")
    try:
        data = json.loads(result_json)
        revisado = data.get("revisado_aprobado", [])
        for row in revisado:
            print(row)
    except Exception as e:
        print(f"Error parseando JSON: {e}")
        print(result_json)

if __name__ == "__main__":
    reproduce()
