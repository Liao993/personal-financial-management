
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
    traveling_category VARCHAR(255),
    trip VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(255) NOT NULL, -- 'Deposit', 'Withdrawal', 'Transfer_out', 'Transfer_into'
    amount NUMERIC(10, 2) NOT NULL,
    fund_category VARCHAR(255),
    source_notes TEXT,
    transfer_to_account VARCHAR(255)
);

-- New table for tracking internal money movement before formal booking
CREATE TABLE IF NOT EXISTS cashflow (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    account_name VARCHAR(255) NOT NULL, -- Account the money is moving *from* (e.g., Checking, Savings)
    transaction_type VARCHAR(255) NOT NULL, -- 'Deposit', 'Withdrawal', 'Internal_Transfer'
    amount NUMERIC(10, 2) NOT NULL,
    purpose VARCHAR(255), -- Action the money is being used for
    transfer_to_account VARCHAR(255), -- Account the money is moving *to* (if it's a transfer)
    source_notes TEXT -- Any additional notes or context
);


   
   