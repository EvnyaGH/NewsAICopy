BEGIN;

CREATE TABLE user_field_interests (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  field_id  UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- prevent duplicates
  UNIQUE (user_id, field_id)
);

-- helpful indexes
CREATE INDEX idx_user_field_interests_user ON user_field_interests(user_id);
CREATE INDEX idx_user_field_interests_field ON user_field_interests(field_id);

COMMIT;
