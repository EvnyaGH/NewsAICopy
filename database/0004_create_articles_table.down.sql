BEGIN;

-- Drop indexes
DROP INDEX IF EXISTS idx_article_prompts_prompt_id;
DROP INDEX IF EXISTS idx_article_prompts_article_id;
DROP INDEX IF EXISTS idx_paper_authors_author_id;
DROP INDEX IF EXISTS idx_paper_authors_paper_id;
DROP INDEX IF EXISTS idx_article_blocks_article_id;
DROP INDEX IF EXISTS idx_articles_paper_id;

-- Drop tables
DROP TABLE IF EXISTS article_prompts;
DROP TABLE IF EXISTS paper_authors;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS article_blocks;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS author_profiles;

-- Drop enums
DROP TYPE IF EXISTS prompt_type;
DROP TYPE IF EXISTS block_type;

COMMIT;
