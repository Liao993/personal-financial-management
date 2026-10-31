-- 07_transaction_category.sql
-- Classifies the purpose of a transaction independently from its direction.

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS transaction_category VARCHAR(255) NOT NULL DEFAULT 'Other';

-- Backfill existing rows conservatively. Linked expense withdrawals are
-- spending; transfers are account-balance movements; calculated deposits are
-- monthly savings; income-linked deposits are income.
UPDATE transactions
SET transaction_category = CASE
    WHEN expense_id IS NOT NULL THEN 'Spending'
    WHEN transaction_type IN ('Transfer Out', 'Transfer In') THEN 'Account Balance'
    WHEN source_notes ILIKE 'saved from%' THEN 'Monthly Saving'
    WHEN income_id IS NOT NULL THEN 'Income'
    WHEN transaction_type = 'Withdrawal' THEN 'Spending'
    ELSE 'Other'
END;

ALTER TABLE transactions
    DROP CONSTRAINT IF EXISTS transactions_transaction_category_check;

ALTER TABLE transactions
    ADD CONSTRAINT transactions_transaction_category_check
    CHECK (transaction_category IN (
        'Account Balance', 'Spending', 'Monthly Saving',
        'Investment', 'Income', 'Other'
    ));
