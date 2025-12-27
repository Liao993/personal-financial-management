import streamlit as st # type: ignore
from utils.connection import get_db_connection # type: ignore
import psycopg2 # type: ignore
import pandas as pd # type: ignore
def insert_expense_data_with_source(validated_data: dict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 1. Update the Query string with new columns
            query = """
                INSERT INTO expense (
                    date, items, amount, category, 
                    traveling_category, trip, source_notes, 
                    house_category, 
                    amount_for_number_of_travelers, 
                    paid_for_number_of_travlerers
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 2. Map the values (using .get for everything that isn't mandatory)
            values = (
                validated_data['date'],
                validated_data['items'],
                validated_data['amount'],
                validated_data['category'],
                validated_data.get('traveling_category'),
                validated_data.get('trip'),
                validated_data.get('source_notes'),
                validated_data.get('house_category'),
                validated_data.get('amount_for_number_of_travelers'),
                validated_data.get('paid_for_number_of_travlerers')
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

# Get Montlhy Expenses by Summary Category
def fetch_monthly_expenses_with_summary(year, month):

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT date, amount, category, summary_category
        FROM dbt_budget.intermediate_expenses_with_summary
        WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s AND category != 'House';
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
    """Fetches annual expense data from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
         
            if isinstance(year, int):
                query = """
                    SELECT date, amount, category, summary_category
                    FROM dbt_budget.intermediate_expenses_with_summary
                    WHERE EXTRACT(YEAR FROM date) = %s AND category != 'Traveling' AND category != 'House';
                """
                cursor.execute(query, (year,))
            else:
                st.error("Invalid year format.  Please select a valid year.")
                return pd.DataFrame()

            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()

def fetch_last_expense_data():
    """Fetches the last two expense data from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT date, items, amount, category
                FROM expense
                Where category != 'House'
                ORDER BY date DESC
                LIMIT 10;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving last two expense data: {e}")
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
            query = """
                SELECT id, date, items, amount, category, house_category, house_summary_category, 
                    EXTRACT(MONTH FROM date) AS month, EXTRACT(YEAR FROM date) AS year
                FROM dbt_budget.intermediate_expenses_with_summary
                WHERE category = 'House'
                ORDER BY date DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]  # Get column names
            df = pd.DataFrame(rows, columns=cols)
            return df

        except psycopg2.Error as e:
            st.error(f"Error retrieving last two expense data: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    else:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()