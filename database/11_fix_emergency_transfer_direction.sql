-- This row was stored as a negative Transfer In. It is an outflow from the
-- Emergency Funds category and must be represented as Transfer Out instead.
UPDATE transactions
SET transaction_type = 'Transfer Out',
    amount = -ABS(amount),
    transaction_category = 'Account Balance'
WHERE transaction_id = 269
  AND date = '2026-04-09'
  AND account_name = 'RBC_DI TFSA'
  AND transaction_type = 'Transfer In'
  AND amount = -2565.25
  AND fund_category = 'Emergency Funds';
