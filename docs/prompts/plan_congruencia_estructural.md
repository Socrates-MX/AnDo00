# Plan de Acción: Implementación de Prueba de Congruencia del Contenido (IA)
**Fecha:** 26 de enero del 2026
**Responsable:** Ingeniero Líder GetAuditUP

## Objetivo
Implementar el módulo de validación cruzada entre secciones críticas del documento (Título, Objetivo, Alcance, Políticas, Procedimientos y Firmantes) siguiendo el **PROMPT OFICIAL V1.00**.

## Arquitectura
1.  **Analizador:** Crear `src/analyzers/congruence_analyzer.py` para procesas la comparación semántica.
2.  **Entrada:** Utilizará el `detailed_report` (JSON estructurado) y el `pages_data` para contexto.
3.  **Salida:** Un objeto JSON que contenga la matriz de congruencia y la conclusión objetiva.

## Pasos de Ejecución
1.  **Diseño de Insumos**: Formatear los datos del reporte detallado para que sean digeribles por el prompt de IA.
2.  **Lógica de Análisis**: Implementar la llamada a Gemini 2.0 Flash con el prompt de "Prueba IA".
3.  **Interfaz de Usuario**:
    - Agregar sección "3. Prueba de Congruencia Estructural" en la pestaña "Revisión del documento".
    - Mostrar la matriz de resultados (✅, ⚠️, ❌).
    - Presentar la conclusión y riesgos detectados en un formato ejecutivo.

## Trazabilidad
- Registro en `log_prompts.md`.
- Sincronización automática con GitHub.

---
© 2026 Analizador de Documentos. V1.00
