
from decimal import Decimal
from datetime import datetime, date
from typing import Any

from utils.connection import get_db_connection


ACCOUNT_TYPES = ("TFSA", "RRSP")


def fetch_retirement_limits() -> dict[str, Any]:
    """
    Return persisted retirement account limits and their last-updated timestamps.

    Example:
    {
        "TFSA": Decimal("100000"),
        "RRSP": Decimal("50000"),
        "TFSA_updated_at": datetime(...),
        "RRSP_updated_at": datetime(...)
    }
    """

    conn = get_db_connection()

    if conn is None:
        return {
            "TFSA": Decimal("0"),
            "RRSP": Decimal("0"),
            "TFSA_updated_at": None,
            "RRSP_updated_at": None,
        }

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT account_type, total_limit, updated_at
                FROM retirement_account_limits
                WHERE account_type IN ('TFSA', 'RRSP')
                """
            )

            rows = cursor.fetchall()

            limits = {
                account_type: {
                    "total_limit": total_limit,
                    "updated_at": updated_at,
                }
                for account_type, total_limit, updated_at in rows
            }

            result = {}

            for account_type in ACCOUNT_TYPES:
                account_data = limits.get(account_type, {})

                result[account_type] = account_data.get(
                    "total_limit", Decimal("0")
                )

                result[f"{account_type}_updated_at"] = account_data.get(
                    "updated_at"
                )

            return result

    finally:
        conn.close()


def update_retirement_limits(
    tfsa_limit: Decimal,
    rrsp_limit: Decimal,
) -> None:
    """
    Persist both retirement account limits in one transaction.
    Update the timestamp whenever the limits are saved.
    """

    conn = get_db_connection()

    if conn is None:
        raise RuntimeError("Could not connect to the database.")

    try:
        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO retirement_account_limits (
                    account_type,
                    total_limit,
                    updated_at
                )
                VALUES (%s, %s, CURRENT_TIMESTAMP)

                ON CONFLICT (account_type) DO UPDATE SET
                    total_limit = EXCLUDED.total_limit,
                    updated_at = CURRENT_TIMESTAMP
                """,
                [
                    ("TFSA", tfsa_limit),
                    ("RRSP", rrsp_limit),
                ],
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
