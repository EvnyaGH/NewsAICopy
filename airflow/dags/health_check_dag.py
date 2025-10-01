"""
Health Check DAG
================

Production health check DAG for Zara ETL system.
Validates system components, configuration, and Airflow Variables.

This DAG implements the foundation for reliable scheduling by:
1. Validating all system components are operational
2. Testing configuration and variable access
3. Verifying external service connectivity
4. Ensuring database connectivity and migrations
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from airflow import DAG
from airflow.sdk import task
from airflow.sdk import Variable
import psycopg2

# Configure logging
log = logging.getLogger(__name__)

# DAG Configuration
DAG_ID = "health_check_dag"
DEFAULT_ARGS = {
    "owner": "zara-etl-platform",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,
}

# Health Check Configuration
REQUIRED_VARIABLES = [
    # Core system variables
    "ENVIRONMENT",
    "LOG_LEVEL", 
    "DATABASE_URL",
    
    # arXiv Ingestion (Sprint 2 - Essential)
    "ARXIV_MAX_RESULTS",
    "ARXIV_CATEGORIES",
    "ARXIV_BATCH_SIZE",
    
    # Feature Flags (Sprint 2)
    "ENABLE_ARXIV_INGESTION",
]

OPTIONAL_VARIABLES = [
    # API Keys (for future sprints)
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    
    # arXiv Advanced Config
    "ARXIV_API_DELAY",
    "ARXIV_MAX_RETRIES",
    "ARXIV_TIMEOUT",
    
    # Processing Configuration
    "DEFAULT_MODEL",
    "BATCH_SIZE",
    "MAX_CONCURRENT_TASKS", 
    "PROCESSING_TIMEOUT",
    "MAX_RETRIES",
    "RETRY_DELAY",
    
    # Quality Control
    "QUALITY_THRESHOLD",
    "MIN_ARTICLE_LENGTH",
    "MAX_ARTICLE_LENGTH",
    
    # Cost Management
    "DAILY_BUDGET_LIMIT",
    "MONTHLY_BUDGET_LIMIT",
    "COST_ALERT_THRESHOLD",
    "COST_CIRCUIT_BREAKER",
    
    # Feature Flags
    "ENABLE_ARXIV_INGESTION",
    "ENABLE_AI_GENERATION",
    "ENABLE_QUALITY_CONTROL",
    "ENABLE_MONITORING",
    "ENABLE_COST_TRACKING",
    
    # Monitoring
    "SLACK_WEBHOOK_URL",
    "SMTP_HOST",
    "ALERT_EMAILS",
    
    # Advanced Features
    "ENABLE_VIDEO_GENERATION",
    "ENABLE_IMAGE_GENERATION",
]


@task(task_id="validate_airflow_variables")
def validate_airflow_variables() -> Dict[str, Any]:
    """
    Validate that all required Airflow Variables are set and accessible.
    
    Returns:
        Dict containing variable validation results
    """
    log.info("🔍 Starting Airflow Variables validation...")
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "required_variables": {},
        "optional_variables": {},
        "missing_required": [],
        "missing_optional": [],
        "validation_passed": True,
        "error_count": 0,
        "warning_count": 0,
        "summary": {}, 
    }
    
    # Check required variables
    for var_name in REQUIRED_VARIABLES:
        try:
            value = Variable.get(var_name, default=None)
            if value is None:
                # Try getting from environment as fallback
                value = os.getenv(var_name)
                
            if value is None:
                results["missing_required"].append(var_name)
                results["validation_passed"] = False
                results["error_count"] += 1
                log.error(f"❌ Required variable missing: {var_name}")
            else:
                # Store masked version for sensitive variables
                if any(secret in var_name.upper() for secret in ["API_KEY", "PASSWORD", "SECRET", "TOKEN"]):
                    masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                    results["required_variables"][var_name] = {
                        "present": True,
                        "value": masked_value,
                        "source": "airflow_variable" if Variable.get(var_name, default=None) else "environment"
                    }
                else:
                    results["required_variables"][var_name] = {
                        "present": True,
                        "value": value,
                        "source": "airflow_variable" if Variable.get(var_name, default=None) else "environment"
                    }
                log.info(f"✅ Required variable found: {var_name}")
        except Exception as e:
            results["missing_required"].append(var_name)
            results["validation_passed"] = False
            results["error_count"] += 1
            log.error(f"❌ Error accessing variable {var_name}: {str(e)}")
    
    # Check optional variables
    for var_name in OPTIONAL_VARIABLES:
        try:
            value = Variable.get(var_name, default=None)
            if value is None:
                value = os.getenv(var_name)
                
            if value is None:
                results["missing_optional"].append(var_name)
                results["warning_count"] += 1
                log.warning(f"⚠️ Optional variable missing: {var_name}")
            else:
                if any(secret in var_name.upper() for secret in ["API_KEY", "PASSWORD", "SECRET", "TOKEN"]):
                    masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                    results["optional_variables"][var_name] = {
                        "present": True,
                        "value": masked_value,
                        "source": "airflow_variable" if Variable.get(var_name, default=None) else "environment"
                    }
                else:
                    results["optional_variables"][var_name] = {
                        "present": True,
                        "value": value,
                        "source": "airflow_variable" if Variable.get(var_name, default=None) else "environment"
                    }
                log.info(f"✅ Optional variable found: {var_name}")
        except Exception as e:
            results["missing_optional"].append(var_name)
            results["warning_count"] += 1
            log.warning(f"⚠️ Optional variable error {var_name}: {str(e)}")
    
    # Summary
    total_required = len(REQUIRED_VARIABLES)
    found_required = total_required - len(results["missing_required"])
    total_optional = len(OPTIONAL_VARIABLES) 
    found_optional = total_optional - len(results["missing_optional"])
    
    results["summary"] = {
        "required_variables": f"{found_required}/{total_required}",
        "optional_variables": f"{found_optional}/{total_optional}",
        "required_percentage": round((found_required / total_required) * 100, 2),
        "optional_percentage": round((found_optional / total_optional) * 100, 2) if total_optional > 0 else 100,
    }
    
    if results["validation_passed"]:
        log.info(f"🎉 All required variables validated successfully!")
        log.info(f"📊 Summary: {results['summary']['required_variables']} required, {results['summary']['optional_variables']} optional")
    else:
        log.error(f"💥 Variable validation failed: {len(results['missing_required'])} required variables missing")
    
    return results


@task(task_id="test_database_connectivity")
def test_database_connectivity() -> Dict[str, Any]:
    """
    Test database connectivity and basic queries.
    
    Returns:
        Dict containing database test results
    """
    log.info("🔍 Testing database connectivity...")
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "connection_test": False,
        "query_test": False,
        "migration_status": "unknown",
        "table_count": 0,
        "error_message": "",  # Empty string instead of None for Airflow 3.x XCom compatibility
        "connection_info": {},
        "database_version": "",
        "tables": [],
    }
    
    try:
        # Get database URL from Variable or environment
        db_url = Variable.get("DATABASE_URL", default=None)
        if not db_url:
            db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            raise ValueError("DATABASE_URL not found in Variables or environment")
        
        # Parse connection info (without password)
        import re
        url_pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)"
        match = re.match(url_pattern, db_url)
        if match:
            user, password, host, port, database = match.groups()
            results["connection_info"] = {
                "host": host,
                "port": int(port),
                "database": database,
                "user": user,
                "password_length": len(password),
            }
        
        # Connection test
        with psycopg2.connect(db_url) as conn:
            results["connection_test"] = True
            log.info("✅ Database connection successful")
            
            # Query test
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                results["database_version"] = version
                log.info(f"✅ Database version: {version}")
                
                # Check if we have any tables
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                results["table_count"] = table_count
                log.info(f"📊 Found {table_count} tables in public schema")
                
                # Check for expected schema tables (from SQL migrations)
                # SQL migrations are in /opt/airflow/shared_migrations/
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cursor.fetchall()]
                results["tables"] = tables
                
                # Check for expected core tables from our ER diagram
                expected_tables = [
                    'users', 'roles', 'permissions', 'papers', 
                    'articles', 'author_profiles', 'fields'
                ]
                found_tables = [t for t in expected_tables if t in tables]
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if len(found_tables) == len(expected_tables):
                    results["migration_status"] = "complete"
                    log.info(f"✅ All expected tables found: {len(found_tables)}/{len(expected_tables)}")
                elif len(found_tables) > 0:
                    results["migration_status"] = "partial"
                    results["found_tables"] = found_tables
                    results["missing_tables"] = missing_tables
                    log.warning(f"⚠️ Partial schema: {len(found_tables)}/{len(expected_tables)} tables found")
                else:
                    results["migration_status"] = "not_applied"
                    log.warning("⚠️ No expected tables found - migrations may not be applied")
                
                results["query_test"] = True
                
    except Exception as e:
        results["error_message"] = str(e)
        log.error(f"❌ Database connectivity failed: {str(e)}")
    
    return results


@task(task_id="test_external_apis") 
def test_external_apis() -> Dict[str, Any]:
    """
    Test connectivity to external APIs.
    
    Returns:
        Dict containing API test results
    """
    log.info("🔍 Testing external API connectivity...")
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "apis_tested": [],
        "apis_passed": [],
        "apis_failed": [],
        "overall_status": True,
    }
    
    # Test arXiv API
    try:
        # Simple arXiv API test
        import requests
        response = requests.get(
            "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=1",
            timeout=10
        )
        
        if response.status_code == 200:
            results["apis_tested"].append("arxiv")
            results["apis_passed"].append("arxiv")
            log.info("✅ arXiv API connectivity successful")
        else:
            results["apis_tested"].append("arxiv")
            results["apis_failed"].append(f"arxiv (status: {response.status_code})")
            results["overall_status"] = False
            log.error(f"❌ arXiv API failed with status: {response.status_code}")
            
    except Exception as e:
        results["apis_tested"].append("arxiv")
        results["apis_failed"].append(f"arxiv (error: {str(e)[:100]})")
        results["overall_status"] = False
        log.error(f"❌ arXiv API connectivity failed: {str(e)}")
    
    # Test OpenAI API (if key is available)
    try:
        openai_key = Variable.get("OPENAI_API_KEY", default=None)
        if not openai_key:
            openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key and not openai_key.startswith("sk-your_"):
            # Test OpenAI API with a minimal request
            import openai
            openai.api_key = openai_key
            
            # Simple model list test
            client = openai.OpenAI(api_key=openai_key)
            models = client.models.list()
            
            results["apis_tested"].append("openai")
            results["apis_passed"].append("openai")
            log.info("✅ OpenAI API connectivity successful")
        else:
            log.info("ℹ️ OpenAI API key not configured, skipping test")
            
    except Exception as e:
        results["apis_tested"].append("openai")
        results["apis_failed"].append(f"openai (error: {str(e)[:100]})")
        results["overall_status"] = False
        log.error(f"❌ OpenAI API connectivity failed: {str(e)}")
    
    # Summary
    total_tested = len(results["apis_tested"])
    total_passed = len(results["apis_passed"])
    
    results["summary"] = {
        "apis_tested": total_tested,
        "apis_passed": total_passed,
        "apis_failed": len(results["apis_failed"]),
        "success_rate": round((total_passed / total_tested) * 100, 2) if total_tested > 0 else 0,
    }
    
    log.info(f"📊 API Tests Summary: {total_passed}/{total_tested} passed ({results['summary']['success_rate']}%)")
    
    return results


@task(task_id="check_system_resources")
def check_system_resources() -> Dict[str, Any]:
    """
    Check system resources and performance metrics.
    
    Returns:
        Dict containing system resource information
    """
    log.info("🔍 Checking system resources...")
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "disk_space": {},
        "environment_info": {},
        "airflow_info": {},
        "warnings": [],
        "errors": [],
    }
    
    try:
        import shutil
        import psutil
        
        # Check disk space for critical paths
        paths_to_check = [
            "/opt/airflow/data",
            "/opt/airflow/logs", 
            "/tmp",
        ]
        
        for path in paths_to_check:
            if os.path.exists(path):
                usage = shutil.disk_usage(path)
                total_gb = usage.total / (1024**3)
                free_gb = usage.free / (1024**3)
                used_gb = usage.used / (1024**3)
                used_percent = (used_gb / total_gb) * 100
                
                results["disk_space"][path] = {
                    "total_gb": round(total_gb, 2),
                    "free_gb": round(free_gb, 2), 
                    "used_gb": round(used_gb, 2),
                    "used_percent": round(used_percent, 2),
                }
                
                # Warn if disk usage is high
                if used_percent > 85:
                    warning = f"High disk usage: {path} is {used_percent:.1f}% full"
                    results["warnings"].append(warning)
                    log.warning(f"⚠️ {warning}")
                elif used_percent > 95:
                    error = f"Critical disk usage: {path} is {used_percent:.1f}% full"
                    results["errors"].append(error)
                    log.error(f"❌ {error}")
                else:
                    log.info(f"✅ Disk usage OK: {path} is {used_percent:.1f}% full")
        
        # System information
        results["environment_info"] = {
            "python_version": os.sys.version,
            "airflow_home": os.getenv("AIRFLOW_HOME", "not_set"),
            "environment": Variable.get("ENVIRONMENT", default=os.getenv("ENVIRONMENT", "unknown")),
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown",
        }
        
        # Memory information (if available)
        try:
            memory = psutil.virtual_memory()
            results["memory"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
            }
            
            if memory.percent > 85:
                warning = f"High memory usage: {memory.percent:.1f}%"
                results["warnings"].append(warning)
                log.warning(f"⚠️ {warning}")
            else:
                log.info(f"✅ Memory usage OK: {memory.percent:.1f}%")
                
        except Exception as e:
            log.info(f"ℹ️ Could not get memory info: {str(e)}")
        
    except Exception as e:
        error = f"Error checking system resources: {str(e)}"
        results["errors"].append(error)
        log.error(f"❌ {error}")
    
    return results


@task(task_id="generate_health_summary")
def generate_health_summary(
    variables_result: Dict[str, Any],
    database_result: Dict[str, Any],
    api_result: Dict[str, Any],
    resources_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate overall health summary from all checks.
    
    Args:
        variables_result: Results from variable validation
        database_result: Results from database test
        api_result: Results from API tests
        resources_result: Results from resource checks
        
    Returns:
        Dict containing overall health summary
    """
    log.info("📊 Generating health summary...")
    
    # Calculate overall health score
    health_components = {
        "variables": variables_result.get("validation_passed", False),
        "database": database_result.get("connection_test", False) and database_result.get("query_test", False),
        "apis": api_result.get("overall_status", False),
        "resources": len(resources_result.get("errors", [])) == 0,
    }
    
    passed_components = sum(1 for status in health_components.values() if status)
    total_components = len(health_components)
    health_score = (passed_components / total_components) * 100
    
    # Determine overall status
    if health_score >= 100:
        overall_status = "healthy"
        status_emoji = "🟢"
    elif health_score >= 75:
        overall_status = "warning"  
        status_emoji = "🟡"
    else:
        overall_status = "critical"
        status_emoji = "🔴"
    
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "health_score": round(health_score, 2),
        "component_status": health_components,
        "components_passed": passed_components,
        "total_components": total_components,
        
        # Detailed results
        "variables_summary": {
            "required_found": len(variables_result.get("required_variables", {})),
            "required_missing": len(variables_result.get("missing_required", [])),
            "optional_found": len(variables_result.get("optional_variables", {})),
            "optional_missing": len(variables_result.get("missing_optional", [])),
        },
        
        "database_summary": {
            "connection_ok": database_result.get("connection_test", False),
            "queries_ok": database_result.get("query_test", False),
            "table_count": database_result.get("table_count", 0),
            "migration_status": database_result.get("migration_status", "unknown"),
        },
        
        "api_summary": {
            "apis_tested": len(api_result.get("apis_tested", [])),
            "apis_passed": len(api_result.get("apis_passed", [])),
            "success_rate": api_result.get("summary", {}).get("success_rate", 0),
        },
        
        "resource_summary": {
            "warnings": len(resources_result.get("warnings", [])),
            "errors": len(resources_result.get("errors", [])),
            "disk_paths_checked": len(resources_result.get("disk_space", {})),
        },
        
        # Configuration readiness for Sprint 2
        "sprint2_readiness": {
            "arxiv_ingestion_ready": all([
                variables_result.get("required_variables", {}).get("ARXIV_MAX_RESULTS", {}).get("present", False),
                variables_result.get("required_variables", {}).get("ARXIV_CATEGORIES", {}).get("present", False),
                api_result.get("overall_status", False),
                database_result.get("connection_test", False),
            ]),
            "scheduling_ready": health_components.get("variables", False) and health_components.get("database", False),
            "monitoring_ready": len(resources_result.get("errors", [])) == 0,
        },
    }
    
    # Log summary
    log.info(f"{status_emoji} Overall Health: {overall_status.upper()} ({health_score:.1f}%)")
    log.info(f"📋 Components: {passed_components}/{total_components} passed")
    log.info(f"📊 Variables: {summary['variables_summary']['required_found']} required, {summary['variables_summary']['required_missing']} missing")
    log.info(f"🗄️ Database: {'✅' if summary['database_summary']['connection_ok'] else '❌'} connection, {summary['database_summary']['table_count']} tables")
    log.info(f"🌐 APIs: {summary['api_summary']['apis_passed']}/{summary['api_summary']['apis_tested']} passed")
    log.info(f"💾 Resources: {summary['resource_summary']['warnings']} warnings, {summary['resource_summary']['errors']} errors")
    
    # Sprint 2 readiness
    sprint2_ready = all(summary["sprint2_readiness"].values())
    log.info(f"🚀 Sprint 2 Readiness: {'✅ READY' if sprint2_ready else '⚠️ NEEDS ATTENTION'}")
    
    return summary


# Create the DAG
with DAG(
    dag_id=DAG_ID,
    default_args=DEFAULT_ARGS,
    description="Production health check for Zara ETL system components and configuration",
    schedule=timedelta(hours=6),  # Run every 6 hours
    catchup=False,
    max_active_runs=1,
    tags=["health", "monitoring", "production", "sprint2"],
    doc_md=__doc__,
) as dag:
    
    # Define task flow
    variables_check = validate_airflow_variables()
    database_check = test_database_connectivity()
    api_check = test_external_apis()
    resources_check = check_system_resources()
    
    health_summary = generate_health_summary(
        variables_check,
        database_check, 
        api_check,
        resources_check
    )
    
    # Set task dependencies
    [variables_check, database_check, api_check, resources_check] >> health_summary
