#!/bin/bash

# --- Configuration ---
# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    exit 1
fi

DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
TABLES_TO_PROCESS="transactions income expense cashflow"
HOST_BACKUP_DIR="./backups"

set -e 

echo "--- Starting Smart Database Restore (Schema-Safe) ---"

# 1. Check if Container is Running
if ! docker compose ps -q db | grep -q .; then
    echo "Error: database container is not running."
    exit 1
fi

# 2. Confirmation
echo "WARNING: This will empty the tables and reload data from backups."
echo "Your new columns in 'expense' will be preserved (but will be empty/NULL if not in backup)."
read -p "Proceed? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 3. Process Tables
for TABLE in ${TABLES_TO_PROCESS}; do
    BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql"
    
    if [ ! -f "${BACKUP_FILE}" ]; then
        echo "Skipping ${TABLE}: Backup file not found."
        continue
    fi

    echo "Processing table: ${TABLE}..."

    # STEP A: Empty the table without deleting it (KEEPS NEW COLUMNS)
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" -c "TRUNCATE TABLE \"${TABLE}\" CASCADE;"

    # STEP B: Import data only
    # We use sed to strip out 'CREATE TABLE' and 'ALTER TABLE' commands 
    # This prevents the backup from overwriting your new 01_init_schema.sql structure
    echo "  -> Injecting data from ${BACKUP_FILE}..."
    sed -e '/^CREATE TABLE/d' -e '/^ALTER TABLE/d' -e '/^DROP TABLE/d' "${BACKUP_FILE}" | \
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}"

    echo "  -> Done."
done

echo "--- Restore Complete! ---"