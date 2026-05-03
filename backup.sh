#!/bin/bash
# =============================================================================
# backup.sh — Automated PostgreSQL table backup (data-only, timestamped)
# Usage: ./backup.sh [--tables "table1 table2"] [--keep-days 7]
# =============================================================================

set -euo pipefail  # Strict mode: exit on error, unbound vars, pipe failures

# --- Resolve script directory (works regardless of where you call it from) ---
SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

# --- Load .env safely (handles quoted values, spaces, comments) ---
load_env() {
    local env_file="$SCRIPT_DIR/.env"
    if [[ ! -f "$env_file" ]]; then
        echo "Error: .env not found at $env_file"
        exit 1
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and blank lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        # Strip inline comments, then export
        line="${line%%#*}"
        if [[ "$line" == *"="* ]]; then
            export "${line?}"
        fi
    done < "$env_file"
}

load_env

# --- Defaults (override via CLI flags) ---
TABLES="${TABLES_OVERRIDE:-"income expense transactions"}"
KEEP_DAYS=7
HOST_BACKUP_DIR="$SCRIPT_DIR/backups"

# --- Parse optional CLI arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tables)   TABLES="$2";    shift 2 ;;
        --keep-days) KEEP_DAYS="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# --- Config from .env ---
DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
BACKUP_SET_DIR="$HOST_BACKUP_DIR/$TIMESTAMP"  # One folder per backup run

mkdir -p "$BACKUP_SET_DIR"

echo "============================================="
echo " Backup started: $(date)"
echo " Database : $DB_NAME"
echo " Tables   : $TABLES"
echo " Output   : $BACKUP_SET_DIR"
echo "============================================="

# --- Check container health ---
if ! docker compose -f "$SCRIPT_DIR/docker-compose.yml" ps -q db 2>/dev/null | grep -q .; then
    echo "Error: 'db' container is not running. Start it with: docker compose up -d db"
    exit 1
fi

# --- Backup each table (data-only, plain SQL) ---
declare -a TABLE_ARRAY=($TABLES)
FAILED_TABLES=()

for TABLE in "${TABLE_ARRAY[@]}"; do
    BACKUP_FILE="$BACKUP_SET_DIR/${TABLE}.sql"
    echo ""
    echo "  Backing up: $TABLE -> ${TABLE}.sql"

    # --data-only: schema lives in Docker volume, only dump rows
    # --column-inserts: use INSERT statements instead of COPY (safer for partial restores)
    if docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T db \
        pg_dump \
            --username="$DB_USER" \
            --dbname="$DB_NAME" \
            --table="$TABLE" \
            --data-only \
            --column-inserts \
            --no-owner \
            --no-acl \
        > "$BACKUP_FILE"; then
        # Compress immediately after dump
        gzip "$BACKUP_FILE"
        echo "  ✓ Saved: ${TABLE}.sql.gz ($(du -h "${BACKUP_FILE}.gz" | cut -f1))"
    else
        echo "  ✗ Failed: $TABLE"
        FAILED_TABLES+=("$TABLE")
    fi
done

# --- Write a manifest so restore.sh knows what's in this backup set ---
MANIFEST="$BACKUP_SET_DIR/manifest.txt"
{
    echo "timestamp=$TIMESTAMP"
    echo "database=$DB_NAME"
    echo "tables=${TABLE_ARRAY[*]}"
    echo "failed=${FAILED_TABLES[*]:-none}"
} > "$MANIFEST"

# --- Rotate: delete backup sets older than KEEP_DAYS ---
echo ""
echo "Rotating backups older than $KEEP_DAYS days..."
find "$HOST_BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -mtime "+$KEEP_DAYS" \
    | while read -r old_dir; do
        echo "  Removing: $old_dir"
        rm -rf "$old_dir"
    done

# --- Also maintain a 'latest' symlink for easy restore ---
LATEST_LINK="$HOST_BACKUP_DIR/latest"
ln -sfn "$BACKUP_SET_DIR" "$LATEST_LINK"

echo ""
echo "============================================="
if [[ ${#FAILED_TABLES[@]} -gt 0 ]]; then
    echo " Backup PARTIAL — failed tables: ${FAILED_TABLES[*]}"
    echo " Check logs above for details."
    exit 1
else
    echo " Backup COMPLETE: $TIMESTAMP"
    echo " Symlink: $LATEST_LINK -> $BACKUP_SET_DIR"
fi
echo "============================================="