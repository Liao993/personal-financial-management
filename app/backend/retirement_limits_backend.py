from decimal import Decimal

from utils.connection import get_db_connection


ACCOUNT_TYPES = ("TFSA", "RRSP")


def fetch_retirement_limits() -> dict[str, Decimal]:
    """Return the persisted total limits keyed by account type."""
    conn = get_db_connection()
    if conn is None:
        return {account_type: Decimal("0") for account_type in ACCOUNT_TYPES}

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT account_type, total_limit
                FROM retirement_account_limits
                WHERE account_type IN ('TFSA', 'RRSP')
                """
            )
            limits = {account_type: amount for account_type, amount in cursor.fetchall()}
            return {
                account_type: limits.get(account_type, Decimal("0"))
                for account_type in ACCOUNT_TYPES
            }
    finally:
        conn.close()


def update_retirement_limits(tfsa_limit: Decimal, rrsp_limit: Decimal) -> None:
    """Persist both total limits in one transaction."""
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Could not connect to the database.")

    try:
        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO retirement_account_limits (account_type, total_limit)
                VALUES (%s, %s)
                ON CONFLICT (account_type) DO UPDATE SET
                    total_limit = EXCLUDED.total_limit,
                    updated_at = CURRENT_TIMESTAMP
                """,
                [("TFSA", tfsa_limit), ("RRSP", rrsp_limit)],
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
