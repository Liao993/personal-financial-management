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

wait_for_db() {
    echo "Waiting for database..."
    for _ in {1..30}; do
        if $DC exec -T db sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done

    echo "Database did not become ready in time."
    exit 1
}

case "$CMD" in
    up)
        echo "Starting PROD environment..."
        $DC up -d db
        wait_for_db
        "$SCRIPT_DIR/prod.sh" schema
        $DC up -d app dbt
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
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/05_expense_ingestion_dedupe.sql
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/06_income_deposit_account.sql
        $DC exec -T db psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" -f /docker-entrypoint-initdb.d/07_transaction_category.sql ;;
    dbt)
        $DC run --rm dbt dbt run ;;
    backup)
        /Users/henry/Desktop/personal_finance_management_backup/backup.sh ;;
    *)
        echo "Usage: ./prod.sh [up|down|restart|build|logs|psql|schema|dbt|backup]"
        exit 1 ;;
esac
