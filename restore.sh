#!/bin/bash
# =============================================================================
# restore.sh — Restore PostgreSQL tables from a backup set
# Usage: ./restore.sh [--from TIMESTAMP] [--tables "table1 table2"] [--no-dbt]
#
# Examples:
#   ./restore.sh                          # Restore all tables from latest backup
#   ./restore.sh --from 2026-05-03_220000 # Restore from a specific backup set
#   ./restore.sh --tables "income"        # Restore only one table
#   ./restore.sh --no-dbt                 # Skip dbt refresh after restore
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

# --- Load .env safely ---
load_env() {
    local env_file="$SCRIPT_DIR/.env"
    if [[ ! -f "$env_file" ]]; then
        echo "Error: .env not found at $env_file"
        exit 1
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        line="${line%%#*}"
        if [[ "$line" == *"="* ]]; then
            export "${line?}"
        fi
    done < "$env_file"
}

load_env

# --- Defaults ---
HOST_BACKUP_DIR="$SCRIPT_DIR/backups"
FROM_TIMESTAMP=""
TABLES_OVERRIDE=""
RUN_DBT=true

# --- Parse CLI arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --from)    FROM_TIMESTAMP="$2"; shift 2 ;;
        --tables)  TABLES_OVERRIDE="$2"; shift 2 ;;
        --no-dbt)  RUN_DBT=false; shift 1 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# --- Resolve the backup set to restore from ---
if [[ -n "$FROM_TIMESTAMP" ]]; then
    BACKUP_SET_DIR="$HOST_BACKUP_DIR/$FROM_TIMESTAMP"
else
    BACKUP_SET_DIR="$(realpath "$HOST_BACKUP_DIR/latest")"
fi

if [[ ! -d "$BACKUP_SET_DIR" ]]; then
    echo "Error: Backup set not found: $BACKUP_SET_DIR"
    echo ""
    echo "Available backups:"
    ls -1 "$HOST_BACKUP_DIR" | grep -v latest | sort -r | head -10
    exit 1
fi

# --- Read manifest ---
MANIFEST="$BACKUP_SET_DIR/manifest.txt"
if [[ ! -f "$MANIFEST" ]]; then
    echo "Error: No manifest.txt in $BACKUP_SET_DIR"
    echo "This backup may be from an older format."
    exit 1
fi

# FIX: Read manifest key=value pairs explicitly with safe defaults.
# The previous version used 'source <(cat manifest)' which caused an
# "unbound variable" error when 'set -u' was active and any key was missing.
MANIFEST_TIMESTAMP=""
MANIFEST_TABLES=""
MANIFEST_DATABASE=""

while IFS='=' read -r key value; do
    case "$key" in
        timestamp) MANIFEST_TIMESTAMP="$value" ;;
        tables)    MANIFEST_TABLES="$value" ;;
        database)  MANIFEST_DATABASE="$value" ;;
    esac
done < "$MANIFEST"

# Guard: ensure manifest had a tables entry
if [[ -z "$MANIFEST_TABLES" ]]; then
    echo "Error: manifest.txt is missing a 'tables=' entry."
    echo "Contents of manifest:"
    cat "$MANIFEST"
    exit 1
fi

DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"

# Build the array of tables to restore
if [[ -n "$TABLES_OVERRIDE" ]]; then
    RESTORE_TABLES=($TABLES_OVERRIDE)
else
    RESTORE_TABLES=($MANIFEST_TABLES)   # FIX: was ($tables) — unbound variable
fi

# Total count from manifest (used for dbt decision below)
MANIFEST_TABLE_ARRAY=($MANIFEST_TABLES)
MANIFEST_TABLE_COUNT=${#MANIFEST_TABLE_ARRAY[@]}

echo "============================================="
echo " Restore started : $(date)"
echo " Backup timestamp: ${MANIFEST_TIMESTAMP:-unknown}"
echo " Database        : $DB_NAME"
echo " Tables          : ${RESTORE_TABLES[*]}"
echo " Run dbt         : $RUN_DBT"
echo "============================================="
echo ""
echo "WARNING: This will TRUNCATE and reload the selected tables."
echo "Backup set: $BACKUP_SET_DIR"
echo ""
read -rp "Proceed? (yes/no): " CONFIRM
[[ "$CONFIRM" != "yes" ]] && { echo "Aborted."; exit 0; }
echo ""

# --- Check container health ---
if ! docker compose -f "$SCRIPT_DIR/docker-compose.yml" ps -q db 2>/dev/null | grep -q .; then
    echo "Error: 'db' container is not running."
    echo "Start it with: docker compose up -d db"
    exit 1
fi

FAILED_TABLES=()

for TABLE in "${RESTORE_TABLES[@]}"; do
    BACKUP_FILE_GZ="$BACKUP_SET_DIR/${TABLE}.sql.gz"

    if [[ ! -f "$BACKUP_FILE_GZ" ]]; then
        echo "  Skipping '$TABLE' — file not found: $BACKUP_FILE_GZ"
        continue
    fi

    echo "  Restoring: $TABLE"

    echo "    -> Truncating existing rows..."
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T db \
        psql --username="$DB_USER" --dbname="$DB_NAME" --quiet \
        -c "TRUNCATE TABLE \"$TABLE\" CASCADE;"

    echo "    -> Loading data from backup..."
    if gunzip -c "$BACKUP_FILE_GZ" | \
        docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T db \
            psql --username="$DB_USER" --dbname="$DB_NAME" --quiet; then
        echo "    ✓ $TABLE restored successfully"
    else
        echo "    ✗ $TABLE restore failed"
        FAILED_TABLES+=("$TABLE")
    fi
done

# --- Optional: dbt refresh ---
if [[ "$RUN_DBT" == true ]]; then
    echo ""
    RESTORE_COUNT=${#RESTORE_TABLES[@]}

    if [[ "$TABLES_OVERRIDE" == "" || "$RESTORE_COUNT" -eq "$MANIFEST_TABLE_COUNT" ]]; then
        echo "Running dbt full-refresh (all $MANIFEST_TABLE_COUNT tables restored)..."
        docker compose -f "$SCRIPT_DIR/docker-compose.yml" run --rm dbt \
            dbt run --full-refresh
    else
        echo "Running dbt incremental for: ${RESTORE_TABLES[*]}"
        SELECT_FLAGS=""
        for T in "${RESTORE_TABLES[@]}"; do
            SELECT_FLAGS="$SELECT_FLAGS --select $T"
        done
        docker compose -f "$SCRIPT_DIR/docker-compose.yml" run --rm dbt \
            dbt run $SELECT_FLAGS
    fi
fi

echo ""
echo "============================================="
if [[ ${#FAILED_TABLES[@]} -gt 0 ]]; then
    echo " Restore PARTIAL — failed tables: ${FAILED_TABLES[*]}"
    exit 1
else
    echo " Restore COMPLETE from: ${MANIFEST_TIMESTAMP:-$BACKUP_SET_DIR}"
fi
echo "============================================="