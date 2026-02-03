# AnDo - Plataforma de Inteligencia Documental

AnDo es una solución avanzada para el análisis, auditoría y cruce de documentos normativos y operativos utilizando Inteligencia Artificial Generativa.

---

## 🏗 Arquitectura del Sistema

El sistema ha sido migrado de una arquitectura monolítica (Streamlit) a una arquitectura moderna y escalable:

*   **Frontend**: React + TypeScript + TailwindCSS (Ubicado en `LandingPage00/components/ando`).
*   **Backend**: FastAPI (Python) (Ubicado en `AnDo00/api`).
*   **Core AI**: Google Gemini Pro 1.5 + OCR Multimodal.
*   **Persistencia**: Supabase (PostgreSQL + Storage).

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos
*   Node.js 18+
*   Python 3.10+
*   Cuenta de Supabase y Google Cloud (API Keys).

### 2. Configuración de Variables de Entorno (`.env`)
Asegúrate de tener un archivo `.env` en `AnDo00/` con:
```env
GOOGLE_API_KEY=tua_api_key
SUPABASE_URL=tu_url
SUPABASE_KEY=tu_service_role_key
```

### 3. Ejecutar el Servidor Backend (API)
Desde la raíz `AnDo00`:
```bash
# Activar entorno virtual si aplica
source .venv/bin/activate

# Iniciar Uvicorn (Puerto 8000)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
La documentación interactiva estará en: `http://localhost:8000/docs`.

### 4. Ejecutar el Cliente Frontend
Desde `LandingPage00`:
```bash
npm install
npm run dev
```
La aplicación estará disponible en: `http://localhost:3000/ando`.

---

## 🛠 Funcionalidades Clave

1.  **Análisis Multimodal**: Extracción de texto, tablas, imágenes, firmas y sellos.
2.  **Matriz de Congruencia**: Validación automática vs normas ISO/Compliance.
3.  **Cruce Operativo**: Comparación visual (Diagrama de Flujo) vs Procedimiento escrito.
    *   *Nota: La visualización de diagramas está en Beta.*
4.  **Detección de Suplantación**: Alerta de discrepancias entre firmantes y metadatos digitales.

---

## 📂 Estructura del Proyecto

*   `api/`: Controlador principal de FastAPI.
*   `src/analyzers/`: Módulos de lógica de IA (Detailed, Congruence, Cross, Impersonation).
*   `legacy/`: Código antiguo de Streamlit (Deprecado).
*   `docs/`: Bitácoras y documentación de migración.

---
**Versión Actual:** 2.0.0 (React Migration)
**Última Actualización:** Febrero 2026.
