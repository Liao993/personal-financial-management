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

        # 1. Insert income row and return the new id
        query = """
            INSERT INTO income (date, amount, source, regular, notes, deposit_account)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = (
            validated_data["date"],
            validated_data["amount"],
            validated_data["source"],
            validated_data["regular"],
            validated_data["notes"],
            deposit_account,
        )
        cursor.execute(query, values)
        new_income_id = cursor.fetchone()[0]

        # 2. For non-chequing accounts auto-create a linked Deposit transaction
        if not _is_chequing_account(deposit_account):
            fund_cat = _fund_category_for_account(deposit_account)
            source_label = validated_data.get("source", "income")
            source_notes = f"income deposit – {source_label}"
            cursor.execute(
                """
                INSERT INTO transactions (
                    date, account_name, transaction_type, amount,
                    fund_category, source_notes, income_id
                )
                VALUES (%s, %s, 'Deposit', %s, %s, %s, %s)
                """,
                (
                    validated_data["date"],
                    deposit_account,
                    validated_data["amount"],
                    fund_cat,
                    source_notes,
                    new_income_id,
                ),
            )

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

def fetch_annual_income_by_month(year):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount) As amount
            FROM income
            WHERE EXTRACT(YEAR FROM date) = %s
            GROUP BY EXTRACT(MONTH FROM date)
            ORDER BY month;
    """
        try:
            cursor.execute(query, (year,))
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


def fetch_all_income_by_month():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT CAST(EXTRACT(YEAR FROM date) AS INTEGER) AS year,
                   CAST(EXTRACT(MONTH FROM date) AS INTEGER) AS month,
                   SUM(amount) AS amount
            FROM income
            GROUP BY 1, 2
            ORDER BY year, month;
        """
        try:
            cursor.execute(query)
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
        query = """
        SELECT SUM(amount)
        FROM income
        WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s
          AND deposit_account ILIKE '%%chequing%%';
    """
        try:
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
    """Fetches the last 20 income records including the deposit account."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT date, amount, source, notes, deposit_account
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
            st.error(f"Error retrieving last two income data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
