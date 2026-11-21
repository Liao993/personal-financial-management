-- Store the selected fund category on excluded income so its linked
-- transaction can be kept synchronized when the income is edited.
ALTER TABLE income
    ADD COLUMN IF NOT EXISTS fund_category VARCHAR(255);

CREATE OR REPLACE FUNCTION sync_income_transaction()
RETURNS trigger AS $$
BEGIN
    IF NEW.exclude_from_monthly = TRUE THEN
        UPDATE transactions
        SET date = NEW.date,
            account_name = NEW.deposit_account,
            amount = NEW.amount,
            fund_category = NEW.fund_category,
            source_notes = 'income deposit – ' || NEW.source
        WHERE income_id = NEW.id;

        IF NOT FOUND THEN
            INSERT INTO transactions (
                date, account_name, transaction_type, amount,
                fund_category, source_notes, income_id
            )
            VALUES (
                NEW.date, NEW.deposit_account, 'Deposit', NEW.amount,
                NEW.fund_category, 'income deposit – ' || NEW.source, NEW.id
            );
        END IF;
    ELSE
        DELETE FROM transactions WHERE income_id = NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS income_transaction_sync_trigger ON income;
CREATE TRIGGER income_transaction_sync_trigger
AFTER INSERT OR UPDATE ON income
FOR EACH ROW
EXECUTE FUNCTION sync_income_transaction();
