-- Explicitly control whether an income participates in monthly saving.
-- Existing income rows remain included and are not linked retroactively.
ALTER TABLE income
    ADD COLUMN IF NOT EXISTS exclude_from_monthly BOOLEAN NOT NULL DEFAULT FALSE;

-- Historical income is not linked to the transaction ledger. Going forward,
-- only income explicitly excluded from monthly calculation receives a link.
UPDATE transactions AS t
SET income_id = NULL
FROM income AS i
WHERE t.income_id = i.id
  AND i.exclude_from_monthly = FALSE;

-- Store TFSA/RRSP contribution room by year. The displayed total is the sum
-- of all rows for each account type.
CREATE TABLE IF NOT EXISTS retirement_account_limits_by_year (
    account_type VARCHAR(10) NOT NULL,
    tax_year INTEGER NOT NULL CHECK (tax_year BETWEEN 1900 AND 2200),
    annual_amount NUMERIC(12, 2) NOT NULL CHECK (annual_amount >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_type, tax_year),
    CONSTRAINT retirement_limits_by_year_account_type_check
        CHECK (account_type IN ('TFSA', 'RRSP'))
);
