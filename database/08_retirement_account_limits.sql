-- Persist the TFSA and RRSP total contribution limits in the database so
-- they can be maintained from the application instead of environment files.

CREATE TABLE IF NOT EXISTS retirement_account_limits (
    account_type VARCHAR(10) PRIMARY KEY,
    total_limit NUMERIC(12, 2) NOT NULL CHECK (total_limit >= 0),
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
END $$;

-- Keep existing installations usable until the limits are entered in the UI.
INSERT INTO retirement_account_limits (account_type, total_limit)
VALUES ('TFSA', 0), ('RRSP', 0)
ON CONFLICT (account_type) DO NOTHING;
