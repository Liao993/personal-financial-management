#!/bin/bash

# --- 1. Load environment variables ---
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    exit 1
fi

DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
TABLES_TO_PROCESS="transactions income expense"
HOST_BACKUP_DIR="./backups"

echo "--- Starting Smart Database Restore (Schema-Safe) ---"

# 2. Check if Container is Running
if ! docker compose ps -q db | grep -q .; then
    echo "Error: database container is not running."
    exit 1
fi

echo "WARNING: This will empty tables and reload data."
read -p "Proceed? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# --- Step 3: Restore Data ---
echo "Restoring data..."
for TABLE in ${TABLES_TO_PROCESS}; do
    BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql"
    
    if [ ! -f "${BACKUP_FILE}" ]; then 
        echo "Skipping $TABLE: File not found."
        continue; 
    fi

    echo "Processing table: ${TABLE}..."

    # 1. Clear existing data
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" -c "TRUNCATE TABLE \"${TABLE}\" CASCADE;"

    # 2. Advanced Filter: 
    # - It skips lines starting with CREATE or ALTER (which cause the 'already exists' error)
    # - It keeps SET, SELECT (for sequences), COPY, and actual data lines.
    # - It passes everything else to psql.
    sed -e '/^CREATE TABLE/d' \
        -e '/^ALTER TABLE/d' \
        -e '/^DROP TABLE/d' \
        -e '/^CREATE INDEX/d' \
        "${BACKUP_FILE}" | \
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" --quiet

    echo "  -> ${TABLE} restore finished."
done

# --- Step 4: Final dbt Refresh ---
echo "Refreshing dbt models to ensure UI sees new data..."
docker compose run --rm dbt dbt run --full-refresh

echo "Done! Please check your Streamlit app for the updated data."