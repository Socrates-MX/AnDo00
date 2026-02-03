# Plan Detallado de Migración AnDo (React + FastAPI)

Este documento define el estado actual y la hoja de ruta para completar la migración del sistema AnDo desde Streamlit hacia una arquitectura moderna basada en React y FastAPI.

## 📍 Estado Actual (Fase 5: Estabilización)
El sistema se encuentra en un estado funcional del 90%. El núcleo de procesamiento de IA y la persistencia de datos operan correctamente. La interfaz de usuario en React ha alcanzado la paridad funcional con la versión anterior.

### ✅ Fases Completadas

1.  **Fase 1: Infraestructura y Backend (API Headless)**
    *   [x] Configuración de FastAPI (`api/main.py`).
    *   [x] Integración completa con **Supabase** (Base de datos y Storage).
    *   [x] Endpoints CRUD: Carga (`/upload`), Estado, Borrado (`DELETE`).
    *   [x] Configuración de CORS y Middleware de seguridad (Permisivo para dev).

2.  **Fase 2: Motor de Inteligencia Artificial (Core)**
    *   [x] Migración de `pdf_analyzer.py` (OCR y Visión).
    *   [x] Migración de `detailed_analyzer.py` (Reporte base + Mermaid Graph).
    *   [x] Migración de `congruence_analyzer.py` (Matriz de coherencia).
    *   [x] Migración de `process_cross_analyzer.py` (Cruce operativo).
    *   [x] Implementación de `impersonation_analyzer.py` (Detección de fraude).

3.  **Fase 3: Frontend Moderno (React/TSX)**
    *   [x] Componente principal `AnDoApp.tsx`.
    *   [x] Carga de archivos con feedback visual (Drag & Drop).
    *   [x] Barra de progreso en tiempo real (Polling).
    *   [x] Pestañas de resultados (Resumen, Matrices, Diagrama).

4.  **Fase 5: Estabilización Visual (⚠️ DEUDA TÉCNICA)**
    *   [x] Generación de código Mermaid (Backend Inyectado).
    *   [!] **Visualización de Diagramas**: El componente existe pero el renderizado visual es inconsistente (Fallback activo). Se mantiene como Deuda Técnica Aceptada.

---

## 🔜 Hoja de Ruta Restante (Fases 6-8)

### Fase 6: Limpieza y Optimización (Inmediato)
1.  **Revisión de Hallazgos y Riesgos:**
    *   Verificar que la sección de "Alertas de Seguridad" y hallazgos críticos sea claramente visible en la UI.
2.  **Limpieza de Código:**
    *   Eliminar funciones duplicadas o código muerto en `api/main.py` (residuos de debugging).
    *   Reducir la verbosidad de logs en consola.
3.  **Gestión de Errores UX:**
    *   Asegurar mensajes de error amigables en el Frontend (no mostrar "Internal Server Error" crudo).

### Fase 7: Deprecación del Legado (Switch-Off)
1.  **Archivado de Streamlit:**
    *   Mover `src/app.py` y `src/pages` a una carpeta `legacy/` para referencia histórica.
    *   Actualizar scripts de inicio para no levantar Streamlit por defecto.
2.  **Unificación de Puertos:**
    *   Estandarizar los puertos de desarrollo (Frontend: 3000, Backend: 8000).

### Fase 8: Entrega Final
1.  **Documentación:**
    *   Actualizar `README.md` con instrucciones de inicio para el nuevo stack.
2.  **Validación de Entorno:**
    *   Confirmar variables de entorno en `.env` para producción.

---
**Última Actualización:** 2 de Febrero de 2026.
