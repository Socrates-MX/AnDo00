import sys
import os
import json
from dotenv import load_dotenv

# Asegurar que el path incluya src para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzers import pdf_analyzer, image_analyzer

def test_maestro(pdf_path="data/archivo_maestro.pdf"):
    print(f"--- Iniciando Análisis de DOCUMENTO MAESTRO ---")
    print(f"Archivo: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"Error: No se encontró el archivo maestro en {pdf_path}")
        return

    load_dotenv()

    # 1. Extracción de Texto e imágenes
    print("1. Ejecutando extracción de PDF...")
    pages_data = pdf_analyzer.analyze_pdf(pdf_path)
    
    if not pages_data:
        print("Falló el análisis del PDF.")
        return

    print(f"Éxito: {len(pages_data)} páginas detectadas.")

    # 2. Análisis de Imágenes
    print("2. Ejecutando análisis de imágenes con IA...")
    total_imgs = 0
    imgs_sustantivas = 0
    
    for page in pages_data:
        if page['images']:
            total_imgs += len(page['images'])
            for img in page['images']:
                desc = image_analyzer.generate_image_description(img['image_bytes'])
                img['description'] = desc
                if "[SKIP]" not in desc.upper():
                    imgs_sustantivas += 1

    print(f"Resumen de imágenes:")
    print(f" - Totales: {total_imgs}")
    print(f" - Sustantivas (No logos/marcas): {imgs_sustantivas}")
    
    # 3. Guardar línea base
    baseline_path = "data/baseline_maestro.json"
    # Limpiamos bytes para guardar el JSON
    for p in pages_data:
        for img in p['images']:
            img.pop('image_bytes', None)

    with open(baseline_path, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Línea base establecida y guardada en: {baseline_path}")

if __name__ == "__main__":
    test_maestro()
