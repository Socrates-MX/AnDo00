# Guía de Pruebas y Revisión - AnDo V1.0

Sigue estos pasos para validar el funcionamiento del prototipo en tu entorno local.

## 1. Configuración Previa
Asegúrate de tener configurada tu API Key de Google (opcional para test básico, obligatorio para test de imágenes real).
1. Abre el archivo `.env` en la raíz del proyecto.
2. Verifica que `GOOGLE_API_KEY` tenga tu clave (empieza por `AIza...`).

## 2. Prueba Básica (Flujo de Texto)
Ejecuta el análisis sobre un documento simple sin imágenes.
```bash
python3 src/main.py data/dummy.pdf
```
**Resultado esperado:**
- "Análisis completado".
- JSON mostrado en consola con el texto extraído.
- *Nota:* Si `data/dummy.pdf` no existe, créalo con: `python3 src/utils/create_test_pdf.py`

## 3. Prueba Avanzada (Flujo con Imágenes e IA)
Esta prueba valida la detección de imágenes y la conexión con Gemini.
1. Genera el PDF de prueba con gráficos:
   ```bash
   python3 src/utils/create_test_pdf_with_image.py
   ```
2. Ejecuta el análisis:
   ```bash
   python3 src/main.py data/dummy_with_image.pdf
   ```
**Resultado esperado:**
- Log: `> Imágenes detectadas en Página 1: 1`.
- JSON final: Dentro de `images`, verás un campo `description`.
    - Si configuraste la API Key: Verás una descripción generada por Google Gemini.
    - Si NO configuraste la API Key: Verás el mensaje `[MOCK] Configura tu GOOGLE_API_KEY...`.

## 4. Prueba con Documento Real
1. Copia cualquier PDF (ej. `mi_contrato.pdf`) a la carpeta `data/`.
2. Ejecuta:
   ```bash
   python3 src/main.py data/mi_contrato.pdf
   ```
3. Revisa la salida en consola y verifica el registro en `data/history.json`.

## 5. Revisión de Historial
Para ver todos los análisis realizados:
1. Abre el archivo `data/history.json`.
2. Verás un registro acumulado de todos los documentos y sus versiones analizadas.
