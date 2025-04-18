
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
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(255) NOT NULL, -- 'Deposit', 'Withdrawal', 'Transfer_out', 'Transfer_into'
    amount NUMERIC(10, 2) NOT NULL,
    fund_category VARCHAR(255),
    source_notes TEXT,
    transfer_to_account VARCHAR(255),
    transfer_to_fund_category VARCHAR(255)
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


-- Example: Insert some sample transaction data
INSERT INTO transactions (date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account, transfer_to_fund_category) VALUES
    ('2025-04-15', 'Checking Account', 'Deposit', 1200.00, 'Income', 'Monthly Salary', NULL, NULL),
    ('2025-04-15', 'Credit Card', 'Withdrawal', -35.50, 'Groceries', 'Lunch at store', NULL, NULL),
    ('2025-04-16', 'Savings Account', 'Deposit', 500.00, 'Savings', 'Transfer from Checking', 'Checking Account', NULL),
    ('2025-04-16', 'Investment Account - RRSP', 'Deposit', 200.00, 'Retirement Savings', 'Regular Contribution', NULL, NULL),
    ('2025-04-17', 'Checking Account', 'Withdrawal', -75.00, 'Utilities', 'Electricity Bill', NULL, NULL),
    ('2025-04-17', 'Checking Account', 'Transfer_out', -100.00, NULL, 'Transfer to TFSA', 'Investment Account - TFSA', 'TFSA Savings'),
    ('2025-04-17', 'Investment Account - TFSA', 'Transfer_into', 100.00, 'TFSA Savings', 'Transfer from Checking', 'Checking Account', NULL),
    ('2025-04-18', 'Checking Account', 'Withdrawal', -12.00, 'Coffee', 'Morning coffee', NULL, NULL),
    ('2025-04-18', 'Credit Card', 'Withdrawal', -60.00, 'Entertainment', 'Movie tickets', NULL, NULL),
    ('2025-04-19', 'Savings Account', 'Withdrawal', -25.00, 'Emergency Fund', 'Small unexpected expense', NULL, NULL);

   
   