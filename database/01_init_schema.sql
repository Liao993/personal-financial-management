
-- Create the income table if it doesn't exist
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    source VARCHAR(255) NOT NULL,
    regular BOOLEAN NOT NULL DEFAULT TRUE, -- Use BOOLEAN here
    notes TEXT
);


-- Create the expense table if it doesn't exist
CREATE TABLE IF NOT EXISTS expense (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    date DATE NOT NULL,
    items VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(255) NOT NULL,
    source_notes VARCHAR(255),
    payment_method VARCHAR(255),
    traveling_category VARCHAR(255),
    trip VARCHAR(255),
    amount_for_number_of_travelers INTEGER,
    paid_for_number_of_travlerers INTEGER,
    house_category VARCHAR(255),

    -- This line prevents the ETL from creating duplicates
    CONSTRAINT unique_expense_entry UNIQUE (date, items, amount, source_notes)
    
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(255) NOT NULL, -- 'Deposit', 'Withdrawal', 'Transfer_out', 'Transfer_into'
    amount NUMERIC(10, 2) NOT NULL,
    fund_category VARCHAR(255),
    source_notes TEXT,
    prepaid BOOLEAN NOT NULL DEFAULT FALSE,
    transfer_to_account VARCHAR(255)
);


   