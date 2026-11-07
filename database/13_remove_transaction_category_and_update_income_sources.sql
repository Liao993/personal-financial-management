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
