\COPY transactions (date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account) FROM '/csv_data/transaction_cleaned.csv' WITH (FORMAT CSV, HEADER); 

\COPY income (date, amount, source, regular, notes) FROM '/csv_data/income_cleaned.csv' WITH (FORMAT CSV, HEADER); 

\COPY expense (date, items, amount, category, traveling_category, trip) FROM '/csv_data/expense_cleaned.csv' WITH (FORMAT CSV, HEADER);  
