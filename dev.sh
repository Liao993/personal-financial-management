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

run_db_sql() {
    local sql_file="$1"
    $DC exec -T db sh -lc "psql -v ON_ERROR_STOP=1 -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -f $sql_file"
}

reload_sample_data() {
    echo "Applying development schema extensions..."
    run_db_sql /docker-entrypoint-initdb.d/03_expense_transaction_sync.sql
    run_db_sql /docker-entrypoint-initdb.d/04_portfolio_schema.sql

    echo "Reloading development sample data..."
    run_db_sql /docker-entrypoint-initdb.d/05_seed_dev.sql

    echo "Refreshing dbt models..."
    $DC run --rm dbt dbt run
}

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
        echo "Restarting DEV environment and reloading sample data..."
        $DC down
        $DC up -d db
        wait_for_db
        reload_sample_data
        $DC up -d app
        echo ""
        echo "  budget_db_dev        → localhost:5433"
        echo "  budget_streamlit_dev → http://localhost:8502"
        ;;
    reload-sample)
        $DC up -d db
        wait_for_db
        reload_sample_data
        ;;
    logs)
        $DC logs -f "${2:-}" ;;
    psql)
        $DC exec db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' ;;
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
        echo "Usage: ./dev.sh [up|down|restart|reload-sample|logs|psql|dbt|reset]"
        exit 1 ;;
esac
