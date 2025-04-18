import os
import psycopg2 # type: ignore
from load_transaction_data import load_transactions
from load_expense_data import load_expenses
from load_income_data import load_income

# Database connection details (assuming environment variables are set)
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")

def main():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
        print("Successfully connected to the database!")

        load_transactions(conn)
        load_expenses(conn)
        load_income(conn)

        conn.close()
        print("Database connection closed.")

    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    main()