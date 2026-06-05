-- =========================================================================
-- 03_expense_transaction_sync.sql
-- Revision: Universal Fund Distribution & Expense-Transaction Sync (V6)
-- Description:
--   1. Extend transactions table with expense_id (foreign key) and trip
--   2. Extend expense table with fund allocation columns
--   3. BEFORE INSERT trigger — normalize split amounts
--   4. AFTER INSERT trigger — auto-create withdrawal transactions when
--      exclude_from_monthly = TRUE
--   5. AFTER UPDATE trigger — sync linked transaction amounts when expense
--      amount or source_notes changes, using secondary-first absorption:
--        - Amount increases  → primary fund absorbs all extra
--        - Amount decreases  → remove from secondary first, then primary
--   6. DELETE is handled automatically via ON DELETE CASCADE on expense_id
--
-- Prerequisites: 01_init_schema.sql must have been run first.
-- No prepaid columns — that concept is removed entirely.
-- =========================================================================


-- =========================================================================
-- STEP 1: EXTEND TRANSACTIONS TABLE
-- =========================================================================

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS expense_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_attribute a
          ON a.attrelid = c.conrelid
         AND a.attnum = ANY(c.conkey)
        WHERE c.conrelid = 'transactions'::regclass
          AND c.confrelid = 'expense'::regclass
          AND c.contype = 'f'
          AND a.attname = 'expense_id'
    ) THEN
        ALTER TABLE transactions
            ADD CONSTRAINT transactions_expense_id_fkey
            FOREIGN KEY (expense_id)
            REFERENCES expense(id)
            ON DELETE CASCADE;
    END IF;
END;
$$;

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS trip VARCHAR(255);


-- =========================================================================
-- STEP 2: EXTEND EXPENSE TABLE
-- =========================================================================

-- Controls whether this expense is excluded from monthly spending totals
-- and whether a fund withdrawal transaction should be auto-created.
ALTER TABLE expense
    ADD COLUMN IF NOT EXISTS exclude_from_monthly BOOLEAN NOT NULL DEFAULT FALSE;

-- Primary fund to deduct from (required when exclude_from_monthly = TRUE)
ALTER TABLE expense
    ADD COLUMN IF NOT EXISTS target_fund_category VARCHAR(255);

-- Optional split allocation — secondary fund bucket
ALTER TABLE expense
    ADD COLUMN IF NOT EXISTS split_fund_category_1 VARCHAR(255);

ALTER TABLE expense
    ADD COLUMN IF NOT EXISTS split_amount_1 NUMERIC(10, 2) NOT NULL DEFAULT 0.00;


-- =========================================================================
-- STEP 3: BEFORE INSERT TRIGGER — normalize split amounts
-- =========================================================================
-- Ensures split_amount fields are never NULL in the database,
-- even if the application passes NULL.

CREATE OR REPLACE FUNCTION set_expense_defaults()
RETURNS TRIGGER AS $$
BEGIN
    NEW.split_amount_1 := COALESCE(NEW.split_amount_1, 0.00);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_set_expense_defaults ON expense;
CREATE TRIGGER trigger_set_expense_defaults
BEFORE INSERT ON expense
FOR EACH ROW EXECUTE FUNCTION set_expense_defaults();


-- =========================================================================
-- STEP 4: AFTER INSERT TRIGGER — auto-create fund withdrawal transactions
-- =========================================================================
-- Fires when a new expense row is inserted.
-- Only acts when exclude_from_monthly = TRUE.
-- Creates up to 2 withdrawal rows: primary and secondary split.
-- The account is always RBC Chequing — payment_method is just the card used.
-- The application layer validates that target_fund_category IS NOT NULL
-- whenever exclude_from_monthly = TRUE before data reaches here.

CREATE OR REPLACE FUNCTION automate_expense_transactions()
RETURNS TRIGGER AS $$
DECLARE
    v_my_share     NUMERIC(10, 2);
    v_secondary    NUMERIC(10, 2);
    v_account      VARCHAR(255);
BEGIN
    v_account := 'RBC Chequing';

    IF NEW.exclude_from_monthly = TRUE THEN
        v_secondary := CASE
            WHEN NEW.split_fund_category_1 IS NOT NULL
                THEN LEAST(COALESCE(NEW.split_amount_1, 0.00), NEW.amount)
            ELSE 0.00
        END;
        v_my_share := NEW.amount - v_secondary;

        -- Primary fund withdrawal (total minus splits)
        IF v_my_share > 0 THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, expense_id, trip
            ) VALUES (
                NEW.date, v_account, 'Withdrawal', -v_my_share,
                NEW.target_fund_category, NEW.source_notes, NEW.id, NEW.trip
            );
        END IF;

        -- Secondary fund split
        IF v_secondary > 0
           AND NEW.split_fund_category_1 IS NOT NULL THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, expense_id, trip
            ) VALUES (
                NEW.date, v_account, 'Withdrawal', -v_secondary,
                NEW.split_fund_category_1, NEW.source_notes, NEW.id, NEW.trip
            );
        END IF;

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_automate_expense_transactions ON expense;
CREATE TRIGGER trigger_automate_expense_transactions
AFTER INSERT ON expense
FOR EACH ROW EXECUTE FUNCTION automate_expense_transactions();


-- =========================================================================
-- STEP 5: AFTER UPDATE TRIGGER — sync transactions when expense changes
-- =========================================================================
-- Fires when expense.amount or expense.source_notes is updated.
-- Recalculates linked transaction amounts using absorption logic:
--
--   Example: existing transactions are primary=$500, secondary=$300
--   New amount=$600 (reduce $200):
--     secondary: $300 → $100
--     primary stays $500
--   New amount=$400 (reduce $400):
--     secondary: $300 → $0
--     primary: $500 → $400
--   Amount increases add the increase to primary.
--
-- source_notes on linked transactions is replaced with the
-- current expense source_notes (useful for noting "refund applied" etc.)

CREATE OR REPLACE FUNCTION sync_expense_transactions()
RETURNS TRIGGER AS $$
DECLARE
    v_current_primary   NUMERIC(10, 2);
    v_current_secondary NUMERIC(10, 2);
    v_delta             NUMERIC(10, 2);
    v_reduction         NUMERIC(10, 2);
    v_new_primary       NUMERIC(10, 2);
    v_new_secondary     NUMERIC(10, 2);
BEGIN
    -- Only sync expenses that have linked transactions
    IF NEW.exclude_from_monthly IS DISTINCT FROM TRUE THEN
        RETURN NEW;
    END IF;

    -- Only act if amount or source_notes actually changed
    IF NEW.amount IS NOT DISTINCT FROM OLD.amount
       AND NEW.source_notes IS NOT DISTINCT FROM OLD.source_notes THEN
        RETURN NEW;
    END IF;

    SELECT COALESCE(SUM(ABS(amount)), 0.00)
    INTO v_current_primary
    FROM transactions
    WHERE expense_id = NEW.id
      AND fund_category = NEW.target_fund_category;

    SELECT COALESCE(SUM(ABS(amount)), 0.00)
    INTO v_current_secondary
    FROM transactions
    WHERE expense_id = NEW.id
      AND fund_category = NEW.split_fund_category_1;

    v_delta := NEW.amount - OLD.amount;
    v_new_primary := v_current_primary;
    v_new_secondary := v_current_secondary;

    IF v_delta >= 0 THEN
        v_new_primary := v_current_primary + v_delta;
    ELSE
        v_reduction := ABS(v_delta);
        v_new_secondary := GREATEST(v_current_secondary - v_reduction, 0.00);
        v_reduction := GREATEST(v_reduction - v_current_secondary, 0.00);
        v_new_primary := GREATEST(v_current_primary - v_reduction, 0.00);
    END IF;

    -- Update primary transaction row
    UPDATE transactions
    SET
        amount       = -v_new_primary,
        source_notes = NEW.source_notes
    WHERE
        expense_id    = NEW.id
        AND fund_category = NEW.target_fund_category;

    -- Update secondary split transaction row
    IF NEW.split_fund_category_1 IS NOT NULL THEN
        UPDATE transactions
        SET
            amount       = -v_new_secondary,
            source_notes = NEW.source_notes
        WHERE
            expense_id    = NEW.id
            AND fund_category = NEW.split_fund_category_1;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_sync_expense_transactions ON expense;
CREATE TRIGGER trigger_sync_expense_transactions
AFTER UPDATE OF amount, source_notes ON expense
FOR EACH ROW EXECUTE FUNCTION sync_expense_transactions();
