BEGIN;

-- ===========================================
-- Top-level fields (parent_id = NULL)
-- ===========================================
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('cs',      'Computer Science',                             NULL, 1),
  ('econ',    'Economics',                                    NULL, 2),
  ('eess',    'Electrical Engineering and Systems Science',   NULL, 3),
  ('math',    'Mathematics',                                  NULL, 4),
  ('physics', 'Physics',                                      NULL, 5),
  ('q-bio',   'Quantitative Biology',                         NULL, 6),
  ('q-fin',   'Quantitative Finance',                         NULL, 7),
  ('stat',    'Statistics',                                   NULL, 8)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Computer Science subfields (alphabetical by name)
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='cs' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('cs.AI','Artificial Intelligence',               (SELECT id FROM parent), 1),
  ('cs.GT','Computer Science and Game Theory',      (SELECT id FROM parent), 2),
  ('cs.CL','Computation and Language',              (SELECT id FROM parent), 3),
  ('cs.CC','Computational Complexity',              (SELECT id FROM parent), 4),
  ('cs.CE','Computational Engineering, Finance, and Science', (SELECT id FROM parent), 5),
  ('cs.CG','Computational Geometry',                (SELECT id FROM parent), 6),
  ('cs.CY','Computers and Society',                 (SELECT id FROM parent), 7),
  ('cs.CR','Cryptography and Security',             (SELECT id FROM parent), 8),
  ('cs.DB','Databases',                             (SELECT id FROM parent), 9),
  ('cs.DC','Distributed, Parallel, and Cluster Computing',(SELECT id FROM parent), 10),
  ('cs.DL','Digital Libraries',                     (SELECT id FROM parent), 11),
  ('cs.DM','Discrete Mathematics',                  (SELECT id FROM parent), 12),
  ('cs.DS','Data Structures and Algorithms',        (SELECT id FROM parent), 13),
  ('cs.ET','Emerging Technologies',                 (SELECT id FROM parent), 14),
  ('cs.FL','Formal Languages and Automata Theory',  (SELECT id FROM parent), 15),
  ('cs.GL','General Literature',                    (SELECT id FROM parent), 16),
  ('cs.GR','Graphics',                              (SELECT id FROM parent), 17),
  ('cs.HC','Human-Computer Interaction',            (SELECT id FROM parent), 18),
  ('cs.IR','Information Retrieval',                 (SELECT id FROM parent), 19),
  ('cs.IT','Information Theory',                    (SELECT id FROM parent), 20),
  ('cs.LG','Machine Learning',                      (SELECT id FROM parent), 21),
  ('cs.LO','Logic in Computer Science',             (SELECT id FROM parent), 22),
  ('cs.MS','Mathematical Software',                 (SELECT id FROM parent), 23),
  ('cs.MA','Multiagent Systems',                    (SELECT id FROM parent), 24),
  ('cs.MM','Multimedia',                            (SELECT id FROM parent), 25),
  ('cs.NA','Numerical Analysis (alias of math.NA)', (SELECT id FROM parent), 26),
  ('cs.NE','Neural and Evolutionary Computing',     (SELECT id FROM parent), 27),
  ('cs.NI','Networking and Internet Architecture',  (SELECT id FROM parent), 28),
  ('cs.OH','Other Computer Science',                (SELECT id FROM parent), 29),
  ('cs.OS','Operating Systems',                     (SELECT id FROM parent), 30),
  ('cs.PF','Performance',                           (SELECT id FROM parent), 31),
  ('cs.PL','Programming Languages',                 (SELECT id FROM parent), 32),
  ('cs.RO','Robotics',                              (SELECT id FROM parent), 33),
  ('cs.SC','Symbolic Computation',                  (SELECT id FROM parent), 34),
  ('cs.SD','Sound',                                 (SELECT id FROM parent), 35),
  ('cs.SE','Software Engineering',                  (SELECT id FROM parent), 36),
  ('cs.SI','Social and Information Networks',       (SELECT id FROM parent), 37),
  ('cs.AR','Hardware Architecture',                 (SELECT id FROM parent), 38),
  ('cs.SY','Systems and Control (alias of eess.SY)',(SELECT id FROM parent), 39)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Economics subfields
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='econ' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('econ.EM','Econometrics',          (SELECT id FROM parent), 1),
  ('econ.GN','General Economics',     (SELECT id FROM parent), 2),
  ('econ.TH','Theoretical Economics', (SELECT id FROM parent), 3)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- EESS subfields
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='eess' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('eess.AS','Audio and Speech Processing', (SELECT id FROM parent), 1),
  ('eess.IV','Image and Video Processing',  (SELECT id FROM parent), 2),
  ('eess.SP','Signal Processing',           (SELECT id FROM parent), 3),
  ('eess.SY','Systems and Control',         (SELECT id FROM parent), 4)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Mathematics subfields (alphabetical by name)
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='math' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('math.AG','Algebraic Geometry',           (SELECT id FROM parent), 1),
  ('math.AT','Algebraic Topology',           (SELECT id FROM parent), 2),
  ('math.AC','Commutative Algebra',          (SELECT id FROM parent), 3),
  ('math.CO','Combinatorics',                (SELECT id FROM parent), 4),
  ('math.CV','Complex Variables',            (SELECT id FROM parent), 5),
  ('math.CT','Category Theory',              (SELECT id FROM parent), 6),
  ('math.DG','Differential Geometry',        (SELECT id FROM parent), 7),
  ('math.DS','Dynamical Systems',            (SELECT id FROM parent), 8),
  ('math.FA','Functional Analysis',          (SELECT id FROM parent), 9),
  ('math.GM','General Mathematics',          (SELECT id FROM parent), 10),
  ('math.GN','General Topology',             (SELECT id FROM parent), 11),
  ('math.GR','Group Theory',                 (SELECT id FROM parent), 12),
  ('math.GT','Geometric Topology',           (SELECT id FROM parent), 13),
  ('math.HO','History and Overview',         (SELECT id FROM parent), 14),
  ('math.IT','Information Theory (alias of cs.IT)', (SELECT id FROM parent), 15),
  ('math.KT','K-Theory and Homology',        (SELECT id FROM parent), 16),
  ('math.LO','Logic',                        (SELECT id FROM parent), 17),
  ('math.MP','Mathematical Physics (alias of math-ph)', (SELECT id FROM parent), 18),
  ('math.MG','Metric Geometry',              (SELECT id FROM parent), 19),
  ('math.NT','Number Theory',                (SELECT id FROM parent), 20),
  ('math.NA','Numerical Analysis',           (SELECT id FROM parent), 21),
  ('math.OA','Operator Algebras',            (SELECT id FROM parent), 22),
  ('math.OC','Optimization and Control',     (SELECT id FROM parent), 23),
  ('math.PR','Probability',                  (SELECT id FROM parent), 24),
  ('math.QA','Quantum Algebra',              (SELECT id FROM parent), 25),
  ('math.RA','Rings and Algebras',           (SELECT id FROM parent), 26),
  ('math.RT','Representation Theory',        (SELECT id FROM parent), 27),
  ('math.SG','Symplectic Geometry',          (SELECT id FROM parent), 28),
  ('math.SP','Spectral Theory',              (SELECT id FROM parent), 29),
  ('math.ST','Statistics Theory',            (SELECT id FROM parent), 30)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Physics subfields (alphabetical by name)
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='physics' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('astro-ph',      'Astrophysics',                                 (SELECT id FROM parent), 1),
  ('cond-mat',      'Condensed Matter',                             (SELECT id FROM parent), 2),
  ('gr-qc',         'General Relativity and Quantum Cosmology',     (SELECT id FROM parent), 3),
  ('physics.gen-ph','General Physics',                              (SELECT id FROM parent), 4),
  ('hep-ex',        'High Energy Physics - Experiment',             (SELECT id FROM parent), 5),
  ('hep-lat',       'High Energy Physics - Lattice',                (SELECT id FROM parent), 6),
  ('hep-ph',        'High Energy Physics - Phenomenology',          (SELECT id FROM parent), 7),
  ('hep-th',        'High Energy Physics - Theory',                 (SELECT id FROM parent), 8),
  ('math-ph',       'Mathematical Physics',                         (SELECT id FROM parent), 9),
  ('nlin',          'Nonlinear Sciences',                           (SELECT id FROM parent), 10),
  ('nucl-ex',       'Nuclear Experiment',                           (SELECT id FROM parent), 11),
  ('nucl-th',       'Nuclear Theory',                               (SELECT id FROM parent), 12),
  ('quant-ph',      'Quantum Physics',                              (SELECT id FROM parent), 13)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Quantitative Biology subfields
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='q-bio' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('q-bio.BM','Biomolecules',              (SELECT id FROM parent), 1),
  ('q-bio.CB','Cell Behavior',             (SELECT id FROM parent), 2),
  ('q-bio.GN','Genomics',                  (SELECT id FROM parent), 3),
  ('q-bio.MN','Molecular Networks',        (SELECT id FROM parent), 4),
  ('q-bio.NC','Neurons and Cognition',     (SELECT id FROM parent), 5),
  ('q-bio.OT','Other Quantitative Biology',(SELECT id FROM parent), 6),
  ('q-bio.PE','Populations and Evolution', (SELECT id FROM parent), 7),
  ('q-bio.QM','Quantitative Methods',      (SELECT id FROM parent), 8),
  ('q-bio.SC','Subcellular Processes',     (SELECT id FROM parent), 9),
  ('q-bio.TO','Tissues and Organs',        (SELECT id FROM parent), 10)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Quantitative Finance subfields
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='q-fin' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('q-fin.CP','Computational Finance',            (SELECT id FROM parent), 1),
  ('q-fin.EC','Economics (alias of econ.GN)',     (SELECT id FROM parent), 2),
  ('q-fin.GN','General Finance',                  (SELECT id FROM parent), 3),
  ('q-fin.MF','Mathematical Finance',             (SELECT id FROM parent), 4),
  ('q-fin.PM','Portfolio Management',             (SELECT id FROM parent), 5),
  ('q-fin.PR','Pricing of Securities',            (SELECT id FROM parent), 6),
  ('q-fin.RM','Risk Management',                  (SELECT id FROM parent), 7),
  ('q-fin.ST','Statistical Finance',              (SELECT id FROM parent), 8),
  ('q-fin.TR','Trading and Market Microstructure',(SELECT id FROM parent), 9)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- ===========================================
-- Statistics subfields
-- ===========================================
WITH parent AS (SELECT id FROM fields WHERE code='stat' AND parent_id IS NULL)
INSERT INTO fields (code, name, parent_id, sort_order) VALUES
  ('stat.AP','Applications',       (SELECT id FROM parent), 1),
  ('stat.CO','Computation',        (SELECT id FROM parent), 2),
  ('stat.ME','Methodology',        (SELECT id FROM parent), 3),
  ('stat.ML','Machine Learning',   (SELECT id FROM parent), 4),
  ('stat.OT','Other Statistics',   (SELECT id FROM parent), 5),
  ('stat.TH','Statistics Theory (alias of math.ST)', (SELECT id FROM parent), 6)
ON CONFLICT (parent_id, code) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

COMMIT;
