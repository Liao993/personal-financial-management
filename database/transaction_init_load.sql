-- transaction_init_load.sql

\COPY transactions (date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account, transfer_to_fund_category) FROM '/csv_data/transaction_cleaned.csv' WITH (FORMAT CSV, HEADER);