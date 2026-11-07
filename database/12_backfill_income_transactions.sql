-- Backfill the transaction ledger for historical income rows.
-- New income entries are linked by income_backend.py; this migration makes
-- older income records follow the same account-flow model.
UPDATE income
SET deposit_account = COALESCE(
    (
        SELECT account_name
        FROM transactions
        WHERE account_name ILIKE '%chequing%'
        ORDER BY transaction_id
        LIMIT 1
    ),
    'Main Chequing'
)
WHERE deposit_account IS NULL;

INSERT INTO transactions (
    date, account_name, transaction_type, amount,
    fund_category, transaction_category, source_notes, income_id
)
SELECT
    i.date,
    i.deposit_account,
    'Deposit',
    i.amount,
    CASE
        WHEN i.deposit_account ILIKE '%TFSA%'
          OR i.deposit_account ILIKE '%RRSP%' THEN 'Retirement Saving'
        WHEN i.deposit_account ILIKE '%Notice%' THEN 'Medium-term Saving'
        WHEN i.deposit_account ILIKE '%Emergency%' THEN 'Emergency Funds'
        WHEN i.deposit_account ILIKE '%Travel%' THEN 'Traveling Funds'
        WHEN i.deposit_account ILIKE '%House%'
          OR i.deposit_account ILIKE '%Home%' THEN 'House'
        ELSE 'Others'
    END,
    'Income',
    'income deposit – ' || i.source,
    i.id
FROM income i
WHERE i.deposit_account IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM transactions t
      WHERE t.income_id = i.id
  );
