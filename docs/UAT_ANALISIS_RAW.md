# Protocolo UAT - Análisis RAW (Consolidación)

**Identificador:** UAT-ANDO-RAW-001
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE VALIDACIÓN
**Prompt Contractual:** V01.00

## 1. Objetivo
Verificar la funcionalidad del TAB "Análisis RAW", asegurando la consolidación íntegra y secuencial del contenido extraído, disponible en formatos Texto Plano y JSON Estructurado, sin intervención de IA adicional.

## 2. Alcance
- Pestaña "Análisis RAW".
- Toggle de Vistas (Texto / JSON).
- Verificación de contenido vs TAB "Página por Página".

## 3. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **RAW-01** | **Existencia del TAB** | El TAB "Análisis RAW" aparece después de "Análisis Pag por Pag". | Visible y clickeable. |
| **RAW-02** | **Vista Texto Plano** | Muestra contenido concatenado con separadores `--- PÁGINA X ---`. | Texto legible, orden secuencial (1..N). |
| **RAW-03** | **Integridad de Texto** | El texto RAW coincide carácter por carácter con la vista de página individual. | No hay texto truncado ni modificado. |
| **RAW-04** | **Vista JSON** | Al cambiar el toggle, muestra estructura JSON válida. | Formato `{ "documento": { ... } }` visible. |
| **RAW-05** | **Velocidad de Carga** | La carga es instantánea (no muestra spinners de IA). | Transición inmediata (Client-side rendering). |

## 4. Instrucciones para Tester
1. Cargar documento PDF.
2. Esperar análisis.
3. Ir a TAB "Análisis RAW".
4. Verificar que el texto comienza con `--- PÁGINA 1 ---`.
5. Cambiar a "Vista JSON" y verificar estructura.
6. Confirmar que no hubo llamadas de red adicionales (Network in DevTools).

## 5. Criterio de Liberación
Funcionalidad aceptada si RAW-01 a RAW-05 son exitosos.
