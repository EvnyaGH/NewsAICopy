BEGIN;

-- 1) Drop many-to-many table
DROP TABLE IF EXISTS paper_fields;

-- 2) Drop constraints on papers
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'papers_field_subfield_pair_fk') THEN
    ALTER TABLE papers DROP CONSTRAINT papers_field_subfield_pair_fk;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'papers_primary_field_fk') THEN
    ALTER TABLE papers DROP CONSTRAINT papers_primary_field_fk;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'papers_primary_subfield_fk') THEN
    ALTER TABLE papers DROP CONSTRAINT papers_primary_subfield_fk;
  END IF;
END$$;

-- 3) Drop trigger + function
DROP TRIGGER IF EXISTS trg_enforce_field_top_level ON papers;
DROP FUNCTION IF EXISTS enforce_field_top_level;

-- 4) Drop new columns from papers
ALTER TABLE papers DROP COLUMN IF EXISTS primary_field_id;
ALTER TABLE papers DROP COLUMN IF EXISTS primary_subfield_id;

-- 5) Restore old columns
ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS primary_subject  TEXT,
  ADD COLUMN IF NOT EXISTS primary_category TEXT;

-- 6) Drop fields table
DROP TABLE IF EXISTS fields;

COMMIT;
