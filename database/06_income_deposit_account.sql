-- =========================================================================
-- 06_income_deposit_account.sql
-- Description:
--   1. Add deposit_account column to income table
--   2. Backfill existing income rows with the default chequing account
--   3. Add income_id foreign key to transactions table so that non-chequing
--      income deposits can be linked to the originating income record
--      (mirrors the expense_id pattern used for expense-linked withdrawals)
--   4. Add injection_source column to expense table to track how each
--      expense was entered: 'manual_input' or the statement filename
--
-- Prerequisites: 01_init_schema.sql and 03_expense_transaction_sync.sql
-- =========================================================================


-- =========================================================================
-- STEP 1: ADD deposit_account TO income TABLE
-- =========================================================================

ALTER TABLE income
    ADD COLUMN IF NOT EXISTS deposit_account VARCHAR(255);

-- Backfill historical income rows using the chequing account already present
-- in transactions. Dev uses Main Chequing; production uses RBC Chequing.
-- Fresh databases have no historical income rows, so the fallback is only
-- used when a database has no recognizable chequing account yet.
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


-- =========================================================================
-- STEP 2: ADD income_id FK TO transactions TABLE
-- =========================================================================
-- Allows a Deposit transaction to be linked back to the income row that
-- created it (only set for non-chequing income deposits).
-- ON DELETE CASCADE: if an income row is deleted, any linked deposit
-- transaction is automatically removed as well.

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS income_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_attribute a
          ON a.attrelid = c.conrelid
         AND a.attnum = ANY(c.conkey)
        WHERE c.conrelid  = 'transactions'::regclass
          AND c.confrelid = 'income'::regclass
          AND c.contype   = 'f'
          AND a.attname   = 'income_id'
    ) THEN
        ALTER TABLE transactions
            ADD CONSTRAINT transactions_income_id_fkey
            FOREIGN KEY (income_id)
            REFERENCES income(id)
            ON DELETE CASCADE;
    END IF;
END;
$$;


-- =========================================================================
-- STEP 3: ADD injection_source TO expense TABLE
-- =========================================================================
-- Tracks how each expense row entered the system:
--   'manual_input'           — entered via Page 3 Manual Expense Input
--   '<statement_filename>'   — ingested via Page 4 Upload Expense (PDF name)
--
-- Existing rows are left NULL; future rows will always have this set.

ALTER TABLE expense
    ADD COLUMN IF NOT EXISTS injection_source VARCHAR(255);
