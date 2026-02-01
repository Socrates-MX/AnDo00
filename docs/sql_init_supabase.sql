-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS - AnDo (GetAuditUP)
-- PROMPT OFICIAL V1.00
-- REVISIÓN V1.01: Limpieza de esquema para evitar conflictos

-- ELIMINAR TABLAS EXISTENTES (Orden correcto por dependencias)
DROP TABLE IF EXISTS historial_cambios CASCADE;
DROP TABLE IF EXISTS revisiones_documento CASCADE;
DROP TABLE IF EXISTS analysis_detallado CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- 1. Maestría de Documentos
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_archivo TEXT NOT NULL,
    hash_documento TEXT UNIQUE NOT NULL, -- Para detectar si es el mismo contenido
    numero_paginas INTEGER,
    estado TEXT DEFAULT 'nuevo', -- nuevo, revisado
    version_actual INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Almacenamiento de Análisis Detallado (JSON)
CREATE TABLE analysis_detallado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    payload_completo JSONB NOT NULL,
    version INTEGER NOT NULL,
    fecha_analisis TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Registro de Revisiones y Diferencias
CREATE TABLE revisiones_documento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    version_anterior INTEGER,
    version_nueva INTEGER,
    cambios_detectados JSONB, -- Diff entre versiones
    aceptado_por_usuario BOOLEAN DEFAULT FALSE,
    fecha_revision TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Historial de Cambios Atómicos
CREATE TABLE historial_cambios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    revision_id UUID REFERENCES revisiones_documento(id) ON DELETE CASCADE,
    campo_afectado TEXT,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha_change TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Renombrado para evitar palabras reservadas si aplica
);

-- Índices para búsqueda rápida
CREATE INDEX idx_docs_hash ON documents(hash_documento);
CREATE INDEX idx_analysis_doc_id ON analysis_detallado(document_id);
