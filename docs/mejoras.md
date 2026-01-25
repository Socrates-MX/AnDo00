# Puntos de Mejora y Roadmap

## Mejoras Técnicas Identificadas
1.  **Validación de Imágenes:** El mock actual (`src/analyzers/image_analyzer.py`) debe conectarse a la API de Google Gemini Vision.
    *   *Acción:* Obtener API Key y descomentar lógica de llamada.
2.  **Extracción Robusta:** `pypdf` es básico. Evaluar `pdfplumber` para tablas complejas.
3.  **Persistencia:** Migrar de `JSON` local a Supabase (PostgreSQL) vía MCP.
4.  **Frontend:** Reemplazar CLI actual por interfaz web en Next.js (como indica el plan maestro, futura exportación).

## Notas para Exportación a GitHub
*   Asegurar que `data/` esté en `.gitignore`.
*   Incluir `requirements.txt` actualizado.
*   Documentar variables de entorno necesarias (e.g., `GOOGLE_API_KEY`).
