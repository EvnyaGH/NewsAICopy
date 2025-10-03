# airflow/dags/arxiv_ingestion_dag_v2.py
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.exceptions import AirflowSkipException
from airflow.hooks.base import BaseHook

current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(target_dir)

from utils.test_arXiv import load_config, fetch_and_parse, normalize_entries
from utils.persistence import save_papers


def _get_bool(var_name: str, default: bool) -> bool:
    raw = Variable.get(var_name, default_var=str(default)).strip().lower()
    return raw in ("1", "true", "yes", "y", "on")


def resolve_postgres_url() -> str:
    var_url = Variable.get("POSTGRES_URL", default_var=None)
    if var_url:
        return var_url
    try:
        conn = BaseHook.get_connection("postgres_ai_engine")
        host = conn.host or "localhost"
        port = conn.port or 5432
        schema = conn.schema or "airflow"
        login = conn.login or "airflow"
        passwd = conn.password or "airflow"
        return f"postgresql+psycopg2://{login}:{passwd}@{host}:{port}/{schema}"
    except Exception:
        pass
    return "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"


with DAG(
    dag_id="arxiv_ingestion_dag",
    description="Fetch arXiv feed and persist metadata with atomic, idempotent upserts.",
    start_date=datetime(2025, 9, 1),
    schedule="@daily",
    catchup=False,
    tags=["arxiv", "etl", "metadata"],
    default_args={
        "owner": "etl",
        "depends_on_past": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=3),
        "email_on_failure": False,
        "email_on_retry": False,
    },
) as dag:

    @task
    def load_cfg() -> Dict[str, Any]:
        cfg_path = Variable.get("CONFIG_PATH", default_var="config.yaml")
        cfg = load_config(cfg_path)

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

        tmp_dir = cfg.get("runtime", {}).get("tmp_dir")
        if tmp_dir:
            os.makedirs(tmp_dir, exist_ok=True)

        return cfg

    @task
    def fetch_feed(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries = fetch_and_parse(cfg)
        if not entries:
            raise AirflowSkipException("No entries fetched from arXiv.")
        return entries

    @task
    def normalize_task(cfg: Dict[str, Any], entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        records = normalize_entries(entries, cfg)
        if not records:
            raise AirflowSkipException("No records after normalization.")
        return records

    @task
    def persist_task(cfg: Dict[str, Any], records: List[Dict[str, Any]]) -> int:
        pg_url = cfg.get("database", {}).get("postgres_url") or resolve_postgres_url()
        save_papers(pg_url, records)
        return len(records)

    # TaskFlow wiring (新版 TaskFlow API 风格)
    cfg = load_cfg()
    raw_entries = fetch_feed(cfg)
    normalized = normalize_task(cfg, raw_entries)
    persisted_count = persist_task(cfg, normalized)
