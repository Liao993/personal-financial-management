import streamlit as st  # type: ignore
from utils.connection import get_db_connection  # type: ignore
import psycopg2  # type: ignore
import pandas as pd  # type: ignore
import os

DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt_budget")


def insert_expense_data(validated_data: dict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO expense (
                    date, items, amount, category,
                    traveling_category, trip, payment_method, source_notes,
                    house_category,
                    amount_for_number_of_travelers,
                    paid_for_number_of_travlerers,
                    exclude_from_monthly,
                    target_fund_category,
                    split_fund_category_1,
                    split_amount_1
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                validated_data["date"],
                validated_data["items"],
                validated_data["amount"],
                validated_data["category"],
                validated_data.get("traveling_category"),
                validated_data.get("trip"),
                validated_data.get("payment_method"),
                validated_data.get("source_notes"),
                validated_data.get("house_category"),
                validated_data.get("amount_for_number_of_travelers"),
                validated_data.get("paid_for_number_of_travlerers"),
                validated_data.get("exclude_from_monthly", False),
                validated_data.get("target_fund_category"),
                validated_data.get("split_fund_category_1"),
                validated_data.get("split_amount_1") or 0.0,
            )
            cursor.execute(query, values)
            conn.commit()
            st.success("Transaction recorded successfully!")

        except psycopg2.Error as e:
            conn.rollback()
            st.error(f"Error inserting expense data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot insert data.")


def fetch_monthly_expenses_with_summary(year, month):
    """
    Used by Monthly Calculation (Page 6).
    Excludes fund-withdrawal expenses (exclude_from_monthly=TRUE) and House.
    The dbt view already applies this filter, so querying the view is correct.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # The dbt view already filters exclude_from_monthly=FALSE and category != 'House'
        query = f"""
            SELECT date, amount, category, summary_category
            FROM {DBT_SCHEMA}.intermediate_expenses_with_summary
            WHERE EXTRACT(YEAR FROM date) = %s
              AND EXTRACT(MONTH FROM date) = %s;
        """
        try:
            cursor.execute(query, (year, month))
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            return df
        except psycopg2.Error as e:
            st.error(f"Error fetching monthly expenses with summary: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.error("Database connection failed, cannot fetch expense data.")
        return pd.DataFrame()


def fetch_annual_expense(year):
    """
    Used by Historical Stats (Page 8).
    The dbt view already filters exclude_from_monthly=FALSE and category != 'House'.
    Traveling is included here because historical stats shows it separately.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if isinstance(year, int):
                query = f"""
                    SELECT date, amount, category, summary_category
                    FROM {DBT_SCHEMA}.intermediate_expenses_with_summary
                    WHERE EXTRACT(YEAR FROM date) = %s;
                """
                cursor.execute(query, (year,))
            else:
                st.error("Invalid year format. Please select a valid year.")
                return pd.DataFrame()

            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()


def fetch_last_expense_data():
    """
    Used on expense input page to show recent entries.
    Shows ALL expenses including exclude_from_monthly ones
    so you can see what you just recorded.
    House excluded for display clarity.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT date, items, amount, category, payment_method, exclude_from_monthly
                FROM expense
                WHERE category != 'House'
                  AND house_category IS NULL
                  AND date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                ORDER BY date DESC, id DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving last expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()


def fetch_house_expesne():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # House expenses come from the raw expense table, not the dbt view
            # because the dbt view filters out House category
            query = """
                SELECT id, date, items, amount, category, house_category,
                    CASE
                        WHEN house_category = 'Mortgage' THEN 'Mortgage'
                        WHEN house_category = 'Extra Mortgage' THEN 'Extra Mortgage'
                        WHEN house_category IN ('Internet', 'Electricity', 'Insurance',
                             'Water & Sewage', 'Oil', 'Snow Removal') THEN 'Regular Expenses'
                        WHEN house_category LIKE '%Repair%' THEN 'Repairs'
                        WHEN house_category LIKE '%Tax%' THEN 'Tax'
                        ELSE 'Other'
                    END AS house_summary_category,
                    EXTRACT(MONTH FROM date) AS month,
                    EXTRACT(YEAR FROM date)  AS year
                FROM expense
                WHERE category = 'House'
                   OR house_category IS NOT NULL
                ORDER BY date DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving house expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()
