BEGIN;

-- 0) UUIDs (safe if already enabled)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) fields hierarchy (one table: top-level fields + subfields)
CREATE TABLE IF NOT EXISTS fields (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code       TEXT NOT NULL,                 -- e.g., 'CS', 'AI'
  name       TEXT NOT NULL,                 -- e.g., 'Computer Science', 'Artificial Intelligence'
  parent_id  UUID REFERENCES fields(id),    -- NULL => field (top-level), NOT NULL => subfield under that field
  sort_order INT,
  UNIQUE (parent_id, code)                  -- code unique within its parent
);

-- Helpful index for lookups
CREATE INDEX IF NOT EXISTS fields_parent_idx ON fields(parent_id, code);

-- Need a UNIQUE constraint on (parent_id, id) so a composite FK can reference it
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fields_parent_id_id_uniq'
  ) THEN
    ALTER TABLE fields
      ADD CONSTRAINT fields_parent_id_id_uniq UNIQUE (parent_id, id);
  END IF;
END$$;

-- 2) papers: swap old columns for new FKs

-- Drop legacy text columns if they exist
ALTER TABLE papers DROP COLUMN IF EXISTS primary_subject;
ALTER TABLE papers DROP COLUMN IF EXISTS primary_category;

-- Add FK columns (top-level field + subfield)
ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS primary_field_id    UUID,
  ADD COLUMN IF NOT EXISTS primary_subfield_id UUID;

-- Add FK: primary_field_id -> fields(id)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'papers_primary_field_fk'
  ) THEN
    ALTER TABLE papers
      ADD CONSTRAINT papers_primary_field_fk
      FOREIGN KEY (primary_field_id) REFERENCES fields(id) ON DELETE RESTRICT;
  END IF;
END$$;

-- Add FK: primary_subfield_id -> fields(id)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'papers_primary_subfield_fk'
  ) THEN
    ALTER TABLE papers
      ADD CONSTRAINT papers_primary_subfield_fk
      FOREIGN KEY (primary_subfield_id) REFERENCES fields(id) ON DELETE RESTRICT;
  END IF;
END$$;

-- Enforce: chosen subfield belongs to chosen field
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'papers_field_subfield_pair_fk'
  ) THEN
    ALTER TABLE papers
      ADD CONSTRAINT papers_field_subfield_pair_fk
      FOREIGN KEY (primary_field_id, primary_subfield_id)
      REFERENCES fields(parent_id, id);
  END IF;
END$$;

-- Ensure the chosen field is top-level (parent_id IS NULL)
CREATE OR REPLACE FUNCTION enforce_field_top_level() RETURNS TRIGGER AS $$
DECLARE
  parent UUID;
BEGIN
  IF NEW.primary_field_id IS NOT NULL THEN
    SELECT parent_id INTO parent FROM fields WHERE id = NEW.primary_field_id;
    IF parent IS NOT NULL THEN
      RAISE EXCEPTION 'primary_field_id (%) must be a top-level field (parent_id IS NULL)', NEW.primary_field_id;
    END IF;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_enforce_field_top_level ON papers;
CREATE TRIGGER trg_enforce_field_top_level
  BEFORE INSERT OR UPDATE ON papers
  FOR EACH ROW EXECUTE FUNCTION enforce_field_top_level();

-- Query helpers
CREATE INDEX IF NOT EXISTS papers_primary_field_idx
  ON papers(primary_field_id);
CREATE INDEX IF NOT EXISTS papers_primary_subfield_idx
  ON papers(primary_subfield_id);

-- 3) Many-to-many: extra tags (can be field or subfield)
CREATE TABLE IF NOT EXISTS paper_fields (
  paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
  field_id UUID NOT NULL REFERENCES fields(id)  ON DELETE RESTRICT,
  PRIMARY KEY (paper_id, field_id)
);

CREATE INDEX IF NOT EXISTS paper_fields_by_field
  ON paper_fields(field_id, paper_id);

COMMIT;
