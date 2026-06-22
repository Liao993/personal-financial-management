-- =============================================================================
-- 04_portfolio_schema.sql — Portfolio Holdings (Page 14)
-- Safe to re-run: every statement uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS.
-- Does NOT touch expense, income, or transactions tables.
--
-- v3 changes (this session):
--   - Purpose (Growth/Dividend/Bond) is now REQUIRED for ETF holdings too,
--     not just Stock. ETF Category (Global/US/etc) and Purpose are two
--     independent fields — both required for ETF rows.
--   - Added 'Bond' as a 3rd purpose option (alongside Growth, Dividend).
--   - TEST DATA WIPE: existing rows were saved before purpose was required
--     on ETFs, so this migration truncates portfolio_holdings. Confirmed
--     with user — test data only, safe to discard.
--
-- v2 changes (previous session):
--   - Removed purchase_price (user buys in batches, no per-lot cost tracked)
--   - Added 'Industry' as a 7th etf_category option (leveraged/thematic ETFs
--     like TSLL, SOXL that aren't region-based)
--   - Added a minimal etf_prices table so Page 14 never errors before
--     Page 15's full pipeline is built
-- =============================================================================

-- -----------------------------------------------------------------------
-- portfolio_holdings
-- One row per holding lot you own. Units only — current value is computed
-- live from etf_prices at query time, not stored here.
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id              SERIAL PRIMARY KEY,
    ticker          VARCHAR(20)     NOT NULL,
    asset_type      VARCHAR(10)     NOT NULL,
    account_name    VARCHAR(255)    NOT NULL,
    units           NUMERIC(14, 4)  NOT NULL,
    currency        VARCHAR(5)      NOT NULL,
    etf_category    VARCHAR(50),
    stock_category  VARCHAR(50),
    purpose         VARCHAR(20),
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_asset_type
        CHECK (asset_type IN ('ETF', 'Stock')),

    CONSTRAINT chk_currency
        CHECK (currency IN ('CAD', 'USD')),

    CONSTRAINT chk_units_positive
        CHECK (units > 0)
);

COMMENT ON TABLE portfolio_holdings IS
    'Fact table: one row per holding lot (units only, no cost basis). Joined to etf_prices (dimension) by ticker for live market value.';

-- -----------------------------------------------------------------------
-- TEST DATA WIPE (v3 migration)
-- Existing rows were saved before 'purpose' was required on ETF holdings.
-- Confirmed with user this is throwaway test data — safe to truncate.
-- If you have REAL data in here when re-running this file later, comment
-- out the next line first.
-- -----------------------------------------------------------------------
TRUNCATE TABLE portfolio_holdings RESTART IDENTITY;

-- -----------------------------------------------------------------------
-- Drop old constraints before re-adding updated versions (idempotent —
-- DROP IF EXISTS is a no-op if the constraint isn't there).
-- -----------------------------------------------------------------------
ALTER TABLE portfolio_holdings DROP CONSTRAINT IF EXISTS chk_purpose_values;
ALTER TABLE portfolio_holdings DROP CONSTRAINT IF EXISTS chk_etf_classification;
ALTER TABLE portfolio_holdings DROP CONSTRAINT IF EXISTS chk_etf_category_values;
ALTER TABLE portfolio_holdings DROP CONSTRAINT IF EXISTS chk_stock_category_values;
ALTER TABLE portfolio_holdings DROP COLUMN IF EXISTS purchase_price;

-- Purpose now has 3 options and applies to BOTH asset types.
ALTER TABLE portfolio_holdings ADD CONSTRAINT chk_purpose_values
    CHECK (purpose IS NULL OR purpose IN ('Growth', 'Dividend', 'Bond'));

-- Classification rule, updated:
--   ETF rows  -> etf_category required, purpose required, stock_category NULL
--   Stock rows -> stock_category required, purpose required, etf_category NULL
-- (Purpose is now required for BOTH asset types — this is the core v3 change.)
ALTER TABLE portfolio_holdings ADD CONSTRAINT chk_etf_classification
    CHECK (
        (asset_type = 'ETF'   AND etf_category IS NOT NULL AND purpose IS NOT NULL AND stock_category IS NULL)
        OR
        (asset_type = 'Stock' AND stock_category IS NOT NULL AND purpose IS NOT NULL AND etf_category IS NULL)
    );

ALTER TABLE portfolio_holdings ADD CONSTRAINT chk_etf_category_values
    CHECK (
        etf_category IS NULL
        OR etf_category IN ('Global', 'US', 'Europe', 'Asia', 'Bond', 'Dividend', 'Industry')
    );

ALTER TABLE portfolio_holdings ADD CONSTRAINT chk_stock_category_values
    CHECK (
        stock_category IS NULL
        OR stock_category IN ('Tech', 'Finance', 'Consumer', 'Healthcare', 'Energy', 'Dividend')
    );

-- -----------------------------------------------------------------------
-- portfolio_ticker_meta
-- Display name + currency per ticker. Auto-populated by the Page 15
-- signal pipeline the first time it fetches a new ticker. Optional lookup
-- table — portfolio_backend.py works fine even if a ticker has no row here.
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio_ticker_meta (
    ticker          VARCHAR(20) PRIMARY KEY,
    display_name    VARCHAR(100),
    currency        VARCHAR(5)
);

COMMENT ON TABLE portfolio_ticker_meta IS
    'Lookup table: human-readable name and native currency per ticker symbol.';

-- -----------------------------------------------------------------------
-- etf_prices — minimal placeholder so Page 14 never errors before Page 15
-- (the signal pipeline) is built.
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS etf_prices (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR(20)     NOT NULL,
    price_date  DATE            NOT NULL,
    open        NUMERIC(14, 4),
    high        NUMERIC(14, 4),
    low         NUMERIC(14, 4),
    close       NUMERIC(14, 4)  NOT NULL,
    volume      BIGINT,
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etf_prices_ticker_date UNIQUE (ticker, price_date)
);

COMMENT ON TABLE etf_prices IS
    'Dimension table: daily close price per ticker. Populated by the Page 15 signal pipeline (or the manual Fetch Live Prices button on Page 14).';
