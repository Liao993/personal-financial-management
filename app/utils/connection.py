
"""
import psycopg2
import os

def get_db_connection():
    conn = None
    error = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT"),
        )
        print("Database connection successful.")
    except psycopg2.Error as e:
        error = f"Error connecting to the database: {e}"
        print(error)
    return conn, error

# Example usage (can be removed or used for testing)
if __name__ == "__main__":
    connection, connection_error = get_db_connection()
    if connection:
        connection.close()
    else:
        print(f"Failed to establish connection: {connection_error}")
"""