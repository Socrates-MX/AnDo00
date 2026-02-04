-- MIGRATION: Add 'ConsolidacionRAW_completo' to 'analysis_detallado'
-- Fecha: 2026-02-02
-- Autor: ANTIGRAVITY
-- Prompt Contractual: V01.00

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'analysis_detallado'
        AND column_name = 'ConsolidacionRAW_completo'
    ) THEN
        ALTER TABLE "public"."analysis_detallado"
        ADD COLUMN "ConsolidacionRAW_completo" jsonb DEFAULT '{}'::jsonb;
        
        RAISE NOTICE 'Columna ConsolidacionRAW_completo creada exitosamente.';
    ELSE
        RAISE NOTICE 'La columna ya existe.';
    END IF;
END $$;
