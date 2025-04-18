import pandas as pd


def load_transactions(conn):
    CSV_FILE_PATH = '/historical_data/transactions.csv'
    cursor = conn.cursor()
    try:
        df = pd.read_csv(CSV_FILE_PATH, header=0)
        print(f"Successfully read CSV file: {CSV_FILE_PATH}")
        for index, row in df.iterrows():
            try:
                transaction_date_series = row.get('transaction_date')
                if pd.notna(transaction_date_series):
                    transaction_date = transaction_date_series.to_pydatetime()
                else:
                    print(f"Warning: Skipping transaction row {index} due to invalid transaction_date.")
                    continue
                account_name = row.get('account_name')
                transaction_type = row.get('transaction_type')
                amount = row.get('amount')
                fund_category = row.get('fund_category')
                source_notes = row.get('source_notes')
                transfer_to_account = row.get('transfer_to_account')
                transfer_to_fund_category = row.get('transfer_to_fund_category')

                if all([transaction_date, account_name, transaction_type, pd.notna(amount)]):
                    query = """
                        INSERT INTO transactions (date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account, transfer_to_fund_category)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (transaction_date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account, transfer_to_fund_category))
                else:
                    print(f"Skipping transaction row {index} due to missing essential data.")
            except Exception as e:
                print(f"Error processing transaction row {index}: {e}")
        conn.commit()
        print("Transactions data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error reading transactions CSV file: {e}")