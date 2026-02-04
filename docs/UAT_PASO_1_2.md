# Documento UAT – Paso 1 y Paso 2: Carga y Análisis
**ID Prueba:** UAT-ANDO-001  
**Fecha:** 2026-02-02  
**Responsable:** Antigravity AI  

## 1. Objetivo
Verificar que la carga de documentos PDF y su análisis posterior muestren un **progreso dinámico y transparente** al usuario, replicando o mejorando la experiencia de la versión anterior (Streamlit).

## 2. Alcance
- **Paso 1:** Carga del archivo PDF (Upload).
- **Paso 2:** Procesamiento en tiempo real (Feedback visual de fases).

## 3. Precondiciones
- Backend (FastAPI) activo y libre de errores.
- Frontend (React) cargado con usuario mock.
- Archivo de prueba PDF disponible (`TRA-P-01.pdf` o similar).

## 4. Escenario de Prueba y Resultados Esperados

| Paso | Acción | Comportamiento Esperado (Criterio de Aceptación) | Estado Actual (Evidencia) |
|---|---|---|---|
| 1 | Cargar PDF | El sistema acepta el archivo y cambia a estado de "Procesando". | **OK** (Ver Imagen 1 y 2) |
| 2 | Iniciar Análisis | Se muestran fases secuenciales (ej. "Fase 1/5: OCR...") actualizándose en tiempo real. | **FALLO (Problema 1)**: Se muestra un loader genérico "Procesando Documento..." sin detalle de actividad. (Ver Imagen 2) |
| 3 | Finalizar | Se muestra "Análisis Completado" y la lista de verificaciones en verde. | **OK** (Ver Imagen 3) |

## 5. Análisis del Problema 1 (Bloqueante)
**Descripción:** La interfaz actual en React simplifica excesivamente el estado de carga (`processing`), ocultando la lista de pasos (`steps`) que el backend está reportando. El usuario ve una barra vacía o un spinner, perdiendo contexto.

**Causa Raíz Identificada:** El estado `steps` iniciaba vacío, esperando al primer polling del backend, causando un "flash" de contenido vacío o loader genérico.

## 6. Corrección Aplicada
1. Se ha inyectado `INITIAL_STEPS` en `AnDoApp.tsx` al momento de incurrir en `status === 'processing'`.
2. Esto fuerza la renderización inmediata de la lista de 5 fases, con la Fase 1 activa, eliminando la incertidumbre visual.

## 7. Mejora Adicional (V01.01 - Progreso Granular)
Se ha implementado la visualización de **sub-estados internos**.
- **Comportamiento Esperado:** Durante la Fase 1 (OCR), el sistema mostrará debajo del título de la fase: `» Procesando página X de Y...`.
- **Backend:** `pdf_analyzer.py` reporta progreso al orquestador.
- **Frontend:** Renderiza un campo `detail` animado.

---
**Estado de la Prueba:** ⚠️ PENDIENTE DE EJECUCIÓN (Por favor, reinicia la prueba de carga para validar el detalle granular).
