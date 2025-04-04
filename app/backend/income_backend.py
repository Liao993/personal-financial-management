"""
from app.utils.database import get_db_connection
from app.models.income import Income
import psycopg2

def insert_income(income: Income):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            
            INSERT INTO income (date, amount, source, regular)
            VALUES (%s, %s, %s, %s)
            ,
            (income.date, income.amount, income.source, income.regular),
        )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Add other income-related database functions here (e.g., fetching income data)
"""