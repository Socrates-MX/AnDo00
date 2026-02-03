# Bitácora de Desarrollo - Integración Backend & Persistencia
**Fecha:** 1 de Febrero de 2026
**Proyecto:** AnDo (GetAuditUP Suite)
**Responsable:** Antigravity & Usuario

## 🎯 Objetivo de la Sesión
Implementar la persistencia real de datos en Supabase para la aplicación AnDo, migrando de una estructura monolítica/mock a una arquitectura relacional (Hub & Spoke), y validar el flujo integral desde la Landing Page.

## 🛠 Acciones Realizadas

### 1. Base de Datos (Supabase)
- **Refactorización de Esquema:** Se implementó el nuevo esquema relacional definido en `sql_init_supabase.sql`.
    - `documents`: Tabla maestra ligera (ID, Hash, Nombre, Versión).
    - `analysis_detallado`: Tabla para almacenar el payload JSON pesado del análisis.
    - `revisiones_documento`: Tabla para trazabilidad de cambios.
- **Migración:** Se ejecutó el script SQL para crear las tablas nuevas y limpiar referencias antiguas (`ando_documents`).

### 2. Backend API (`api/main.py`)
- **Lógica de Persistencia:** Se eliminaron los placeholders (`pass`) y se implementó la inserción transaccional:
    1. Verificar Hash en `documents`.
    2. Si es nuevo, insertar cabecera en `documents`.
    3. Insertar detalle en `analysis_detallado`.
- **Nuevo Endpoint:** Se creó `GET /documents/{document_id}` para permitir al Frontend recuperar análisis históricos sin volver a procesar el PDF.

### 3. Frontend App (`src/app.py` & `document_manager.py`)
- **Adaptación al Esquema:** Se actualizó el gestor de persistencia para leer/escribir en las nuevas tablas (`version_actual` vs `current_version`).
- **Corrección de Bugs:**
    - Solucionado error `ModuleNotFoundError: No module named 'fpdf'` instalando la librería `fpdf2`.
    - Ajuste en la visualización de alertas para documentos existentes.

### 4. Pruebas Integrales
- **Entorno Completo:** Se levantaron simultáneamente:
    - LandingPage (`localhost:3000`)
    - AnDo API (`localhost:8000`)
    - AnDo App (`localhost:8501`)
- **Resultado:**
    - La carga de documentos detecta exitosamente duplicados por Hash.
    - Se confirma la recuperación de metadatos desde Supabase ("Documento Existente Detectado").
    - La integración visual desde LandingPage hacia AnDo funciona correctamente.

### 5. Multi-tenencia (SaaS Architecture)
- **Base de Datos:** Se agregó la columna `organization_id` a la tabla `documents` y se creó su índice correspondiente.
- **Backend API:**
    - Actualizado endpoint `POST /analyze/upload` para recibir `org_id`.
    - Lógica de detección de duplicados aislada: ahora verifica hash + organización.
- **Frontend App:**
    - Integración de `st.session_state.organization_id` en el flujo de guardado y verificación.
    - Implementación de lógica fallback para desarrollo local (ID por defecto).

### 6. Migración UI a React (Hub 3000)
- **Dashboard "Mis Documentos":** Se implementó una tabla nativa en React (`AnDoApp.tsx`) que consume el nuevo endpoint `/documents`.
- **Integración en Tiempo Real:** La tabla se actualiza automáticamente al terminar un análisis o subir un archivo.
- **Soporte Multi-tenant:** La vista filtra automáticamente los documentos usando el ID de la organización simulada.

## ✅ Estado Actual
- **Núcleo Funcional:** 100% Operativo. El ciclo Subida -> Análisis -> Persistencia -> Recuperación está completo.
- **SaaS Ready:** La arquitectura ahora soporta múltiples organizaciones aislando sus documentos.
- **Frontend Híbrido:** La versión React tiene paridad funcional de carga y visualización de listado.

## ⏭ Siguientes Pasos
1. **Visor de Histórico:** Permitir ver las diferencias entre la V1 y V2 de un documento en la UI (React).
2. **Visualización de Detalles:** Habilitar clic en la tabla para ver el detalle de un documento antiguo.
3. **Apagado Progresivo:** Evaluar qué funcionalidades restan en Streamlit para migrarlas totalmente.
