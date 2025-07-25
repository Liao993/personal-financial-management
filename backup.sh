#!/bin/bash

# This script performs a manual backup of specified PostgreSQL tables
# and then offers an option to restore from the created backup files.

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
TABLES="income expense transactions" # Space-separated list of tables to backup/restore

HOST_BACKUP_DIR="$(dirname "$(realpath "$0")")/backups" # Directory for backups on host
mkdir -p "${HOST_BACKUP_DIR}" # Ensure the directory exists

# BACKUP_DATE is no longer used for filenames as files will be overwritten
# BACKUP_DATE=$(date +%Y%m%d_%H%M%S) # Timestamp for unique backup files

# --- Error Handling ---
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting Database Backup ---"

# Check if the database container is running
if ! docker compose ps -q db | grep -q .; then
    echo "Error: Docker Compose 'db' service (budget_db) is not running."
    echo "Please start your project manually first: docker-compose up -d"
    exit 1
fi

# Use an indexed array for backup file paths (compatible with older Bash)
BACKUP_FILES=()
TABLE_NAMES=(${TABLES}) # Convert space-separated string into an indexed array

# --- Step 1: Run pg_dump for each table ---
echo "Backing up tables from '${DB_NAME}' database using user '${DB_USER}'..."
for i in "${!TABLE_NAMES[@]}"; do # Iterate using indices
    TABLE="${TABLE_NAMES[$i]}"
    # Modified: Remove BACKUP_DATE from filename to overwrite previous backups
    BACKUP_FILE="${HOST_BACKUP_DIR}/${TABLE}_backup.sql"
    echo "  - Dumping table '${TABLE}' to '${BACKUP_FILE}' (overwriting previous)..."
    docker compose exec -T db pg_dump -U "${DB_USER}" -d "${DB_NAME}" -t "${TABLE}" -Fp > "${BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "    Success: '${TABLE}' backed up."
        BACKUP_FILES[$i]="${BACKUP_FILE}" # Store path in indexed array
    else
        echo "    Error: Failed to backup '${TABLE}'!"
        exit 1 # Exit if any backup fails
    fi
done

echo "--- Database Backup Complete ---"
echo "Backup files saved in: ${HOST_BACKUP_DIR}"

# --- Step 2: Ask for Restore Confirmation ---
echo ""
read -p "Do you want to restore data from the latest backup (Y/n)? " -n 1 -r REPLY
echo "" # Newline for cleaner output

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "--- Initiating Data Restore ---"
    echo "WARNING: This will TRUNCATE (clear) existing data in tables before restoring."
    read -p "Are you sure you want to TRUNCATE and RESTORE (Y/n)? " -n 1 -r CONFIRM_RESTORE
    echo "" # Newline for cleaner output

    if [[ $CONFIRM_RESTORE =~ ^[Yy]$ ]]; then
        for i in "${!TABLE_NAMES[@]}"; do # Iterate using indices again
            TABLE="${TABLE_NAMES[$i]}"
            RESTORE_FILE="${BACKUP_FILES[$i]}" # Retrieve path from indexed array
            echo "  - Restoring table '${TABLE}' from '${RESTORE_FILE}'..."
            
            # Truncate table first to avoid conflicts/duplicates
            echo "    Truncating table '${TABLE}'..."
            docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" -c "TRUNCATE TABLE \"${TABLE}\" RESTART IDENTITY CASCADE;"
            
            # Restore data from the backup file
            echo "    Loading data into '${TABLE}'..."
            docker compose exec -T db psql -U "${DB_USER}" -d "${DB_NAME}" < "${RESTORE_FILE}"
            
            if [ $? -eq 0 ]; then
                echo "    Success: '${TABLE}' restored."
            else
                echo "    Error: Failed to restore '${TABLE}'!"
                exit 1 # Exit if any restore fails
            fi
        done
        echo "--- Data Restore Complete ---"
    else
        echo "Restore cancelled. Exiting."
    fi
else
    echo "Restore skipped. Exiting."
fi

echo "Script finished."