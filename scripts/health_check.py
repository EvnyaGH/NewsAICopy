#!/usr/bin/env python3
"""
Health check script for Airflow services.
Used by Docker to verify service health.
"""

import sys
import os


def check_airflow_health():
    """Basic health check for Airflow."""
    try:
        # Try importing Airflow
        import airflow
        
        # Check if Airflow home is accessible
        airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
        if not os.path.exists(airflow_home):
            print(f"ERROR: Airflow home not found: {airflow_home}")
            return False
        
        print(f"✅ Airflow version: {airflow.__version__}")
        print(f"✅ Airflow home: {airflow_home}")
        return True
        
    except ImportError as e:
        print(f"ERROR: Cannot import Airflow: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return False


if __name__ == "__main__":
    if check_airflow_health():
        print("✅ Health check passed")
        sys.exit(0)
    else:
        print("❌ Health check failed")
        sys.exit(1)
