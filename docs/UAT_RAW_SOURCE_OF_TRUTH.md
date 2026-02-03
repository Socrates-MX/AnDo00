# Protocolo UAT - RAW como Fuente Única de Verdad (V01.00)

**Identificador:** UAT-ANDO-ARCH-001
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE EJECUCIÓN

## 1. Objetivo
Validar que todos los análisis subsiguientes (Hallazgos, Congruencia, Diagramas) se generen exclusivamente a partir del Contenido RAW Consolidado, sin volver a procesar el archivo PDF original.

## 2. Alcance
- Pipeline del Backend (Fases 3, 4 y 5).
- Trazabilidad de datos.
- Consistencia Texto vs Reporte.

## 3. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **ARCH-01** | **Independencia de Archivo** | El análisis detallado se ejecuta sin acceso al PDF en Fase 3. | El log del servidor no muestra "Subiendo archivo...". |
| **ARCH-02** | **Trazabilidad de Imágenes** | El reporte final (Fase 3/4) cita texto que PROVIENE de la interpretación de la imagen en Fase 2. | Si Fase 2 interpretó "Paso X", Fase 3 lo usa. |
| **ARCH-03** | **Congruencia RAW** | No aparecen datos en el reporte final que no existan en el RAW (alucinaciones minimizadas por contexto restringido). | Todo hallazgo tiene referente en el RAW. |
| **ARCH-04** | **Velocidad** | La Fase 3 es más rápida al no subir crudos a la nube. | Tiempo de procesamiento optimizado. |

## 4. Instrucciones para Tester
1. Ejecutar análisis completo de `TRA-P-01`.
2. Verificar logs de consola del backend (opcional).
3. Comparar el texto del TAB "Análisis RAW" con el contenido de "Hallazgos y Riesgos".
4. Confirmar que los hallazgos citan frases presentes en el RAW.

## 5. Criterio de Liberación
Arquitectura aceptada si el sistema funciona end-to-end con la nueva restricción de fuente única.
