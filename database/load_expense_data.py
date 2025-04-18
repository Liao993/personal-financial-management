import pandas as pd

def load_expenses(conn):
    CSV_FILE_PATH = '/historical_data/expenses.csv' # Assuming a separate expenses.csv
    cursor = conn.cursor()
    try:
        df = pd.read_csv(CSV_FILE_PATH, header=0)
        print(f"Successfully read CSV file: {CSV_FILE_PATH}")
        for index, row in df.iterrows():
            try:
                expense_date_series = row.get('expense_date') # Adjust column name
                if pd.notna(expense_date_series):
                    expense_date = expense_date_series.to_pydatetime()
                else:
                    print(f"Warning: Skipping expense row {index} due to invalid expense_date.")
                    continue
                store = row.get('store') # Adjust column name
                category = row.get('category') # Adjust column name
                amount = row.get('amount') # Adjust column name

                if all([expense_date, store, category, pd.notna(amount)]):
                    query = """
                        INSERT INTO expenses (date, store, category, amount)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (expense_date, store, category, amount))
                else:
                    print(f"Skipping expense row {index} due to missing essential data.")
            except Exception as e:
                print(f"Error processing expense row {index}: {e}")
        conn.commit()
        print("Expenses data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error reading expenses CSV file: {e}")