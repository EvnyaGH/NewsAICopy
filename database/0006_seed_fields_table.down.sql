BEGIN;

-- =========================
-- Computer Science subfields
-- =========================
WITH parent AS (SELECT id FROM fields WHERE code='cs' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN (
    'cs.AI','cs.AR','cs.CC','cs.CE','cs.CG','cs.CL','cs.CR','cs.CV','cs.CY',
    'cs.DB','cs.DC','cs.DL','cs.DM','cs.DS','cs.ET','cs.FL','cs.GL','cs.GR',
    'cs.GT','cs.HC','cs.IR','cs.IT','cs.LG','cs.LO','cs.MA','cs.MM','cs.MS',
    'cs.NA','cs.NE','cs.NI','cs.OH','cs.OS','cs.PF','cs.PL','cs.RO','cs.SC',
    'cs.SD','cs.SE','cs.SI','cs.SY'
  );

-- ===========
-- Economics
-- ===========
WITH parent AS (SELECT id FROM fields WHERE code='econ' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN ('econ.EM','econ.GN','econ.TH');

-- ==============================
-- Electrical Eng. & Sys. Science
-- ==============================
WITH parent AS (SELECT id FROM fields WHERE code='eess' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN ('eess.AS','eess.IV','eess.SP','eess.SY');

-- =============
-- Mathematics
-- =============
WITH parent AS (SELECT id FROM fields WHERE code='math' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN (
    'math.AC','math.AG','math.AP','math.AT','math.CA','math.CO','math.CT','math.CV',
    'math.DG','math.DS','math.FA','math.GM','math.GN','math.GR','math.GT','math.HO',
    'math.IT','math.KT','math.LO','math.MG','math.MP','math.NA','math.NT','math.OA',
    'math.OC','math.PR','math.QA','math.RA','math.RT','math.SG','math.SP','math.ST'
  );

-- =========
-- Physics
-- =========
WITH parent AS (SELECT id FROM fields WHERE code='physics' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN (
    'astro-ph','cond-mat','gr-qc','hep-ex','hep-lat','hep-ph','hep-th',
    'math-ph','nlin','nucl-ex','nucl-th','quant-ph','physics.gen-ph'
  );

-- =======================
-- Quantitative Biology
-- =======================
WITH parent AS (SELECT id FROM fields WHERE code='q-bio' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN (
    'q-bio.BM','q-bio.CB','q-bio.GN','q-bio.MN','q-bio.NC','q-bio.OT',
    'q-bio.PE','q-bio.QM','q-bio.SC','q-bio.TO'
  );

-- ========================
-- Quantitative Finance
-- ========================
WITH parent AS (SELECT id FROM fields WHERE code='q-fin' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN (
    'q-fin.CP','q-fin.EC','q-fin.GN','q-fin.MF','q-fin.PM','q-fin.PR','q-fin.RM','q-fin.ST','q-fin.TR'
  );

-- ============
-- Statistics
-- ============
WITH parent AS (SELECT id FROM fields WHERE code='stat' AND parent_id IS NULL)
DELETE FROM fields f
USING parent p
WHERE f.parent_id = p.id
  AND f.code IN ('stat.AP','stat.CO','stat.ME','stat.ML','stat.OT','stat.TH');

-- ============================
-- Finally: delete top-levels
-- (only if no remaining children)
-- ============================
DELETE FROM fields top
WHERE top.parent_id IS NULL
  AND top.code IN ('cs','econ','eess','math','physics','q-bio','q-fin','stat')
  AND NOT EXISTS (
    SELECT 1 FROM fields child WHERE child.parent_id = top.id
  );

COMMIT;
