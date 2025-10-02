# airflow/dags/arxiv_ingestion_dag.py
# Airflow DAG for arXiv ingestion: load config -> fetch -> normalize -> persist.
# - Hot-reload via Airflow Variables (no container restart needed)
# - Atomic, idempotent upsert (no partial writes)
# - Retries on transient DB errors and at task-level
#
# Requirements (add to your requirements.txt if missing):
#   xmltodict, PyYAML, requests, SQLAlchemy, psycopg2-binary, tenacity
#
# Airflow Variables (UI: Admin -> Variables), recommended keys:
#   CONFIG_PATH              (str)  default: "config.yaml" (path inside worker/scheduler)
#   ARXIV_QUERY              (str)  override query in config.yaml, e.g. "cat:cs.LG"
#   ARXIV_START              (int)  override start index (bulk or resume)
#   ARXIV_MAX_RESULTS        (int)  override max results per run, e.g. 50/100
#   ARXIV_EXTRACT_TEXT       (bool) "true"/"false"; default false
#   POSTGRES_URL             (str)  e.g. "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
#
# (Optional) Airflow Connection:
#   Conn Id: postgres_ai_engine (type: Postgres). If POSTGRES_URL Variable not set,
#   the DAG will try to build a SQLAlchemy URL from this connection.

import os
import importlib
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Any, Dict, List

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.hooks.base import BaseHook


@lru_cache
def _get_etl_module():
    """Lazy-load the arXiv ETL helpers so DAG parsing works without extras."""
    try:
        return importlib.import_module("test_arXiv")
    except ModuleNotFoundError as exc:  # pragma: no cover - protective guard
        raise AirflowException(
            "Module 'test_arXiv' is required by arxiv_ingestion_dag but is not "
            "available in the Airflow image. Install the ETL dependencies "
            "(xmltodict, requests, PyYAML, etc.) inside the scheduler/worker "
            "environment."
        ) from exc


@lru_cache
def _get_persistence_module():
    """Lazy-load persistence utilities while providing a helpful error message."""
    try:
        return importlib.import_module("utils.persistence")
    except ModuleNotFoundError as exc:  # pragma: no cover - protective guard
        raise AirflowException(
            "Module 'utils.persistence' is missing. Ensure the ai-engine/utils "
            "package is on PYTHONPATH inside the Airflow container."
        ) from exc


def _get_bool(var_name: str, default: bool) -> bool:
    """Read boolean from Airflow Variable ("true"/"false")."""
    raw = Variable.get(var_name, default_var=str(default)).strip().lower()
    return raw in ("1", "true", "yes", "y", "on")


def resolve_postgres_url() -> str:
    """
    Resolve Postgres URL in order:
    1) Airflow Variable POSTGRES_URL
    2) Airflow Connection 'postgres_ai_engine'
    3) Fallback to local default
    """
    var_url = Variable.get("POSTGRES_URL", default_var=None)
    if var_url:
        return var_url

    # Try connection
    try:
        conn = BaseHook.get_connection("postgres_ai_engine")
        # Build a SQLAlchemy URL
        host = conn.host or "localhost"
        port = conn.port or 5432
        schema = conn.schema or "airflow"
        login = conn.login or "airflow"
        passwd = conn.password or "airflow"
        return f"postgresql+psycopg2://{login}:{passwd}@{host}:{port}/{schema}"
    except Exception:
        pass

    # Fallback (dev)
    return "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"


default_args = {
    "owner": "etl",
    "depends_on_past": False,
    "retries": 2,                        # Task-level retries (DB has its own tenacity retry)
    "retry_delay": timedelta(minutes=3),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="arxiv_ingestion_dag",
    description="Fetch arXiv feed and persist metadata with atomic, idempotent upserts.",
    start_date=datetime(2025, 9, 1),
    schedule_interval="@daily",          # Daily ingestion; switch to @once/manual for bulk
    catchup=False,
    default_args=default_args,
    tags=["arxiv", "etl", "metadata"],
) as dag:

    @task(task_id="load_config")
    def load_cfg() -> Dict[str, Any]:
        """
        Load YAML config and apply runtime overrides from Airflow Variables for hot-reload.
        Returns the effective config dict.
        """
        cfg_path = Variable.get("CONFIG_PATH", default_var="config.yaml")
        etl = _get_etl_module()
        cfg = etl.load_config(cfg_path)

        # Apply hot overrides
        q = Variable.get("ARXIV_QUERY", default_var=None)
        if q:
            cfg.setdefault("arxiv", {})["search_query"] = q

        start_override = Variable.get("ARXIV_START", default_var=None)
        if start_override is not None:
            try:
                cfg.setdefault("arxiv", {})["start"] = int(start_override)
            except ValueError:
                pass

        max_results = Variable.get("ARXIV_MAX_RESULTS", default_var=None)
        if max_results is not None:
            try:
                cfg.setdefault("arxiv", {})["max_results"] = int(max_results)
            except ValueError:
                pass

        extract_text = _get_bool("ARXIV_EXTRACT_TEXT", cfg.get("arxiv", {}).get("extract_text", False))
        cfg.setdefault("arxiv", {})["extract_text"] = extract_text

        # Ensure tmp dir
        tmp_dir = cfg.get("runtime", {}).get("tmp_dir")
        if tmp_dir:
            os.makedirs(tmp_dir, exist_ok=True)

        return cfg

    @task(task_id="fetch_feed")
    def fetch_feed(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch Atom feed and return raw entries.
        """
        etl = _get_etl_module()
        entries = etl.fetch_and_parse(cfg)
        # Small guard: skip DAG if nothing fetched
        if not entries:
            raise AirflowSkipException("No entries fetched from arXiv.")
        return entries

    @task(task_id="normalize_entries")
    def normalize_task(cfg: Dict[str, Any], entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize raw entries into records expected by save_papers().
        """
        etl = _get_etl_module()
        records = etl.normalize_entries(entries, cfg)
        if not records:
            raise AirflowSkipException("No records after normalization.")
        return records

    @task(task_id="persist_metadata")
    def persist_task(cfg: Dict[str, Any], records: List[Dict[str, Any]]) -> int:
        """
        Persist records with atomic, idempotent upsert. Returns saved count.
        """
        pg_url = cfg.get("database", {}).get("postgres_url") or resolve_postgres_url()
        persistence = _get_persistence_module()
        persistence.save_papers(pg_url, records)
        return len(records)

    # Task wiring
    config = load_cfg()
    raw_entries = fetch_feed(config)
    normalized = normalize_task(config, raw_entries)
    _ = persist_task(config, normalized)
