"""Airflow DAG for ingesting and persisting arXiv paper metadata."""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pendulum
from airflow import DAG
from airflow.sdk import Variable, task
from sqlalchemy import and_, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Ensure project root on path so we can import database models when executed by Airflow
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database import AuthorProfile, Paper, PaperAuthor  # noqa: E402

log = logging.getLogger(__name__)

DAG_ID = "arxiv_metadata_ingestion_dag"
DEFAULT_ARGS = {
    "owner": "ai-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,
}


@dataclass
class IngestionConfig:
    """Configuration required for metadata ingestion."""

    categories: List[str]
    max_results: int
    batch_size: int
    database_url: str
    storage_dir: str
    api_delay_seconds: float
    api_max_retries: int
    api_timeout: int

    @classmethod
    def from_airflow(cls) -> "IngestionConfig":
        """Load ingestion configuration from Airflow Variables or environment."""

        raw_categories = Variable.get("ARXIV_CATEGORIES", default_var="cs.AI")
        categories = [cat.strip() for cat in raw_categories.split(",") if cat.strip()]
        if not categories:
            raise ValueError("No arXiv categories configured. Set ARXIV_CATEGORIES variable.")

        max_results = int(Variable.get("ARXIV_MAX_RESULTS", default_var="25"))
        batch_size = int(Variable.get("ARXIV_BATCH_SIZE", default_var="10"))
        api_delay_seconds = float(Variable.get("ARXIV_API_DELAY", default_var="3"))
        api_max_retries = int(Variable.get("ARXIV_MAX_RETRIES", default_var="3"))
        api_timeout = int(Variable.get("ARXIV_TIMEOUT", default_var="30"))

        storage_dir = Variable.get("PAPER_STORAGE_DIR", default_var="/opt/airflow/data/papers")
        os.makedirs(storage_dir, exist_ok=True)

        database_url = Variable.get("DATABASE_URL", default_var=os.getenv("DATABASE_URL"))
        if not database_url:
            raise ValueError("DATABASE_URL must be configured as an Airflow Variable or environment variable.")

        return cls(
            categories=categories,
            max_results=max_results,
            batch_size=batch_size,
            database_url=database_url,
            storage_dir=storage_dir,
            api_delay_seconds=api_delay_seconds,
            api_max_retries=api_max_retries,
            api_timeout=api_timeout,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return JSON-serialisable representation for XCom."""

        return {
            "categories": self.categories,
            "max_results": self.max_results,
            "batch_size": self.batch_size,
            "database_url": self.database_url,
            "storage_dir": self.storage_dir,
            "api_delay_seconds": self.api_delay_seconds,
            "api_max_retries": self.api_max_retries,
            "api_timeout": self.api_timeout,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "IngestionConfig":
        """Rehydrate configuration from task payload."""

        return cls(
            categories=list(payload.get("categories", [])),
            max_results=int(payload.get("max_results", 0)),
            batch_size=int(payload.get("batch_size", 10)),
            database_url=str(payload.get("database_url")),
            storage_dir=str(payload.get("storage_dir")),
            api_delay_seconds=float(payload.get("api_delay_seconds", 3)),
            api_max_retries=int(payload.get("api_max_retries", 3)),
            api_timeout=int(payload.get("api_timeout", 30)),
        )


def _safe_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            log.warning("Unable to parse datetime from value '%s'", value)
            return None


def _derive_pdf_path(base_dir: str, arxiv_id: str) -> str:
    safe_id = arxiv_id.replace("/", "_")
    return str(Path(base_dir) / f"{safe_id}.pdf")


def _serialise_author(author: Any) -> Dict[str, Optional[str]]:
    name = getattr(author, "name", None)
    affiliation = getattr(author, "affiliation", None)
    return {
        "name": name.strip() if isinstance(name, str) else name,
        "affiliation": affiliation.strip() if isinstance(affiliation, str) else affiliation,
    }


def _serialise_link(link: Any) -> Dict[str, Optional[str]]:
    return {
        "href": getattr(link, "href", None),
        "title": getattr(link, "title", None),
        "rel": getattr(link, "rel", None),
    }


def _extract_version(arxiv_id: str) -> Optional[int]:
    if "v" in arxiv_id:
        version_part = arxiv_id.split("v")[-1]
        if version_part.isdigit():
            return int(version_part)
    return None


def _paper_metadata_from_result(result: Any, storage_dir: str) -> Dict[str, Any]:
    arxiv_id = str(getattr(result, "entry_id", "")).rsplit("/", 1)[-1]
    if not arxiv_id:
        short_id = getattr(result, "get_short_id", None)
        if callable(short_id):
            arxiv_id = short_id(include_version=True)  # type: ignore[arg-type]

    title = getattr(result, "title", "").strip()
    summary = getattr(result, "summary", None)
    summary = summary.strip() if isinstance(summary, str) else summary

    published = getattr(result, "published", None)
    updated = getattr(result, "updated", None)

    primary_category = getattr(result, "primary_category", None)
    categories = list(getattr(result, "categories", []) or [])

    paper_links = [link for link in getattr(result, "links", []) or []]

    authors = [
        _serialise_author(author)
        for author in getattr(result, "authors", []) or []
        if getattr(author, "name", None)
    ]

    metadata = {
        "arxiv_id": arxiv_id,
        "version": _extract_version(arxiv_id),
        "title": title,
        "abstract": summary,
        "doi": getattr(result, "doi", None),
        "journal_ref": getattr(result, "journal_ref", None),
        "comment": getattr(result, "comment", None),
        "primary_category": primary_category,
        "categories": categories,
        "authors": authors,
        "links": [_serialise_link(link) for link in paper_links],
        "pdf_url": getattr(result, "pdf_url", None),
        "pdf_path": _derive_pdf_path(storage_dir, arxiv_id),
        "published": published.isoformat() if hasattr(published, "isoformat") else None,
        "updated": updated.isoformat() if hasattr(updated, "isoformat") else None,
    }

    # submitted date defaults to published when available
    metadata["submitted"] = metadata["published"]
    return metadata


def _build_search_query(categories: Iterable[str]) -> str:
    terms = [f"cat:{category}" for category in categories]
    return " OR ".join(terms)


def _get_or_create_author(session: Session, name: str, affiliation: Optional[str]) -> AuthorProfile:
    conditions = [AuthorProfile.name == name]
    if affiliation:
        conditions.append(AuthorProfile.affiliation == affiliation)
    else:
        conditions.append(AuthorProfile.affiliation.is_(None))

    stmt = select(AuthorProfile).where(and_(*conditions)).limit(1)
    author = session.execute(stmt).scalar_one_or_none()
    if author:
        return author

    author = AuthorProfile(name=name, affiliation=affiliation)
    session.add(author)
    session.flush()
    return author


def _update_paper_relationships(session: Session, paper: Paper, authors: List[Dict[str, Optional[str]]]) -> None:
    for paper_author in list(paper.paper_authors):
        session.delete(paper_author)
    session.flush()

    for order, author_data in enumerate(authors, start=1):
        author_name = author_data.get("name")
        if not author_name:
            continue
        author = _get_or_create_author(session, author_name, author_data.get("affiliation"))
        paper_author = PaperAuthor(
            paper=paper,
            author=author,
            author_order=order,
            corresponding=order == 1,
        )
        session.add(paper_author)


def _apply_metadata_to_paper(paper: Paper, metadata: Dict[str, Any]) -> None:
    paper.title = metadata.get("title") or paper.title
    paper.abstract = metadata.get("abstract")
    paper.doi = metadata.get("doi")
    paper.arxiv_id = metadata.get("arxiv_id")
    paper.pdf_url = metadata.get("pdf_url")
    paper.pdf_path = metadata.get("pdf_path")
    paper.published_date = _safe_datetime(metadata.get("published"))
    paper.submitted_date = _safe_datetime(metadata.get("submitted"))
    paper.updated_date = _safe_datetime(metadata.get("updated"))
    paper.keywords = metadata.get("categories") or []
    paper.status = "metadata_saved"

    metadata_payload = dict(paper.processing_metadata or {})
    metadata_payload.update(
        {
            "journal_reference": metadata.get("journal_ref"),
            "arxiv_comment": metadata.get("comment"),
            "arxiv_primary_category": metadata.get("primary_category"),
            "arxiv_categories": metadata.get("categories"),
            "arxiv_links": metadata.get("links"),
            "arxiv_version": metadata.get("version"),
        }
    )
    paper.processing_metadata = metadata_payload


@task(task_id="load_ingestion_config")
def load_ingestion_config() -> Dict[str, Any]:
    """Load ingestion configuration for downstream tasks."""

    config = IngestionConfig.from_airflow()
    log.info(
        "Loaded ingestion config: categories=%s, max_results=%s, batch_size=%s",
        config.categories,
        config.max_results,
        config.batch_size,
    )
    return config.to_dict()


@task(task_id="fetch_arxiv_metadata", retries=3, retry_delay=timedelta(minutes=2))
def fetch_arxiv_metadata(config_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch paper metadata from arXiv for configured categories."""

    import arxiv

    config = IngestionConfig.from_dict(config_payload)
    query = _build_search_query(config.categories)
    log.info("Querying arXiv with query='%s' max_results=%s", query, config.max_results)

    search = arxiv.Search(
        query=query,
        max_results=config.max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    client = arxiv.Client(
        page_size=config.batch_size,
        delay_seconds=config.api_delay_seconds,
        num_retries=config.api_max_retries,
    )

    results: List[Dict[str, Any]] = []
    for result in client.results(search):
        metadata = _paper_metadata_from_result(result, config.storage_dir)
        results.append(metadata)
        log.debug("Fetched metadata for %s", metadata.get("arxiv_id"))

    log.info("Fetched %d papers from arXiv", len(results))
    return results


@task(task_id="save_paper_metadata", retries=3, retry_delay=timedelta(minutes=2))
def save_paper_metadata(config_payload: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Persist fetched metadata to the database with transactional safety."""

    if not papers:
        log.info("No papers to persist.")
        return {"stored": 0, "updated": 0, "skipped": 0}

    config = IngestionConfig.from_dict(config_payload)
    engine = create_engine(config.database_url, pool_pre_ping=True, future=True)

    stored = 0
    updated = 0
    skipped = 0

    try:
        with Session(engine) as session:
            with session.begin():
                for paper_data in papers:
                    arxiv_id = paper_data.get("arxiv_id")
                    if not arxiv_id:
                        skipped += 1
                        continue

                    stmt = select(Paper).where(Paper.arxiv_id == arxiv_id).limit(1)
                    paper = session.execute(stmt).scalar_one_or_none()

                    if paper is None:
                        paper = Paper(
                            title=paper_data.get("title") or "Untitled",
                            arxiv_id=arxiv_id,
                            abstract=paper_data.get("abstract"),
                        )
                        session.add(paper)
                        stored += 1
                    else:
                        updated += 1

                    _apply_metadata_to_paper(paper, paper_data)
                    _update_paper_relationships(session, paper, paper_data.get("authors", []))

    except SQLAlchemyError as exc:
        log.error("Database error while saving metadata: %s", exc)
        raise

    summary = {"stored": stored, "updated": updated, "skipped": skipped}
    log.info("Metadata persistence summary: %s", json.dumps(summary))
    return summary


with DAG(
    dag_id=DAG_ID,
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["arxiv", "metadata", "etl"],
) as dag:
    config_payload = load_ingestion_config()
    fetched_metadata = fetch_arxiv_metadata(config_payload)
    save_paper_metadata(config_payload, fetched_metadata)
