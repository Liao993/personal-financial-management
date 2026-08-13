#!/bin/bash
# prod.sh — Manage the PRODUCTION environment

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

DC="docker compose \
    -p budget_prod \
    -f $SCRIPT_DIR/docker-compose.yml \
    -f $SCRIPT_DIR/docker-compose.prod.yml \
    --env-file $SCRIPT_DIR/.env.prod"

CMD="${1:-up}"

case "$CMD" in
    up)
        echo "Starting PROD environment..."
        $DC up -d
        echo ""
        echo "  budget_db        → internal only"
        echo "  budget_streamlit → http://localhost:8501"
        ;;
    down)
        $DC down ;;
    restart)
        $DC down && $DC up -d ;;
    build)
        $DC build app dbt ;;
    logs)
        $DC logs -f "${2:-}" ;;
    psql)
        $DC exec db psql -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" ;;
    schema)
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/03_expense_transaction_sync.sql
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/04_portfolio_schema.sql
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/05_expense_ingestion_dedupe.sql ;;
    dbt)
        $DC run --rm dbt dbt run ;;
    backup)
        /Users/henry/Desktop/personal_finance_management_backup/backup.sh ;;
    *)
        echo "Usage: ./prod.sh [up|down|restart|build|logs|psql|schema|dbt|backup]"
        exit 1 ;;
esac
