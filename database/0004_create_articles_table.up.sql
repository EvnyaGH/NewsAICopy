BEGIN;

-- UUID generator
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 0) Enums

DROP TYPE IF EXISTS block_type CASCADE;
CREATE TYPE block_type AS ENUM ('title', 'paragraph', 'subheading', 'quote', 'image');

DROP TYPE IF EXISTS prompt_type CASCADE;
CREATE TYPE prompt_type AS ENUM ('article', 'image', 'video', 'text-to-speech');



-- 1) Core entities
CREATE TABLE author_profiles
(
    id          UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL,
    affiliation TEXT,
    email       TEXT,
    bio         TEXT,
    orcid       TEXT UNIQUE,
    website     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE papers
(
    id               UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    title            TEXT        NOT NULL,
    abstract         TEXT,
    doi              TEXT,
    arxiv_id         TEXT,
    primary_subject  TEXT,
    primary_category TEXT,
    subjects         TEXT[],
    categories       TEXT[],
    pdf_url          TEXT,
    published_date   TIMESTAMPTZ,
    submitted_date   TIMESTAMPTZ,
    updated_date     TIMESTAMPTZ,
    status           TEXT,
    extracted_text   TEXT,
    text_chunks      JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE articles
(
    id                 UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    paper_id           UUID        NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    title              TEXT        NOT NULL,
    slug               TEXT        NOT NULL UNIQUE,
    status             TEXT,
    featured_image_url TEXT,
    is_edited          BOOLEAN     NOT NULL DEFAULT FALSE,
    view_count         BIGINT      NOT NULL DEFAULT 0,
    engagement_metrics JSONB,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE article_blocks
(
    id          UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    article_id  UUID        NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    block_type  block_type  NOT NULL,
    content     TEXT,
    order_index INTEGER     NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_article_block_order UNIQUE (article_id, order_index)
);

CREATE TABLE prompts
(
    id                      UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    name                    TEXT        NOT NULL,
    type                    prompt_type NOT NULL,
    image_generation_prompt TEXT,
    description             TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE paper_authors
(
    id            UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    paper_id      UUID        NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    author_id     UUID        NOT NULL REFERENCES author_profiles (id) ON DELETE RESTRICT,
    author_order  INTEGER,
    corresponding BOOLEAN     NOT NULL DEFAULT FALSE,
    contribution  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_paper_author UNIQUE (paper_id, author_id),
    CONSTRAINT uq_paper_author_order UNIQUE (paper_id, author_order)
);

CREATE TABLE article_prompts
(
    id         UUID PRIMARY KEY     DEFAULT gen_random_uuid(),
    article_id UUID        NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    prompt_id  UUID        NOT NULL REFERENCES prompts (id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_article_prompt UNIQUE (article_id, prompt_id)
);

-- 2) Indexes
CREATE INDEX idx_articles_paper_id ON articles (paper_id);
CREATE INDEX idx_article_blocks_article_id ON article_blocks (article_id);
CREATE INDEX idx_paper_authors_paper_id ON paper_authors (paper_id);
CREATE INDEX idx_paper_authors_author_id ON paper_authors (author_id);
CREATE INDEX idx_article_prompts_article_id ON article_prompts (article_id);
CREATE INDEX idx_article_prompts_prompt_id ON article_prompts (prompt_id);

COMMIT;
