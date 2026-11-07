-- Remove the redundant transaction-purpose field and normalize earning names.
ALTER TABLE transactions
    DROP CONSTRAINT IF EXISTS transactions_transaction_category_check;

ALTER TABLE transactions
    DROP COLUMN IF EXISTS transaction_category;

UPDATE income
SET source = 'Salary',
    notes = CASE
        WHEN notes IS NULL OR trim(notes) = '' THEN 'Gov'
        WHEN notes ILIKE '%Gov%' THEN notes
        ELSE notes || ' (Gov)'
    END
WHERE lower(trim(source)) = 'gov';

UPDATE income
SET source = 'Interest Earning',
    notes = CASE
        WHEN notes IS NULL OR trim(notes) = '' THEN 'Interest'
        WHEN notes ILIKE '%Interest%' THEN notes
        ELSE notes || ' (Interest)'
    END
WHERE lower(trim(source)) = 'interest';

-- Normalize legacy labels to the current earning-source vocabulary.
UPDATE income
SET source = 'Tax Return'
WHERE lower(trim(source)) = 'tax refund';

UPDATE income
SET source = 'Side Hustle'
WHERE lower(trim(source)) = 'freelance';

UPDATE income
SET source = 'Investment'
WHERE lower(trim(source)) = 'dividend';
