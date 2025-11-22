#!/bin/bash

# This script performs a manual backup of specified PostgreSQL tables.

# --- Configuration ---
# Load environment variables from .env file
if [ -f .env ]; then
    # Read .env line by line, ignoring comments and empty lines
    while IFS='=' read -r key value; do
        # Remove leading/trailing whitespace from key and value
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        # Check if key is not empty and not a comment
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

# List of tables to backup. Ensure backup files will match these names.
TABLES="income expense transactions cashflow"

HOST_BACKUP_DIR="$(dirname "$(realpath "$0")")/backups" # Directory for backups on host
mkdir -p "${HOST_BACKUP_DIR}" # Ensure the directory exists

# --- Error Handling ---
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting Database Backup ---"

# --- Step 1: Check if the database container is running ---
if ! docker compose ps -q db | grep -q .; then
    echo "Error: Docker Compose 'db' service (budget_db) is not running."
    echo "Please start your project manually first: docker-compose up -d"
    exit 1
fi

# Use an indexed array for table names to iterate consistently
declare -a TABLE_NAMES=(${TABLES})

# --- Step 2: Run pg_dump for each table ---
echo ""
echo "--- Backing up tables from '${DB_NAME}' database ---"
echo "Backup files will overwrite previous versions in '${HOST_BACKUP_DIR}'."

for i in "${!TABLE_NAMES[@]}"; do
    TABLE="${TABLE_NAMES[$i]}"
    # Final file on host (overwrites previous backup)
    HOST_BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql" 

    echo "  - Dumping table '${TABLE}' to '${HOST_BACKUP_FILE}'..."
    docker compose exec -T db pg_dump -U "${DB_USER}" -d "${DB_NAME}" -t "${TABLE}" -Fp > "${HOST_BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "    Success: '${TABLE}' backed up."
    else
        echo "    Error: Failed to backup '${TABLE}'!"
        echo "Exiting script."
        exit 1 # Exit if any backup fails
    fi
done

echo "--- Database Backup Complete ---"
echo "Backup files saved in: ${HOST_BACKUP_DIR}"
echo "Script finished."