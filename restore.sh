#!/bin/bash

# This script drops specified tables and restores them from .sql backup files.
# --- Configuration ---
# Load environment variables from .env file
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        if [[ ! -z "$key" && ! "$key" =~ ^# ]]; then
            export "$key=$value"
        fi
    done < .env
else
    echo "Error: .env file not found in $(pwd)! Cannot proceed."
    exit 1
fi

DB_USER="${POSTGRES_USER}" # Using POSTGRES_USER from .env for database operations
DB_NAME="${POSTGRES_DB}"   # Using POSTGRES_DB from .env

# List of tables to drop and restore. Ensure backup files match these names.
TABLES_TO_PROCESS="transactions income expense cashflow" # Order might matter for foreign keys if not using CASCADE

HOST_BACKUP_DIR="$(dirname "$(realpath "$0")")/backups" # Path to your backups folder

# --- Error Handling ---
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting Full Database Restore Process ---"

# --- Step 1: Check if the database container is running ---
if ! docker compose ps -q db | grep -q .; then
    echo "Error: Docker Compose 'db' service (budget_db) is not running."
    echo "Please start your project manually first: docker-compose up -d"
    exit 1
fi

# --- Step 2: Drop Existing Tables ---
echo ""
echo "WARNING: All data and structures for income, expense, and transactions tables WILL BE DELETED."
read -p "Are you sure you want to proceed with dropping and restoring (Y/n)? " -n 1 -r CONFIRM_DROP
echo "" # Newline for cleaner output

if [[ ! $CONFIRM_DROP =~ ^[Yy]$ ]]; then
    echo "Drop and restore cancelled. Exiting."
    exit 0
fi

echo "Dropping existing tables: ${TABLES_TO_PROCESS}..."
for TABLE in ${TABLES_TO_PROCESS}; do
    echo "  - Dropping table '${TABLE}'..."
    # DROP TABLE IF EXISTS removes the table and its associated sequence (like income_id_seq)
    # CASCADE ensures any dependent objects (like foreign keys) are also handled.
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" -c "DROP TABLE IF EXISTS \"${TABLE}\" CASCADE;"
    if [ $? -eq 0 ]; then
        echo "    Success: Table '${TABLE}' dropped."
    else
        echo "    Error: Failed to drop table '${TABLE}'!"
        exit 1 # Exit if any drop fails
    fi
done

echo "Tables dropped successfully."

# --- Step 3: Restore Data from Backup Files ---
echo ""
echo "Restoring data from backup files in '${HOST_BACKUP_DIR}'..."
for TABLE in ${TABLES_TO_PROCESS}; do
    BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql" # Assuming your files are named table_backup.sql
    
    if [ ! -f "${BACKUP_FILE}" ]; then
        echo "Error: Backup file not found for '${TABLE}': ${BACKUP_FILE}"
        echo "Please ensure your backup files exist in the './backups' folder and are named correctly."
        exit 1
    fi

    echo "  - Restoring table '${TABLE}' from '${BACKUP_FILE}'..."
    # This command executes the SQL commands within your backup file (CREATE TABLE, COPY data, etc.)
    docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" < "${BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "    Success: Table '${TABLE}' restored."
    else
        echo "    Error: Failed to restore table '${TABLE}'!"
        exit 1 # Exit if any restore fails
    fi
done

echo ""
echo "--- Full Database Restore Process Complete ---"
echo "Your database tables are now restored from the backup files."

echo "Script finished."