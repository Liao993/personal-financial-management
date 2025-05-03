
-- Create the income table if it doesn't exist
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    source VARCHAR(255) NOT NULL,
    regular BOOLEAN NOT NULL DEFAULT TRUE, -- Use BOOLEAN here
    notes TEXT
);


-- Create the expense table if it doesn't exist
CREATE TABLE IF NOT EXISTS expense (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    date DATE NOT NULL,
    items VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(255) NOT NULL,
    traveling_category VARCHAR(255)
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

-- Example: Insert some sample income data
INSERT INTO income (date, amount, source, notes) VALUES
    ('2025-04-15', 1000.00, 'Part-time Job', 'Payment for April work'),
    ('2025-04-16', 50.00, 'Online Sale', NULL),
    ('2025-04-17', 25.00, 'Rebate', 'Cashback from purchase'),
    ('2025-04-18', 2000.00, 'Main Job', NULL),
    ('2025-04-19', 10.00, 'Gift', 'From a friend');

INSERT INTO expense (date, items, amount, category) VALUES
    ('2099-01-15', 'Walmart', 12500.00, 'Grocery'),
    ('2099-02-01', 'Anchery', 11500.00, 'Entertainment'),
    ('2099-02-28', 'Home', 13000.00, 'Rent'),
    ('2099-03-05', 'Water', 5100.00, 'Utilities');




   
   