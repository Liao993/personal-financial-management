import sys
import os

# Append the current app directory to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.utils.connection import get_db_connection


SCHEMA_FILES = [
    '03_expense_transaction_sync.sql',
    '04_portfolio_schema.sql',
    '05_expense_ingestion_dedupe.sql',
]


def run_update():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            for schema_file in SCHEMA_FILES:
                sql_file_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), 'database', schema_file)
                )
                with open(sql_file_path, 'r') as f:
                    sql = f.read()

                print(f"Applying {schema_file}...")
                cursor.execute(sql)

            conn.commit()
            print("Schema updated successfully!")
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        print("Failed to get DB connection")

if __name__ == '__main__':
    run_update()
