# Protocolo UAT - Persistencia Supabase: Consolidación RAW (V01.00)

**Identificador:** UAT-ANDO-DB-001
**Fecha:** 2026-02-02
**Estado:** PENDIENTE DE EJECUCIÓN

## 1. Objetivo
Validar la correcta creación de la columna `ConsolidacionRAW_completo` en la base de datos y la persistencia automática del JSON consolidado junto con el payload existente.

## 2. Alcance
- Base de Datos Supabase (Tabla `analysis_detallado`).
- API Backend (Persistencia).

## 3. Pre-Requisito (Migración)
El usuario o administrador DEBE ejecutar el siguiente bloque SQL en el Dashboard de Supabase antes de la prueba:

```sql
ALTER TABLE "public"."analysis_detallado"
ADD COLUMN IF NOT EXISTS "ConsolidacionRAW_completo" jsonb DEFAULT '{}'::jsonb;
```

## 4. Casos de Prueba

| ID | Caso de Prueba | Resultado Esperado | Criterio de Aceptación |
|---|---|---|---|
| **DB-RAW-01** | **Esquema DB** | La tabla tiene la columna `ConsolidacionRAW_completo`. | Visible en SQL Editor. |
| **DB-RAW-02** | **Persistencia Dual** | Al analizar un doc, se guardan datos en `payload_completo` Y `ConsolidacionRAW_completo`. | Query `SELECT` devuelve datos en ambas columnas. |
| **DB-RAW-03** | **Integridad JSON** | El JSON en la nueva columna tiene la estructura `{ documento: { analisis_raw: [] } }`. | JSON válido y consultable. |
| **DB-RAW-04** | **No Regresión** | El flujo normal de la app no falla (status 200 OK). | El usuario ve el resultado en Frontend sin errores. |

## 5. Instrucciones para Tester
1. Ejecutar el SQL de migración en Supabase.
2. Procesar un documento nuevo en AnDo.
3. Verificar en Supabase SQL Editor:
   `SELECT "ConsolidacionRAW_completo" FROM analysis_detallado WHERE document_id = '<ID>';`

## 6. Criterio de Liberación
Persistencia exitosa de ambos campos.
