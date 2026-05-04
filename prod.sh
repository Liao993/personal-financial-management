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
    logs)
        $DC logs -f "${2:-}" ;;
    psql)
        $DC exec db psql -U "${POSTGRES_USER:-hhn}" -d "${POSTGRES_DB:-budget_db}" ;;
    dbt)
        $DC run --rm dbt dbt run ;;
    backup)
        /Users/henry/Desktop/personal_finance_management_backup/backup.sh ;;
    *)
        echo "Usage: ./prod.sh [up|down|restart|logs|psql|dbt|backup]"
        exit 1 ;;
esac