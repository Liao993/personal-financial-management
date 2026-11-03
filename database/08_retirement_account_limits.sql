-- Persist the TFSA and RRSP total contribution limits in the database so
-- they can be maintained from the application instead of environment files.

CREATE TABLE IF NOT EXISTS retirement_account_limits (
    account_type VARCHAR(10) PRIMARY KEY,
    total_limit NUMERIC(12, 2) NOT NULL CHECK (total_limit >= 0),
    -- Deprecated compatibility field for containers running the pre-rename
    -- application during a rolling deployment. Current code never uses it.
    annual_limit NUMERIC(12, 2),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT retirement_account_limits_account_type_check
        CHECK (account_type IN ('TFSA', 'RRSP'))
);

-- Rename the original field for databases that received the first version of
-- this migration before the terminology was clarified.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'retirement_account_limits'
          AND column_name = 'annual_limit'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'retirement_account_limits'
          AND column_name = 'total_limit'
    ) THEN
        ALTER TABLE retirement_account_limits
            RENAME COLUMN annual_limit TO total_limit;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'retirement_account_limits'
          AND column_name = 'annual_limit'
    ) THEN
        ALTER TABLE retirement_account_limits
            ADD COLUMN annual_limit NUMERIC(12, 2);
    END IF;
END $$;

UPDATE retirement_account_limits
SET annual_limit = total_limit
WHERE annual_limit IS NULL;

CREATE OR REPLACE FUNCTION sync_retirement_account_limit_compatibility()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.annual_limit := NEW.total_limit;
    ELSIF NEW.total_limit IS DISTINCT FROM OLD.total_limit THEN
        NEW.annual_limit := NEW.total_limit;
    ELSIF NEW.annual_limit IS DISTINCT FROM OLD.annual_limit THEN
        NEW.total_limit := NEW.annual_limit;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS retirement_account_limits_compatibility_trigger
    ON retirement_account_limits;
CREATE TRIGGER retirement_account_limits_compatibility_trigger
BEFORE INSERT OR UPDATE ON retirement_account_limits
FOR EACH ROW
EXECUTE FUNCTION sync_retirement_account_limit_compatibility();

-- Keep existing installations usable until the limits are entered in the UI.
INSERT INTO retirement_account_limits (account_type, total_limit, annual_limit)
VALUES ('TFSA', 0, 0), ('RRSP', 0, 0)
ON CONFLICT (account_type) DO NOTHING;
