-- Revision: Universal Fund Distribution & Automated Expense Allocation (V4)
-- Description: Completely removes rigid travel logic. Implements explicit multi-fund allocations, 
--              unlinks category tracking from fund logic, and handles automated prepaid and exclusion overrides.
-- =========================================================================
-- STEP 1: SCHEMA EXTENSIONS
-- =========================================================================
-- 1.1 Extend the Transactions Table
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS expense_id INTEGER REFERENCES expense(id) ON DELETE CASCADE;
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS trip VARCHAR(255);
-- 1.2 Extend the Expense Table for Flexible Allocation & Budget Interception
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS exclude_from_monthly BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS is_prepaid BOOLEAN NOT NULL DEFAULT FALSE;
-- The primary savings pool you want to target (e.g., 'Emergency Funds', 'Traveling', 'Retirement')
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS target_fund_category VARCHAR(255);
-- Explicit split allocations for distributing parts of the bill to other dedicated savings funds
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS split_fund_category_1 VARCHAR(255);
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS split_amount_1 NUMERIC(10, 2) NOT NULL DEFAULT 0.00;
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS split_fund_category_2 VARCHAR(255);
ALTER TABLE expense
ADD COLUMN IF NOT EXISTS split_amount_2 NUMERIC(10, 2) NOT NULL DEFAULT 0.00;
-- =========================================================================
-- STEP 2: BEFORE INSERT TRIGGER (NORMALIZE SPLIT AMOUNTS)
-- =========================================================================
-- Only ensures split numeric fields default to 0 if left null.
-- exclude_from_monthly is set by the user explicitly (validated in the application layer:
-- if exclude_from_monthly=TRUE then target_fund_category must be provided).
CREATE OR REPLACE FUNCTION set_expense_defaults() RETURNS TRIGGER AS $$
BEGIN
    NEW.split_amount_1 := COALESCE(NEW.split_amount_1, 0.00);
    NEW.split_amount_2 := COALESCE(NEW.split_amount_2, 0.00);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trigger_set_expense_defaults ON expense;
CREATE TRIGGER trigger_set_expense_defaults BEFORE
INSERT ON expense FOR EACH ROW EXECUTE FUNCTION set_expense_defaults();
-- =========================================================================
-- STEP 3: AFTER INSERT TRIGGER (AUTO WITHDRAWAL TRANSACTION CREATION)
-- =========================================================================
-- Creates withdrawal transactions when exclude_from_monthly = TRUE.
-- By the time data reaches here, the app has already validated that
-- target_fund_category IS NOT NULL whenever exclude_from_monthly = TRUE.
-- is_prepaid passes through to the transaction row so it can be filtered separately.
CREATE OR REPLACE FUNCTION automate_expense_transactions() RETURNS TRIGGER AS $$
DECLARE
    v_my_share     NUMERIC(10, 2);
    v_total_splits NUMERIC(10, 2);
    v_account      VARCHAR(255);
BEGIN
    -- RBC Chequing is always the fund source account; payment_method is just the credit card used.
    v_account := 'RBC Chequing';

    -- Only create transactions when the user explicitly marked this as a fund withdrawal.
    IF NEW.exclude_from_monthly = TRUE THEN
        v_total_splits := COALESCE(NEW.split_amount_1, 0.00) + COALESCE(NEW.split_amount_2, 0.00);
        v_my_share := NEW.amount - v_total_splits;

        -- 1. Primary fund withdrawal (amount minus any splits)
        IF v_my_share > 0 THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, prepaid, expense_id, trip
            ) VALUES (
                NEW.date, v_account, 'Withdrawal', -v_my_share,
                NEW.target_fund_category, NEW.source_notes, NEW.is_prepaid, NEW.id, NEW.trip
            );
        END IF;

        -- 2. Secondary fund split
        IF COALESCE(NEW.split_amount_1, 0.00) > 0 AND NEW.split_fund_category_1 IS NOT NULL THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, prepaid, expense_id, trip
            ) VALUES (
                NEW.date, v_account, 'Withdrawal', -NEW.split_amount_1,
                NEW.split_fund_category_1, NEW.source_notes, NEW.is_prepaid, NEW.id, NEW.trip
            );
        END IF;

        -- 3. Tertiary fund split
        IF COALESCE(NEW.split_amount_2, 0.00) > 0 AND NEW.split_fund_category_2 IS NOT NULL THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, prepaid, expense_id, trip
            ) VALUES (
                NEW.date, v_account, 'Withdrawal', -NEW.split_amount_2,
                NEW.split_fund_category_2, NEW.source_notes, NEW.is_prepaid, NEW.id, NEW.trip
            );
        END IF;

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trigger_automate_expense_transactions ON expense;
CREATE TRIGGER trigger_automate_expense_transactions
AFTER INSERT ON expense FOR EACH ROW EXECUTE FUNCTION automate_expense_transactions();