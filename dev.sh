#!/bin/bash
# dev.sh — Manage the DEVELOPMENT environment

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

DC="docker compose \
    -p budget_dev \
    -f $SCRIPT_DIR/docker-compose.yml \
    -f $SCRIPT_DIR/docker-compose.dev.yml \
    --env-file $SCRIPT_DIR/.env.dev"

CMD="${1:-up}"

case "$CMD" in
    up)
        echo "Starting DEV environment..."
        $DC up -d
        echo ""
        echo "  budget_db_dev        → localhost:5433"
        echo "  budget_streamlit_dev → http://localhost:8502"
        ;;
    down)
        $DC down ;;
    restart)
        $DC down && $DC up -d ;;
    logs)
        $DC logs -f "${2:-}" ;;
    psql)
        $DC exec db psql -U "${POSTGRES_USER:-budget_user}" -d "${POSTGRES_DB:-budget_dev}" ;;
    dbt)
        $DC run --rm dbt dbt run ;;
    reset)
        echo "WARNING: Deletes postgres_data_dev volume. Prod unaffected."
        read -rp "Proceed? (yes/no): " C
        [[ "$C" != "yes" ]] && { echo "Aborted."; exit 0; }
        $DC down -v
        $DC up -d
        ;;
    *)
        echo "Usage: ./dev.sh [up|down|restart|logs|psql|dbt|reset]"
        exit 1 ;;
esac