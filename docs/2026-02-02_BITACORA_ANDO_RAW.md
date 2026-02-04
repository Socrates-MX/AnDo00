# Bitácora de Desarrollo - 2 de Febrero 2026
**Proyecto:** AnDo (Analizador Documental)
**Módulo:** Backend de Análisis RAW y Frontend de Visualización

## 🚀 Resumen Ejecutivo
Se realizó una reingeniería profunda del módulo de análisis para priorizar la **"Evidencia RAW"** (contenido crudo) sobre el análisis estructurado tradicional. Esto incluyó la creación de nuevos analizadores en backend, la implementación de tablas de congruencia específicas y la solución de problemas de robustez en la generación de datos con IA.

## 🛠️ Cambios Técnicos Realizados

### 1. Backend (`api` y `src/analyzers`)
*   **Nuevo Motor de Análisis (`raw_congruence_analyzer.py`):**
    *   Implementación de análisis de congruencia basado puramente en texto crudo + interpretación de imágenes.
    *   **Prompt Engineering:** Se definieron prompts estrictos para extraer:
        *   Matrices de Congruencia de 9 Puntos (Título vs Contenido, Objetivo vs Información, etc.).
        *   Diagramas de Flujo en formato MermaidJS.
        *   Tablas de Desviaciones Normativas e Inconsistencias Operativas.
    *   **Robustez:** Se activó el `response_mime_type="application/json"` en Gemini Flash 2.0 y se implementó un saneamiento de strings (escaping de llaves `{}`) para evitar caídas por inyección de código en PDFs técnicos.
    *   **Hotfix:** Se deshabilitó temporalmente la validación de duplicados (Hash check) en `main.py` para permitir el re-análisis forzado de documentos durante las pruebas.

### 2. Frontend (`AnDoApp.tsx`)
*   **Reestructuración de Pestañas (Tabs):**
    *   **Nuevo Tab "Análisis de Elementos":** Se creó una vista dedicada para la Matriz de 9 Puntos de Control (Título, Objetivo, Alcance, Participantes, etc.).
    *   **Tab "Hallazgos y Riesgos":** Se reemplazó la lista antigua por tablas RAW de "Desviaciones Normativas" (Cumple/No Cumple) e "Inconsistencias Operativas" (Severidad Alta/Media/Baja).
    *   **Tab "Diagrama de Flujo":** Se restauró la visualización gráfica (Mermaid) + Tabla estructural de pasos, permitiendo alternar entre esta vista y el Cruce Operativo.
*   **Experiencia de Usuario (UX):**
    *   Implementación de **"Fallbacks Visuales"**: Ahora las pestañas muestran advertencias claras ("Análisis no disponible") cuando los datos no existen, en lugar de pantallas blancas vacías.
    *   Mejora en la CSS de las tablas (estilos "Blue" para Elementos, "Amber" para Riesgos, "Purple" para Cruce).

## 🐛 Bugs Corregidos
1.  **Pantalla Blanca en Tabs:** Corregido mediante validación condicional y mensajes de error amigables.
2.  **Fallo Silencioso en Backend:** El analizador RAW devolvía `None` si el PDF contenía caracteres especiales (`{}`) o si la IA respondía con Markdown. Se corrigió sanitizando la entrada y forzando modo JSON.
3.  **Persistencia de Datos Viejos:** Al re-subir el mismo PDF, el sistema no actualizaba el reporte. Se solucionó (temporalmente) permitiendo re-procesar hash duplicados.

## 📝 Estado Final
El sistema es capaz de generar y visualizar un análisis de congruencia normativa avanzado con un nivel de detalle "forense", separando claramente lo que dice el texto (RAW) de las alucinaciones estructurales.

---
**Próximos Pasos Sugeridos:**
*   Rehabilitar el chequeo de duplicados con un botón explícito de "Forzar Re-análisis" en la UI.
*   Refinar los prompts para casos de documentos muy extensos (paginación de contexto RAW).
