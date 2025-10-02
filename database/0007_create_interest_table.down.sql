BEGIN;

-- Drop the junction table first (depends on users + fields)
DROP TABLE IF EXISTS user_field_interests;

COMMIT;
