#!/bin/bash
set -e

# Create databases if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE zara_airflow'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'zara_airflow')\gexec
    
    SELECT 'CREATE DATABASE zara_etl'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'zara_etl')\gexec
EOSQL

echo "✅ Databases initialized successfully (zara_airflow, zara_etl)"
