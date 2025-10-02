# utils/persistence.py
# Persistence utilities for saving arXiv papers into Postgres (SQLAlchemy + tenacity)

import re
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy import create_engine, Table, Column, Integer, Text, JSON, TIMESTAMP, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError
from datetime import datetime

# Regex to extract arXiv id and version from abs/pdf URLs
# Examples:
#   https://arxiv.org/abs/1234.56789v2
#   https://arxiv.org/pdf/1234.56789v1.pdf
ARXIV_ABS_RE = re.compile(r'arxiv\.org/(?:abs|pdf)/(?P<id>\d{4}\.\d{5})(?:v(?P<v>\d+))?')

def parse_arxiv_id_and_version(abs_or_pdf_url: str, fallback_id: str = None):
    """
    Try extracting (arxiv_id, version) from abs/pdf URL.
    If no version is found, default to 1.
    If URL is missing, fall back to 'fallback_id'.
    """
    for url in [abs_or_pdf_url, fallback_id]:
        if not url:
            continue
        m = ARXIV_ABS_RE.search(url)
        if m:
            return m.group("id"), int(m.group("v") or 1)
    # As a last resort, return a synthesized id with version 1
    return (fallback_id or "unknown"), 1


def _mk_engine(pg_url: str):
    """
    Create SQLAlchemy engine with pre_ping to avoid stale connections.
    """
    return create_engine(pg_url, pool_pre_ping=True, future=True)


def _mk_table(metadata: MetaData):
    """
    Define the arxiv_papers table metadata (aligned with migrations/001_create_arxiv_papers.sql).
    """
    return Table(
        "arxiv_papers", metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("arxiv_id", Text, nullable=False),
        Column("version", Integer, nullable=False),
        Column("title", Text),
        Column("authors", JSON),        # list[dict{name, affiliation}]
        Column("affiliations", JSON),   # list[str]
        Column("published_at", TIMESTAMP(timezone=True)),
        Column("updated_at", TIMESTAMP(timezone=True)),
        Column("journal_ref", Text),
        Column("doi", Text),
        Column("primary_category", Text),
        Column("categories", JSON),     # list[str]
        Column("abstract", Text),
        Column("comment", Text),
        Column("abs_url", Text),
        Column("pdf_url", Text),
        Column("links", JSON),          # list[dict{rel, type, href}]
        Column("file_path", Text),
        Column("meta_json", JSON),      # optional: store extra or raw details
        Column("created_at", TIMESTAMP(timezone=True), default=datetime.utcnow),
        Column("updated_at", TIMESTAMP(timezone=True), default=datetime.utcnow),
        extend_existing=True
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=0.5, min=1, max=8),
    retry=retry_if_exception_type((OperationalError,))
)
def save_papers(pg_url: str, records: List[Dict]):
    """
    Atomically save a batch of arXiv paper records with idempotent upsert.
    - Uses a single transaction: either all rows are persisted or none (rollback).
    - Uses ON CONFLICT (arxiv_id, version) DO UPDATE to make writes idempotent.
    - Retries on transient OperationalError with exponential backoff.
    """
    engine = _mk_engine(pg_url)
    metadata = MetaData()
    t = _mk_table(metadata)
    # In production you should manage schema with migrations. This is a safety net for local dev.
    metadata.create_all(engine)

    to_rows = []
    for r in records:
        # Choose the best source to parse arxiv_id/version: abs_url first, then entry['id']
        abs_url = r.get("abs_url") or r.get("arxiv_id")
        arxiv_id, version = parse_arxiv_id_and_version(abs_url, r.get("arxiv_id"))
        row = {
            "arxiv_id": arxiv_id,
            "version": version,
            "title": r.get("title"),
            "authors": r.get("authors"),
            "affiliations": r.get("affiliations"),
            "published_at": r.get("published_at"),
            "updated_at": r.get("updated_at"),
            "journal_ref": r.get("journal_ref"),
            "doi": r.get("doi"),
            "primary_category": r.get("primary_category"),
            "categories": r.get("categories"),
            "abstract": r.get("summary"),
            "comment": r.get("comment"),
            "abs_url": r.get("abs_url"),
            "pdf_url": r.get("pdf_url"),
            "links": r.get("links"),
            "file_path": r.get("file_path"),
            "meta_json": {
                "raw_id": r.get("arxiv_id"),
                "extracted_text_present": bool(r.get("extracted_text")),
            },
            "updated_at": datetime.utcnow(),
        }
        to_rows.append(row)

    # Transaction boundary: all-or-nothing
    with engine.begin() as conn:
        stmt = insert(t).values(to_rows)
        # On conflict, replace the updatable columns to ensure idempotency
        updatable = {
            c: getattr(stmt.excluded, c)
            for c in [
                "title","authors","affiliations","published_at","updated_at",
                "journal_ref","doi","primary_category","categories","abstract",
                "comment","abs_url","pdf_url","links","file_path","meta_json","updated_at"
            ]
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["arxiv_id", "version"],
            set_=updatable
        )
        conn.execute(stmt)
