"""
ArXiv ETL DAG
Automated pipeline to fetch arXiv papers, extract metadata, and store in PostgreSQL

This DAG orchestrates the following workflow:
1. Validate environment and configuration
2. Fetch papers from arXiv API based on category/query
3. Parse and normalize XML metadata
4. Extract authors, categories, and links
5. Perform idempotent upserts to PostgreSQL
6. Generate execution reports and cleanup

Schedule: Configurable via config.yaml (default: daily)
Airflow Version: 2.7+
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.exceptions import AirflowException
import os
import sys
from typing import Dict, List, Any, Optional

# Add project path to Python path for imports
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, PROJECT_ROOT)

# Import utility functions from test_arXiv.py
from utils.test_arXiv import (
    load_config,
    ensure_dir,
    fetch_and_parse,
    normalize_entries,
    persist_records,
)

# Configuration
CONFIG_PATH = os.getenv("CONFIG_PATH", os.path.join(PROJECT_ROOT, "config/arXiv_postgre_config.yaml"))
DEFAULT_SCHEDULE = "0 2 * * *"  # 2 AM daily by default


def get_schedule_from_config() -> str:
    """
    Load schedule from config.yaml if available, otherwise use default
    
    Returns:
        Cron expression string for DAG schedule
    """
    try:
        if os.path.exists(CONFIG_PATH):
            config = load_config(CONFIG_PATH)
            hours = config.get("schedule_hours", 24)
            # Convert hours to cron: every N hours at minute 0
            if hours == 24:
                return "0 2 * * *"  # Daily at 2 AM
            elif hours == 12:
                return "0 */12 * * *"  # Every 12 hours
            elif hours == 6:
                return "0 */6 * * *"  # Every 6 hours
            else:
                return f"0 */{hours} * * *"  # Every N hours
    except Exception as e:
        print(f"[WARN] Could not load schedule from config: {e}")
    
    return DEFAULT_SCHEDULE


# Default arguments for all tasks
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['data-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=2),
}


@dag(
    dag_id='arxiv_papers_etl',
    default_args=default_args,
    description='Fetch, parse, and store arXiv papers metadata in PostgreSQL',
    schedule=get_schedule_from_config(),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['arxiv', 'etl', 'papers', 'ai', 'postgresql'],
    doc_md=__doc__,
)
def arxiv_etl_pipeline():
    """
    Main DAG orchestrating arXiv paper ingestion pipeline
    Uses TaskFlow API for clean task dependencies and data passing
    """

    @task()
    def validate_environment() -> Dict[str, Any]:
        """
        Task 1: Validate runtime environment and configuration
        
        Validates:
        - Config file existence and structure
        - PostgreSQL connection parameters
        - arXiv API configuration
        - Required directories
        
        Returns:
            Dict containing validated configuration and paths
            
        Raises:
            FileNotFoundError: If config file is missing
            ValueError: If required config fields are missing
            AirflowException: If validation fails
        """
        print("[INFO] ==> Starting environment validation")
        
        # Check config file exists
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(
                f"Configuration file not found: {CONFIG_PATH}\n"
                f"Please ensure arXiv_postgre_config.yaml exists in the project root"
            )
        
        print(f"[INFO] Config file found: {CONFIG_PATH}")
        
        # Load and validate configuration
        try:
            config = load_config(CONFIG_PATH)
        except Exception as e:
            raise AirflowException(f"Failed to load config file: {str(e)}")
        
        # Validate required sections
        required_sections = ['arxiv', 'postgres', 'field_mapping']
        missing_sections = [s for s in required_sections if s not in config]
        if missing_sections:
            raise ValueError(
                f"Missing required config sections: {', '.join(missing_sections)}"
            )
        
        # Validate arXiv configuration
        arxiv_config = config['arxiv']
        required_arxiv_fields = ['base_url', 'search_query', 'max_results']
        missing_fields = [f for f in required_arxiv_fields if not arxiv_config.get(f)]
        if missing_fields:
            raise ValueError(
                f"Missing required arXiv config fields: {', '.join(missing_fields)}"
            )
        
        print(f"[INFO] arXiv Query: {arxiv_config['search_query']}")
        print(f"[INFO] Max Results: {arxiv_config['max_results']}")
        print(f"[INFO] Start Index: {arxiv_config.get('start', 0)}")
        
        # Validate PostgreSQL configuration
        postgres_url = config['postgres'].get('url') or os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN')
        if not postgres_url:
            raise ValueError(
                "PostgreSQL URL not found in config.postgres.url or AIRFLOW__DATABASE__SQL_ALCHEMY_CONN env var"
            )
        
        # Mask password in logs for security
        if '@' in postgres_url:
            safe_url = postgres_url.split('@')[1]
            print(f"[INFO] Database: {safe_url}")
        else:
            print("[INFO] Database connection configured")
        
        # Setup temporary directory for PDF extraction (if enabled)
        tmp_dir = config.get('runtime', {}).get('tmp_dir', '/tmp/arxiv_etl')
        ensure_dir(tmp_dir)
        print(f"[INFO] Temporary directory: {tmp_dir}")
        
        # Check PDF extraction setting
        extract_text = arxiv_config.get('extract_text', False)
        if extract_text:
            print("[INFO] PDF text extraction: ENABLED")
        else:
            print("[INFO] PDF text extraction: DISABLED (metadata only)")
        
        print("[INFO] ==> Environment validation: PASSED")
        
        return {
            'config_path': CONFIG_PATH,
            'tmp_dir': tmp_dir,
            'arxiv_query': arxiv_config['search_query'],
            'max_results': arxiv_config['max_results'],
            'extract_text': extract_text,
        }

    @task()
    def fetch_arxiv_papers(env_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 2: Fetch papers from arXiv API
        
        Connects to arXiv Atom feed API and retrieves papers based on
        the search query (category or custom query) from config
        
        Args:
            env_config: Environment configuration from validation task
            
        Returns:
            Dict containing raw XML entries and fetch statistics
            
        Raises:
            AirflowException: If API request fails or no data retrieved
        """
        print("[INFO] ==> Starting arXiv data fetch")
        
        # Load configuration
        config_path = env_config['config_path']
        config = load_config(config_path)
        
        print(f"[INFO] Querying arXiv API: {config['arxiv']['base_url']}")
        print(f"[INFO] Search query: {env_config['arxiv_query']}")
        
        # Fetch data from arXiv API
        try:
            entries = fetch_and_parse(config)
        except Exception as e:
            raise AirflowException(f"Failed to fetch arXiv data: {str(e)}")
        
        if not entries:
            raise AirflowException(
                "No papers retrieved from arXiv API. "
                "Check your search query or arXiv API availability"
            )
        
        print(f"[INFO] ==> Successfully fetched {len(entries)} paper entries")
        
        # Log sample of retrieved paper IDs
        sample_size = min(5, len(entries))
        for i, entry in enumerate(entries[:sample_size]):
            paper_id = entry.get('id', 'N/A')
            title = entry.get('title', 'N/A')
            print(f"[INFO] Sample [{i+1}]: {paper_id} - {title[:60]}...")
        
        return {
            'entries': entries,
            'config': config,
            'fetch_count': len(entries),
            'query': env_config['arxiv_query'],
            'timestamp': datetime.now().isoformat(),
        }

    @task()
    def parse_and_normalize(fetch_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 3: Parse XML and normalize paper metadata
        
        Processes raw arXiv XML entries and extracts:
        - Paper ID, title, summary
        - Authors and affiliations
        - Categories (primary and all)
        - Links (abstract URL, PDF URL)
        - Publication/update dates
        
        Args:
            fetch_result: Raw entries from fetch task
            
        Returns:
            Dict containing normalized records and statistics
            
        Raises:
            AirflowException: If normalization fails completely
        """
        print("[INFO] ==> Starting data normalization and parsing")
        
        entries = fetch_result['entries']
        config = fetch_result['config']
        
        print(f"[INFO] Processing {len(entries)} entries...")
        print("[INFO] Extracting: authors, categories, links, metadata")
        
        # Normalize all entries
        try:
            normalized_records = normalize_entries(entries, config)
        except Exception as e:
            raise AirflowException(f"Normalization failed: {str(e)}")
        
        if not normalized_records:
            raise AirflowException(
                "All entries failed normalization. Check XML structure or field mapping"
            )
        
        # Data quality validation
        valid_records = []
        invalid_count = 0
        
        for record in normalized_records:
            # A valid record must have at least: id, title, and authors
            if record.get('id') and record.get('title') and record.get('authors'):
                valid_records.append(record)
            else:
                invalid_count += 1
                paper_id = record.get('id', 'UNKNOWN')
                print(f"[WARN] Invalid record filtered: {paper_id}")
        
        # Calculate statistics
        total_processed = len(normalized_records)
        valid_count = len(valid_records)
        quality_rate = (valid_count / total_processed * 100) if total_processed > 0 else 0
        
        print(f"[INFO] ==> Normalization complete")
        print(f"[INFO] Total processed: {total_processed}")
        print(f"[INFO] Valid records: {valid_count}")
        print(f"[INFO] Invalid records: {invalid_count}")
        print(f"[INFO] Data quality: {quality_rate:.2f}%")
        
        # Log sample normalized record structure
        if valid_records:
            sample = valid_records[0]
            print(f"[INFO] Sample record structure:")
            print(f"[INFO]   - ID: {sample.get('id')}")
            print(f"[INFO]   - Title: {sample.get('title', '')[:60]}...")
            print(f"[INFO]   - Authors: {len(sample.get('authors', []))}")
            print(f"[INFO]   - Categories: {len(sample.get('categories', []))}")
            print(f"[INFO]   - Has PDF URL: {bool(sample.get('pdf_url'))}")
        
        return {
            'records': valid_records,
            'config': config,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'total_processed': total_processed,
            'quality_rate': quality_rate,
        }

    @task()
    def load_to_database(transform_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 4: Load normalized data to PostgreSQL
        
        Performs idempotent upserts to arxiv_papers table.
        If a paper already exists (by arXiv ID), it will be updated.
        
        Args:
            transform_result: Normalized records from parse task
            
        Returns:
            Dict containing load statistics
            
        Raises:
            AirflowException: If database operations fail
        """
        print("[INFO] ==> Starting database load")
        
        records = transform_result['records']
        config = transform_result['config']
        
        if not records:
            print("[WARN] No records to load, skipping database operation")
            return {
                'loaded_count': 0,
                'status': 'SKIPPED',
                'message': 'No valid records to load'
            }
        
        pg_url = config.get("database", {}).get("DATABASE_URL") or os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://zara_user:zara_password@postgres:5432/zara_airflow"
            )
        print(f'[INFO] Using PostgreSQL URL: {pg_url}')
        
        print(f"[INFO] Preparing to load {len(records)} records to PostgreSQL")
        
        # Perform database upsert
        try:
            persist_records(records, config)
        except Exception as e:
            raise AirflowException(f"Database load failed: {str(e)}")
        
        print(f"[INFO] ==> Successfully loaded {len(records)} records")
        print("[INFO] Operation: Idempotent UPSERT (insert or update)")
        print("[INFO] Target table: arxiv_papers")
        
        return {
            'loaded_count': len(records),
            'table': 'arxiv_papers',
            'operation': 'UPSERT',
            'timestamp': datetime.now().isoformat(),
            'status': 'SUCCESS',
        }

    @task()
    def generate_execution_report(
        env_config: Dict[str, Any],
        fetch_result: Dict[str, Any],
        transform_result: Dict[str, Any],
        load_result: Dict[str, Any],
        **context
    ) -> str:
        """
        Task 5: Generate comprehensive execution report
        
        Aggregates statistics from all pipeline stages and creates
        a detailed report for monitoring and auditing purposes
        
        Args:
            env_config: Environment configuration
            fetch_result: Fetch task statistics
            transform_result: Transform task statistics
            load_result: Load task statistics
            context: Airflow context
            
        Returns:
            Formatted execution report string
        """
        print("[INFO] ==> Generating execution report")
        
        # Extract execution context
        execution_date = context['execution_date']
        dag_run_id = context['run_id']
        logical_date = context['logical_date']
        
        # Compile statistics
        fetch_count = fetch_result['fetch_count']
        valid_count = transform_result['valid_count']
        invalid_count = transform_result['invalid_count']
        quality_rate = transform_result['quality_rate']
        loaded_count = load_result['loaded_count']
        
        # Calculate pipeline efficiency
        fetch_to_load_rate = (loaded_count / fetch_count * 100) if fetch_count > 0 else 0
        
        # Create detailed report
        report = f"""
{'='*70}
ARXIV ETL PIPELINE - EXECUTION REPORT
{'='*70}

EXECUTION METADATA
  Run ID:           {dag_run_id}
  Execution Date:   {execution_date}
  Logical Date:     {logical_date}
  Completed:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURATION
  arXiv Query:      {env_config['arxiv_query']}
  Max Results:      {env_config['max_results']}
  PDF Extraction:   {'Enabled' if env_config['extract_text'] else 'Disabled'}

PIPELINE STATISTICS
  Stage 1 - Fetch:
    Papers Retrieved:       {fetch_count}
    API Query:              {fetch_result['query']}
    
  Stage 2 - Transform:
    Total Processed:        {transform_result['total_processed']}
    Valid Records:          {valid_count}
    Invalid Records:        {invalid_count}
    Data Quality Rate:      {quality_rate:.2f}%
    
  Stage 3 - Load:
    Records Loaded:         {loaded_count}
    Database Table:         {load_result['table']}
    Operation Type:         {load_result['operation']}
    Load Status:            {load_result['status']}

PIPELINE EFFICIENCY
  Fetch → Load Rate:        {fetch_to_load_rate:.2f}%
  Overall Status:           {'✓ SUCCESS' if load_result['status'] == 'SUCCESS' else '✗ FAILED'}

{'='*70}
        """
        
        print(report)
        
        # Store report in Airflow Variables for monitoring dashboard
        report_key = f"arxiv_etl_report_{context['ds_nodash']}"
        Variable.set(
            report_key,
            {
                'dag_run_id': dag_run_id,
                'execution_date': str(execution_date),
                'fetch_count': fetch_count,
                'loaded_count': loaded_count,
                'quality_rate': quality_rate,
                'status': load_result['status'],
                'query': env_config['arxiv_query'],
            },
            serialize_json=True
        )
        
        print(f"[INFO] Report saved to Airflow Variable: {report_key}")
        
        # Store latest run stats for quick access
        Variable.set(
            "arxiv_etl_latest_run",
            {
                'timestamp': datetime.now().isoformat(),
                'loaded_count': loaded_count,
                'quality_rate': quality_rate,
            },
            serialize_json=True
        )
        
        print("[INFO] ==> Report generation complete")
        
        return report

    @task()
    def data_quality_check(transform_result: Dict[str, Any]) -> bool:
        """
        Task 6: Perform data quality validation
        
        Validates that the pipeline meets minimum quality thresholds
        
        Args:
            transform_result: Transform statistics
            
        Returns:
            True if quality checks pass
            
        Raises:
            AirflowException: If quality thresholds not met
        """
        print("[INFO] ==> Running data quality checks")
        
        quality_rate = transform_result['quality_rate']
        valid_count = transform_result['valid_count']
        
        # Define quality thresholds
        MIN_QUALITY_RATE = 80.0  # Minimum 80% valid records
        MIN_RECORD_COUNT = 1     # At least 1 valid record
        
        print(f"[INFO] Quality Rate: {quality_rate:.2f}% (threshold: {MIN_QUALITY_RATE}%)")
        print(f"[INFO] Valid Count: {valid_count} (threshold: {MIN_RECORD_COUNT})")
        
        # Check quality thresholds
        if quality_rate < MIN_QUALITY_RATE:
            raise AirflowException(
                f"Data quality check FAILED: Quality rate {quality_rate:.2f}% "
                f"is below threshold {MIN_QUALITY_RATE}%"
            )
        
        if valid_count < MIN_RECORD_COUNT:
            raise AirflowException(
                f"Data quality check FAILED: Only {valid_count} valid records "
                f"(minimum required: {MIN_RECORD_COUNT})"
            )
        
        print("[INFO] ==> Data quality checks: PASSED ✓")
        return True

    # Task: Cleanup temporary files
    cleanup_temp = BashOperator(
        task_id='cleanup_temp_files',
        bash_command="""
        echo "[INFO] Cleaning up temporary files..."
        rm -rf /tmp/arxiv_etl/*.pdf 2>/dev/null || true
        echo "[INFO] Cleanup complete"
        """,
        trigger_rule='all_done',  # Run even if upstream tasks fail
    )

    # ============================================================
    # DEFINE TASK DEPENDENCIES (TaskFlow API)
    # ============================================================
    
    # Stage 1: Environment validation
    env_config = validate_environment()
    
    # Stage 2: Fetch papers from arXiv
    fetch_result = fetch_arxiv_papers(env_config)
    
    # Stage 3: Parse and normalize metadata
    transform_result = parse_and_normalize(fetch_result)
    
    # Stage 4: Data quality validation (branching checkpoint)
    quality_check = data_quality_check(transform_result)
    
    # Stage 5: Load to database (only if quality check passes)
    load_result = load_to_database(transform_result)
    
    # Stage 6: Generate execution report
    report = generate_execution_report(
        env_config,
        fetch_result,
        transform_result,
        load_result
    )
    
    # Stage 7: Cleanup
    # Set dependencies: quality check must pass before load
    quality_check >> load_result
    
    # Report and cleanup happen after load completes
    load_result >> report >> cleanup_temp


# Instantiate the DAG
arxiv_dag = arxiv_etl_pipeline()