# Protocolo UAT - Extensión RAW con Imágenes (V01.01)

**Identificador:** UAT-ANDO-RAW-002
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE EJECUCIÓN
**Prompt Contractual:** V01.01

## 1. Objetivo
Validar que la Consolidación RAW incluya no solo el texto del PDF, sino también el texto interpretado de imágenes funcionales (Diagramas, etc.), asegurando completitud para auditoría.

## 2. Alcance
- Tab "Análisis RAW".
- Validación de contenido híbrido (Texto + Imagen Interpretada).
- Validación de JSON Estructurado V2.

## 3. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **RAW-EXT-01** | **Header de Imágenes** | En páginas con diagramas (ej. Pag 3), aparece `--- CONTENIDO DERIVADO DE IMÁGENES ---`. | Visible en Vista Texto. |
| **RAW-EXT-02** | **Contenido de Imagen** | Debajo del header, aparece la descripción lógica del diagrama. | Texto coincide con el visto en "Pág por Pág". |
| **RAW-EXT-03** | **Omisión de Ruido** | Imágenes [SKIP] NO aparecen en el RAW. | RAW limpio de basura visual. |
| **RAW-EXT-04** | **JSON Estructurado** | El JSON tiene campos `contenido_raw_pdf` y `contenido_raw_imagenes`. | Estructura válida para consumo API. |
| **RAW-EXT-05** | **Consistencia** | El total de caracteres del RAW es mayor que antes de la actualización (debido a las imágenes). | Enriquecimiento confirmado. |

## 4. Instrucciones para Tester
1. Usar documento analizado con diagramas (`TRA-P-01`).
2. Ir a "Análisis RAW".
3. Buscar página 3.
4. Confirmar presencia del bloque de imagen.
5. Cambiar a JSON y verificar array `contenido_raw_imagenes`.

## 5. Criterio de Liberación
Prueba aceptada si el RAW exportable contiene la "verdad completa" (Texto + Interpretación Visual).
