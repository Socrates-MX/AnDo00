import sys
import os
import json
from dotenv import load_dotenv
from utils import history
from analyzers import pdf_analyzer

load_dotenv()

def main(pdf_path):
    print(f"--- Iniciando Sistema AnDo ---")
    print(f"Procesando archivo: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print("Error: El archivo no existe.")
        return

    # 1. Registro / Carga Historial
    doc_info, is_new = history.register_document(pdf_path)
    if is_new:
        print(f"Documento NUEVO registrado: {doc_info['id']}")
    else:
        print(f"Documento PREVIO detectado: {doc_info['id']}")
        print("Cargando historial...")

    # 2. Análisis Core (Simulado si ya existe, forzado para demo)
    print("Ejecutando motor de análisis...")
    pages_data = pdf_analyzer.analyze_pdf(pdf_path)
    
    # 2.1 Procesamiento de Imágenes (Conexión Gemini)
    from analyzers import image_analyzer
    
    if pages_data:
        print("Buscando imágenes extraídas para análisis IA...")
        for page in pages_data:
            if page['images']:
                print(f"  > Imágenes detectadas en Página {page['page_number']}: {len(page['images'])}")
                for img in page['images']:
                    # En un caso real pasaríamos img['data'] (bytes) 
                    desc = image_analyzer.generate_image_description(img['name']) 
                    img['description'] = desc

    
    if pages_data:
        print(f"Análisis completado. Páginas procesadas: {len(pages_data)}")
        
        # 3. Guardar Resultado (Versión)
        analysis_version = {
            "timestamp": "25 de enero del 2026, 12:00",
            "version": "1.0",
            "pages_analyzed": len(pages_data),
            "credits_consumed": len(pages_data) # Simple calculation
        }
        
        history.log_analysis(doc_info['id'], analysis_version)
        print("Resultados guardados en historial.")
        
        # Output preview
        print(json.dumps(pages_data[0], indent=2, ensure_ascii=False)) # Show page 1
    else:
        print("Falló el análisis del PDF.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/main.py <ruta_al_pdf>")
    else:
        main(sys.argv[1])
