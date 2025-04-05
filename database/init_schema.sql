
-- Create the income table if it doesn't exist
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    source VARCHAR(255) NOT NULL,
    regular BOOLEAN NOT NULL DEFAULT TRUE -- Use BOOLEAN here
);

-- Create the store table if it doesn't exist
CREATE TABLE IF NOT EXISTS store (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    store_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL
);

-- Create the expense table if it doesn't exist
CREATE TABLE IF NOT EXISTS expense (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    date DATE NOT NULL,
    items VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(255) NOT NULL
);

-- Example: Insert some sample income data
INSERT INTO income (date, amount, source) VALUES
    ('2099-01-15', 2500.00, 'Salary'),
    ('2099-02-01', 500.00, 'Freelance Work'),
    ('2099-02-28', 3000.00, 'Salary'),
    ('2099-02-28', 70000.00, 'Salary'),
    ('2099-03-05', 100.00, 'Interest');

INSERT INTO expense (date, items, amount, category) VALUES
    ('2099-01-15', 'Walmart', 12500.00, 'Grocery'),
    ('2099-02-01', 'Anchery', 11500.00, 'Entertainment'),
    ('2099-02-28', 'Home', 13000.00, 'Rent'),
    ('2099-03-05', 'Water', 5100.00, 'Utilities');

INSERT INTO store (store_name, category) VALUES
    ('Walmart', 'Grocery'),
    ('Best Buy', 'Electronics'),
    ('H&M', 'Clothing');
   
   