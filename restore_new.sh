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

# --- Step 3: Restore Data (Improved Filter) ---
echo "Restoring data..."
for TABLE in ${TABLES_TO_PROCESS}; do
    BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql"
    
    if [ ! -f "${BACKUP_FILE}" ]; then continue; fi

    echo "Processing table: ${TABLE}..."

    # 1. Clear existing data
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" -c "TRUNCATE TABLE \"${TABLE}\" CASCADE;"

    # 2. Import ONLY data lines (COPY and INSERT) and SEQUENCE updates
    # This filter removes lines starting with CREATE, ALTER, or loose constraints
    grep -E "^COPY|^INSERT|^SELECT|^SET|\\\." "${BACKUP_FILE}" | \
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}"

    echo "  -> Done."
done