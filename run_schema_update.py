import sys
import os

# Append the current app directory to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.utils.connection import get_db_connection


def run_update():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', '03_schema_extension.sql'))
        with open(sql_file_path, 'r') as f:
            sql = f.read()
        try:
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
