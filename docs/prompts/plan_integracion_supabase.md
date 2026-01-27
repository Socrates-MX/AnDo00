# Plan de Acción: Integración de Persistencia y Versionado (Supabase)
**Fecha:** 26 de enero del 2026
**Responsable:** Ingeniero Líder GetAuditUP

## Objetivo
Implementar la capa de persistencia utilizando Supabase para habilitar el versionado de documentos, detección de cambios y auditoría histórica, siguiendo el **PROMPT OFICIAL V1.00**.

## Arquitectura de Persistencia
1.  **Motor:** Base de datos relacional PostgreSQL (Supabase).
2.  **Cliente:** `supabase-py` para comunicación segura.
3.  **Identificación:** Uso de **Hashing (SHA-256)** para reconocer documentos idénticos aunque cambien de nombre.

## Componentes a Desarrollar
1.  **SQL Schema**: Script de creación de tablas (`documents`, `analysis_detallado`, `revisiones_documento`, `historial_cambios`).
2.  **Supabase Client**: Módulo `src/utils/supabase_client.py`.
3.  **Repositorio de Persistencia**: `src/persistence/document_manager.py` para manejar el flujo de Nuevo vs Revisado.
4.  **UI de Versionado**:
    - Alerta de "Documento ya existente".
    - Resumen de diferencias (diff) entre la versión en DB y el nuevo análisis.
    - Botón de **Aceptación de Cambios** para versionar.

## Pasos de Ejecución
1.  **Paso 1**: Generar el script SQL para la base de datos.
2.  **Paso 2**: Configurar variables de entorno (`SUPABASE_URL`, `SUPABASE_KEY`).
3.  **Paso 3**: Implementar el gestor de persistencia.
4.  **Paso 4**: Integrar la lógica de "Volver a Revisar" con comparación de JSON/Diff.
5.  **Paso 5**: Sincronización con GitHub.

---
© 2026 Analizador de Documentos. V1.00
