# Protocolo UAT - Interpretación de Diagramas de Flujo (V01.00)

**Identificador:** UAT-ANDO-DIAG-001
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE EJECUCIÓN

## 1. Objetivo
Validar que el sistema detecte, analice y convierta a texto lógico los diagramas de flujo contenidos dentro del documento PDF, discriminando elementos decorativos.

## 2. Alcance
- Integración Multimodal (Gemini Vision).
- Tab "Análisis Pag por Pag" -> Sección "Contenido Visual".
- Validación vs Imagen Original (Página 3 de TRA-P-01).

## 3. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **DIAG-01** | **Detección de Imagen** | Detecta la imagen en la Página 3. | Aparece lista "Contenido Visual" con la imagen. |
| **DIAG-02** | **Discriminación (SKIP)** | Logos y márgenes son marcados como "Decorativo". | Texto gris indicando omisión. |
| **DIAG-03** | **Interpretación de Flujo** | El diagrama de la Pág 3 muestra texto estructurado. | Bloque de texto visible con formato "1. [Inicio]...". |
| **DIAG-04** | **Fidelidad Lógica** | El texto describe el flujo correcto (Pre-Calificación). | Coincidencia lógica con la imagen original. |
| **DIAG-05** | **Persistencia** | La descripción se mantiene al cambiar de tab. | Datos persistentes en JSON. |

## 4. Instrucciones para Tester
1. Cargar documento `TRA-P-01.pdf`.
2. Observar progreso en Fase 2 ("Analizando imágenes...").
3. Ir a Tab "Análisis Pag por Pag".
4. Scrollear a **Página 3**.
5. Verificar el bloque "Contenido Visual".
6. Confirmar que el texto describe el flujo de decisión.

## 5. Criterio de Liberación
Funcionalidad aceptada si el diagrama es legible en modo texto.
