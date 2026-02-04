# Protocolo UAT - Análisis Página por Página (V02.03)

**Identificador:** UAT-ANDO-PAG-001
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE VALIDACIÓN

## 1. Objetivo
Validar la funcionalidad de desglose granular del análisis de documentos PDF, asegurando que cada página sea procesada, identificada y validada individualmente en cuanto a estructura e integridad.

## 2. Alcance (Funcionalidad Nueva)
- Tab "Análisis Pag por Pag" en la interfaz de resultados.
- Visualización de tarjetas individuales por página.
- Validaciones automáticas de footer (Pág X de Y).
- Detección de títulos y contenido visual.

## 3. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **CPP-01** | **Visualización de Pestaña** | La pestaña "Análisis Pag por Pag" es visible después del análisis. | Tab Renderizado correctamente en la barra de navegación. |
| **CPP-02** | **Desglose Secuencial** | Se muestran tarjetas ordenadas (Página 1, Página 2, ...). | Existencia de N tarjetas donde N es el total de páginas. |
| **CPP-03** | **Validación de Integridad (Exitosa)** | Si el documento tiene "Página 1 de 5", el sistema muestra "✓ Footer Íntegro". | Badge verde visible. |
| **CPP-04** | **Validación de Integridad (Fallida)** | Si falta una página o el número no coincide, muestra "⚠️ Error Integridad". | Badge rojo visible y detalle del error. |
| **CPP-05** | **Identificación de Títulos** | Detecta líneas en mayúsculas como posibles títulos. | Lista de "Títulos Detectados" poblada. |
| **CPP-06** | **Contenido Raw** | Muestra el texto extraído íntegramente. | Caja de texto scrollable con contenido legible. |

## 4. Instrucciones para Tester
1. Cargar el documento `TRA-P-01.pdf` (u otro PDF operativo).
2. Observar el progreso dinámico (Validación anterior).
3. Al finalizar, navegar al tab "Análisis Pag por Pag".
4. Verificar visualmente cada uno de los puntos CPP-01 a CPP-06.
5. Tomar captura de pantalla como evidencia.

## 5. Criterio de Liberación
La funcionalidad se considerará **LIBERADA** si todos los casos CPP-01 a CPP-06 son marcados como **EXITOSO** sin errores de consola.
