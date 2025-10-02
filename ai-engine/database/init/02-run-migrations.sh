#!/bin/bash
set -e

echo "🔄 Running SQL migrations from shared folder..."

# Check if migrations directory exists
MIGRATIONS_DIR="/docker-entrypoint-initdb.d/../../database"
SHARED_MIGRATIONS="/shared_migrations"

# Use shared migrations if mounted, otherwise check local
if [ -d "$SHARED_MIGRATIONS" ] && [ "$(ls -A $SHARED_MIGRATIONS/*.up.sql 2>/dev/null)" ]; then
    MIGRATIONS_DIR="$SHARED_MIGRATIONS"
    echo "📁 Using shared migrations from: $MIGRATIONS_DIR"
elif [ -d "/database" ] && [ "$(ls -A /database/*.up.sql 2>/dev/null)" ]; then
    MIGRATIONS_DIR="/database"
    echo "📁 Using local migrations from: $MIGRATIONS_DIR"
else
    echo "ℹ️  No migrations found to apply"
    exit 0
fi

# Run migrations in order against zara_etl database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "zara_etl" <<-EOSQL
    -- Create migrations tracking table if it doesn't exist
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR(255) PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
EOSQL

# Find and run all .up.sql files in order
for migration_file in $(ls $MIGRATIONS_DIR/*.up.sql 2>/dev/null | sort); do
    migration_name=$(basename "$migration_file" .up.sql)
    
    # Check if migration was already applied
    already_applied=$(psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "zara_etl" -tAc \
        "SELECT COUNT(*) FROM schema_migrations WHERE version='$migration_name'")
    
    if [ "$already_applied" -eq "0" ]; then
        echo "  ▶️  Applying migration: $migration_name"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "zara_etl" -f "$migration_file"
        
        # Record migration as applied
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "zara_etl" <<-EOSQL
            INSERT INTO schema_migrations (version) VALUES ('$migration_name');
EOSQL
        echo "  ✅ Applied: $migration_name"
    else
        echo "  ⏭️  Skipping (already applied): $migration_name"
    fi
done

echo "✅ All migrations completed successfully"
