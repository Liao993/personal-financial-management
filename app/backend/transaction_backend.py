import streamlit as st  # type: ignore
from utils.connection import get_db_connection  # type: ignore
import psycopg2  # type: ignore
import pandas as pd  # type: ignore


def insert_transaction_data(validated_data: dict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        success = False
        try:
            query = """
                INSERT INTO transactions (
                    date, account_name, transaction_type, amount,
                    fund_category, source_notes, transfer_to_account
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                validated_data["date"],
                validated_data["account_name"],
                validated_data["transaction_type"],
                validated_data["amount"],
                validated_data["fund_category"],
                validated_data["source_notes"],
                validated_data["transfer_to_account"],
            )
            cursor.execute(query, values)
            conn.commit()
            success = True
        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting transaction data: {e}")
        finally:
            cursor.close()
            conn.close()
        return success
    else:
        st.info("Database connection failed, cannot insert data.")
        return False


def fetch_transaction_data_by_month(year):
    """
    Used by Monthly Calculation and Historical Stats.
    Only counts 'saved from' deposits — not expense-linked withdrawals.
    """
    search_pattern = "saved from%"
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT EXTRACT(MONTH FROM date) AS month,
                   fund_category,
                   SUM(amount) AS total_amount
            FROM transactions
            WHERE EXTRACT(YEAR FROM date) = %s
              AND transaction_type = 'Deposit'
              AND source_notes LIKE %s
              AND expense_id IS NULL
            GROUP BY EXTRACT(MONTH FROM date), fund_category
            ORDER BY month;
        """
        try:
            cursor.execute(query, (year, search_pattern))
            columns = ["month", "fund_category", "total_amount"]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()


def fetch_transaction_data_by_year(year):
    """
    Used by Historical Stats for yearly saving totals.
    Excludes expense-linked transactions to avoid double-counting.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT fund_category, SUM(amount) AS total_amount
            FROM transactions
            WHERE EXTRACT(YEAR FROM date) = %s
              AND expense_id IS NULL
            GROUP BY fund_category;
        """
        try:
            cursor.execute(query, (year,))
            columns = ["fund_category", "total_amount"]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()


def fetch_transaction_deposit_check(year, month):
    """
    Checks if saving deposits already exist for a given month.
    Used by Monthly Calculation to decide Save vs Rerun.
    """
    conn = get_db_connection()
    search_pattern = "saved from%"
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT transaction_id, date, fund_category, amount
            FROM transactions
            WHERE EXTRACT(YEAR FROM date)  = %s
              AND EXTRACT(MONTH FROM date) = %s
              AND transaction_type = 'Deposit'
              AND source_notes LIKE %s
              AND expense_id IS NULL;
        """
        try:
            cursor.execute(query, (year, month, search_pattern))
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            return df
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()


def fetch_all_transaction_data():
    """
    Fetches all manually recorded transactions (not expense-linked).
    Used by Current Saving Status pivot table (Page 10).
    Expense-linked withdrawals are shown separately on that page.
    """
    conn = get_db_connection()
    columns = []
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT *
            FROM transactions
            WHERE expense_id IS NULL
        """
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            if data:
                return columns, pd.DataFrame(data, columns=columns)
            else:
                return columns, pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving transaction data: {e}")
            return columns, pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return columns, pd.DataFrame()


def fetch_expense_withdrawal_transactions():
    """
    Fetches all auto-created withdrawal transactions linked to expenses.
    Used by Current Saving Status (Page 10) to show fund deductions.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT
                t.transaction_id,
                t.date,
                t.account_name,
                t.amount,
                t.fund_category,
                t.transaction_type,
                t.expense_id,
                t.trip,
                e.items       AS expense_items,
                e.category    AS expense_category,
                e.source_notes
            FROM transactions t
            JOIN expense e ON t.expense_id = e.id
            WHERE t.expense_id IS NOT NULL
            ORDER BY t.date DESC, t.transaction_id DESC
        """
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame(columns=columns)
        except psycopg2.Error as e:
            st.error(f"Error retrieving expense-linked transactions: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()


def fetch_last_transaction_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT *
            FROM transactions
            ORDER BY date DESC, transaction_id DESC
            LIMIT 20;
        """
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            if data:
                return pd.DataFrame(data, columns=columns)
            else:
                return pd.DataFrame()
        except psycopg2.Error as e:
            st.error(f"Error retrieving last transaction data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve last transaction data.")
        return pd.DataFrame()
