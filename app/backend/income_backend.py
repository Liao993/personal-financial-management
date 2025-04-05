
from database.connection import get_db_connection # type: ignore
import psycopg2
def check_database_connection():
    conn, error = get_db_connection()
    if conn:
        print("Successfully connected to the database from income_backend.py")
        conn.close()
        return True
    else:
        print(f"Failed to connect to the database from income_backend.py: {error}")
        return False

def process_income_data(validated_data: dict):
    print("Received validated income data in income_backend.py:")
    print(validated_data)
    # Here you would add your logic to interact with the database
    # using the validated_data (e.g., insert into the income table)
    conn, error = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO income (date, amount, source, regular)
                VALUES (%s, %s, %s, %s)
                """,
                (validated_data['date'], validated_data['amount'], validated_data['source'], validated_data['regular']),
            )
            conn.commit()
            print("Income data successfully inserted into the database.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error inserting income data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Database connection failed, cannot insert data.")

if __name__ == "__main__":
    check_database_connection()