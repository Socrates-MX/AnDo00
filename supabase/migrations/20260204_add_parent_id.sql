-- MIGRATION: Add parent_id to ando_documents
-- Fecha: 2026-02-04
-- Autor: ANTIGRAVITY

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'ando_documents'
        AND column_name = 'parent_id'
    ) THEN
        ALTER TABLE "public"."ando_documents"
        ADD COLUMN "parent_id" UUID REFERENCES public.ando_documents(id);
        
        RAISE NOTICE 'Columna parent_id creada en ando_documents.';
    END IF;
END $$;
