import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore
import os


# ---------------------------------------------------------------------------
# Fund category auto-mapping from account name
# ---------------------------------------------------------------------------

_ACCOUNT_FUND_MAP = {
    "TFSA":         "Retirement Saving",
    "RRSP":         "Retirement Saving",
    "House":        "House",
    "Home":         "House",
    "Notice":       "Medium-term Saving",
    "Emergency":    "Emergency Funds",
    "Travel":       "Traveling Funds",
}


def _fund_category_for_account(account_name: str) -> str:
    """Auto-map an account name to the closest fund_category label.
    Falls back to 'Others' when no known keyword is found.
    """
    
    for keyword, category in _ACCOUNT_FUND_MAP.items():
        if keyword.lower() in account_name.lower():
            return category
    return "Others"


def _is_chequing_account(account_name: str) -> bool:
    """Returns True if the account name contains 'chequing' (case-insensitive)."""
    return "chequing" in account_name.lower()


def _default_chequing_account() -> str:
    """Returns the first account in ACCOUNT_NAMES env var (the default chequing)."""
    raw = os.environ.get("ACCOUNT_NAMES", "")
    accounts = [a.strip() for a in raw.split(",") if a.strip()]
    return accounts[0] if accounts else "Main Chequing"


def _income_schema_columns(cursor) -> set[str]:
    """Return optional income schema columns present in this database."""
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'income'
          AND column_name IN ('deposit_account', 'exclude_from_monthly', 'fund_category')
        """
    )
    return {row[0] for row in cursor.fetchall()}


def _monthly_income_clause(cursor) -> str:
    """Return the monthly-inclusion predicate when the migration is present."""
    return "exclude_from_monthly = FALSE" if "exclude_from_monthly" in _income_schema_columns(cursor) else "TRUE"


# ---------------------------------------------------------------------------
# Insert income + optional linked deposit transaction
# ---------------------------------------------------------------------------

def insert_income_data(validated_data: dict):
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot insert data.")
        return

    deposit_account = validated_data.get("deposit_account") or _default_chequing_account()

    try:
        cursor = conn.cursor()
        optional_columns = _income_schema_columns(cursor)
        has_deposit_account = "deposit_account" in optional_columns
        has_exclude_from_monthly = "exclude_from_monthly" in optional_columns
        has_fund_category = "fund_category" in optional_columns

        # 1. Insert income row and return the new id
        columns = ["date", "amount", "source", "regular", "notes"]
        values = [
            validated_data["date"], validated_data["amount"],
            validated_data["source"], validated_data["regular"],
            validated_data["notes"],
        ]
        if has_deposit_account:
            columns.append("deposit_account")
            values.append(deposit_account)
        if has_exclude_from_monthly:
            columns.append("exclude_from_monthly")
            values.append(validated_data.get("exclude_from_monthly", False))
        if has_fund_category:
            columns.append("fund_category")
            values.append(validated_data.get("fund_category"))
        placeholders = ", ".join(["%s"] * len(values))
        query = f"""
            INSERT INTO income ({', '.join(columns)})
            VALUES ({placeholders})
            RETURNING id
        """
        cursor.execute(query, values)
        new_income_id = cursor.fetchone()[0]

        # The database trigger creates/synchronizes the linked transaction.

        conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error inserting income data: {e}")
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def fetch_annual_income_by_month(year, excluded_sources=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        monthly_clause = _monthly_income_clause(cursor)
        query = """
            SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount) As amount
            FROM income
            WHERE EXTRACT(YEAR FROM date) = %s
              AND {monthly_clause}
        """
        query = query.format(monthly_clause=monthly_clause)
        params = [year]
        if excluded_sources:
            query += " AND source <> ALL(%s)"
            params.append(list(excluded_sources))
        query += """
            GROUP BY EXTRACT(MONTH FROM date)
            ORDER BY month;
        """
        try:
            cursor.execute(query, params)
            columns = ['month', 'total_income']
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=columns)

        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []


def fetch_all_income_by_month(excluded_sources=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        monthly_clause = _monthly_income_clause(cursor)
        query = """
            SELECT CAST(EXTRACT(YEAR FROM date) AS INTEGER) AS year,
                   CAST(EXTRACT(MONTH FROM date) AS INTEGER) AS month,
                   SUM(amount) AS amount
            FROM income
            WHERE {monthly_clause}
        """
        query = query.format(monthly_clause=monthly_clause)
        params = []
        if excluded_sources:
            query += " AND source <> ALL(%s)"
            params.append(list(excluded_sources))
        query += """
            GROUP BY 1, 2
            ORDER BY year, month;
        """
        try:
            cursor.execute(query, params)
            columns = ["year", "month", "total_income"]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return pd.DataFrame(columns=["year", "month", "total_income"])
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame(columns=["year", "month", "total_income"])

def fetch_monthly_income(year, month):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            income_columns = _income_schema_columns(cursor)
            if "exclude_from_monthly" in income_columns:
                account_filter = "AND exclude_from_monthly = FALSE"
            elif "deposit_account" in income_columns:
                account_filter = "AND deposit_account ILIKE '%%chequing%%'"
            else:
                account_filter = ""
            query = f"""
                SELECT SUM(amount)
                FROM income
                WHERE EXTRACT(YEAR FROM date) = %s
                  AND EXTRACT(MONTH FROM date) = %s
                  {account_filter};
            """
            cursor.execute(query, (year, month))
            result = cursor.fetchone()
            if result and result[0] is not None:
                return float(result[0])
            else:
                return 0.0

        except psycopg2.Error as e:
            st.error(f"Error retrieving income data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return []

def fetch_last_income_data():
    """Fetches the last 20 income records across current and legacy schemas."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            has_deposit_account = "deposit_account" in _income_schema_columns(cursor)
            deposit_column = "deposit_account" if has_deposit_account else "NULL::varchar AS deposit_account"
            query = f"""
                SELECT date, amount, source, notes, {deposit_column}
                FROM income
                ORDER BY date DESC
                LIMIT 20;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving last income data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
