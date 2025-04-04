-- database/income.sql

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

-- Example: Insert some sample income data
-- Replace the date and amount with actual values.
INSERT INTO income (date, amount, source) VALUES
    ('2024-01-15', 2500.00, 'Salary'),
    ('2024-02-01', 500.00, 'Freelance Work'),
    ('2024-02-28', 3000.00, 'Salary'),
    ('2024-03-05', 100.00, 'Interest');