-- 05_expense_ingestion_dedupe.sql
-- Align duplicate protection with statement ingestion:
-- date + payment_method + normalized item + amount + source_notes.

ALTER TABLE expense
    DROP CONSTRAINT IF EXISTS unique_expense_entry;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'expense'
          AND indexname = 'unique_expense_ingestion_entry'
    ) THEN
        BEGIN
            CREATE UNIQUE INDEX unique_expense_ingestion_entry
            ON expense (
                date,
                COALESCE(payment_method, ''),
                lower(trim(items)),
                amount,
                COALESCE(trim(source_notes), '')
            );
        EXCEPTION
            WHEN unique_violation THEN
                RAISE NOTICE
                    'Skipped unique_expense_ingestion_entry because existing duplicate expense rows must be cleaned first.';
        END;
    END IF;
END $$;
