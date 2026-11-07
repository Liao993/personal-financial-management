-- This row was entered as a Transfer In without a source account or matching
-- Transfer Out. It represents money entering the retirement fund from outside
-- the tracked accounts, so classify it as a Deposit instead.
UPDATE transactions
SET transaction_type = 'Deposit',
    source_notes = COALESCE(
        NULLIF(source_notes, ''),
        'External retirement deposit; original transfer source was not recorded'
    )
WHERE transaction_id = 268
  AND date = '2026-04-09'
  AND account_name = 'RBC_DI TFSA'
  AND transaction_type = 'Transfer In'
  AND amount = 2565.25
  AND fund_category = 'Retirement Saving'
  AND transfer_to_account IS NULL;
