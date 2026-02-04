# Plan de Acción: Implementación de Índice Inteligente e Interpretación de Congruencia
**Fecha:** 26 de enero del 2026
**Responsable:** Ingeniero Líder GetAuditUP

## Objetivo
Transformar el módulo de generación de reportes para que utilice IA real (Gemini 2.0 Flash) en la creación de un Índice General (TOC) y valide si los títulos encontrados coinciden semánticamente con el contenido de las páginas.

## Alcance Técnico
1.  **Nuevo Módulo de IA:** Crear `src/utils/index_logic.py` para manejar la lógica de extracción de índices.
2.  **Integración en Generadores:** Actualizar `src/generators/report_generator.py` para invocar a Gemini.
3.  **Lógica de Prompts:**
    - Solicitar a Gemini que identifique secciones principales y subsecciones.
    - Solicitar un "Score de Congruencia" comparando el Título del Índice vs el Contenido real.
4.  **UI (Streamlit):** Mostrar el Índice y el Score en la pestaña de "Análisis Inicial" o "Resumen".

## Pasos de Ejecución
1.  **Paso 1:** Desarrollar el prompt especializado para extracción de estructura.
2.  **Paso 2:** Implementar la llamada con reintentos (Retry Logic) en el generador.
3.  **Paso 3:** Actualizar la interfaz Streamlit para visualizar el índice de forma interactiva.
4.  **Paso 4:** Validación con documento real.

## Trazabilidad
- Los resultados se guardarán en el objeto `pages_data` para persistencia.
- Se registrará la actividad en `log_prompts.md`.

---
© 2026 Analizador de Documentos. V1.00
