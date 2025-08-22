# Manual Backup
docker compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -t income -Fp > ./backups/income_backup.sql

docker compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -t expense -Fp > ./backups/expense_backup.sql

docker compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -t transactions -Fp > ./backups/transactions_backup.sql

# Truncate Existing Data
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "TRUNCATE TABLE income RESTART IDENTITY CASCADE;"

docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "TRUNCATE TABLE expense RESTART IDENTITY CASCADE;"

docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;"


# Drop the table and its sequence
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS transactions CASCADE;"

docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS income CASCADE;"

docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS expense CASCADE;"

# Restore with Backup Files
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < ./backups/income_backup.sql
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < ./backups/expense_backup.sql
docker compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < ./backups/transactions_backup.sql