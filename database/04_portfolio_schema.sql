-- =============================================================================
-- 04_portfolio_schema.sql - Portfolio Holdings (Page 14)
-- Production schema only.
--
-- This file is intended for a clean database initialization. It does not
-- truncate data, drop columns, or perform development migration cleanup.
-- =============================================================================

-- -----------------------------------------------------------------------
-- portfolio_holdings
-- One row per holding lot you own. Units only; current value is computed
-- from etf_prices at query time, not stored here.
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
    purpose         VARCHAR(20)     NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_asset_type
        CHECK (asset_type IN ('ETF', 'Stock')),

    CONSTRAINT chk_currency
        CHECK (currency IN ('CAD', 'USD')),

    CONSTRAINT chk_units_positive
        CHECK (units > 0),

    CONSTRAINT chk_purpose_values
        CHECK (purpose IN ('Growth', 'Dividend', 'Bond')),

    CONSTRAINT chk_etf_category_values
        CHECK (
            etf_category IS NULL
            OR etf_category IN ('Global', 'US', 'Europe', 'Asia', 'Bond', 'Dividend', 'Industry')
        ),

    CONSTRAINT chk_stock_category_values
        CHECK (
            stock_category IS NULL
            OR stock_category IN ('Tech', 'Finance', 'Consumer', 'Healthcare', 'Energy', 'Dividend')
        ),

    CONSTRAINT chk_portfolio_holding_classification
        CHECK (
            (asset_type = 'ETF' AND etf_category IS NOT NULL AND stock_category IS NULL)
            OR
            (asset_type = 'Stock' AND stock_category IS NOT NULL AND etf_category IS NULL)
        )
);

COMMENT ON TABLE portfolio_holdings IS
    'Fact table: one row per holding lot (units only, no cost basis). Joined to etf_prices by ticker for market value.';

-- -----------------------------------------------------------------------
-- portfolio_ticker_meta
-- Display name + native currency per ticker. Optional lookup table; the app
-- works even when a ticker has no row here.
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio_ticker_meta (
    ticker          VARCHAR(20) PRIMARY KEY,
    display_name    VARCHAR(100),
    currency        VARCHAR(5),

    CONSTRAINT chk_portfolio_ticker_meta_currency
        CHECK (currency IS NULL OR currency IN ('CAD', 'USD'))
);

COMMENT ON TABLE portfolio_ticker_meta IS
    'Lookup table: human-readable name and native currency per ticker symbol.';

-- -----------------------------------------------------------------------
-- etf_prices
-- Latest and historical daily close prices by ticker.
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

    CONSTRAINT uq_etf_prices_ticker_date
        UNIQUE (ticker, price_date)
);

COMMENT ON TABLE etf_prices IS
    'Dimension table: daily close price per ticker. Populated by live price fetches and the signal pipeline.';

CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_ticker
    ON portfolio_holdings (ticker);

CREATE INDEX IF NOT EXISTS idx_etf_prices_ticker_price_date
    ON etf_prices (ticker, price_date DESC);
