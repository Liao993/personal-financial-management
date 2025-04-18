import pandas as pd

def load_income(conn):
    CSV_FILE_PATH = '/historical_data/income.csv' # Assuming a separate income.csv
    cursor = conn.cursor()
    try:
        df = pd.read_csv(CSV_FILE_PATH, header=0)
        print(f"Successfully read CSV file: {CSV_FILE_PATH}")
        for index, row in df.iterrows():
            try:
                income_date_series = row.get('income_date') # Adjust column name
                if pd.notna(income_date_series):
                    income_date = income_date_series.to_pydatetime()
                else:
                    print(f"Warning: Skipping income row {index} due to invalid income_date.")
                    continue
                source = row.get('source') # Adjust column name
                amount = row.get('amount') # Adjust column name
                notes = row.get('notes') # Adjust column name

                if all([income_date, source, pd.notna(amount)]):
                    query = """
                        INSERT INTO income (date, source, amount, notes)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (income_date, source, amount, notes))
                else:
                    print(f"Skipping income row {index} due to missing essential data.")
            except Exception as e:
                print(f"Error processing income row {index}: {e}")
        conn.commit()
        print("Income data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error reading income CSV file: {e}")