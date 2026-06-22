"""
live_price_fetch.py — manual on-demand price fetch for Page 14.

This is intentionally NOT the full Page 15 pipeline. It does one thing:
read every distinct ticker currently in portfolio_holdings, fetch today's
price from yfinance, and upsert it into etf_prices (latest price only,
no history). It also fetches the live USD->CAD exchange rate in the same
click, storing it under the reserved ticker FX_TICKER in the same table —
so every chart's CAD-equivalent totals stay current without a second
button or a separate FX table. Triggered by a button click, not scheduled.

When Page 15 is eventually built, this file can be deleted — its job
will be superseded by the full etf_pipeline package.
"""
import yfinance as yf  # type: ignore
import psycopg2  # type: ignore
from datetime import date
from utils.connection import get_db_connection  # type: ignore
from backend.portfolio_backend import FX_TICKER


def fetch_distinct_tickers() -> list:
    """Returns every unique ticker currently held, so we only fetch what's needed."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ticker FROM portfolio_holdings ORDER BY ticker")
        return [row[0] for row in cursor.fetchall()]
    except psycopg2.Error:
        return []
    finally:
        cursor.close()
        conn.close()


def fetch_live_price(ticker: str):
    """
    Fetches today's most recent close price for a single ticker (or FX
    pair, e.g. 'USDCAD=X') via yfinance. Returns float on success, None on
    failure (ticker delisted, network error, rate limit, etc). Never
    raises — callers should treat None as "skip this one".
    """
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None


def upsert_latest_price(ticker: str, price: float) -> bool:
    """
    Stores only the LATEST price per ticker (or FX pair). Each click
    overwrites today's row for that ticker via ON CONFLICT — no price
    history is kept, since this page only needs current market value,
    not a price chart.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO etf_prices (ticker, price_date, close)
            VALUES (%s, %s, %s)
            ON CONFLICT (ticker, price_date)
            DO UPDATE SET close = EXCLUDED.close
            """,
            (ticker, date.today(), price),
        )
        conn.commit()
        return True
    except psycopg2.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def run_manual_price_fetch() -> dict:
    """
    Orchestrates the whole button click: get tickers you own, fetch each
    one's live price, save it — then fetch the live USD->CAD FX rate too,
    so every chart's CAD-equivalent totals stay current. Returns a summary
    dict so the page can show a clear success/error message instead of
    guessing what happened.
    """
    tickers = fetch_distinct_tickers()

    result = {
        "total": len(tickers),
        "success": 0,
        "failed": [],
        "tickers_fetched": [],
        "fx_rate": None,
        "fx_fetched": False,
    }

    for ticker in tickers:
        price = fetch_live_price(ticker)
        if price is None:
            result["failed"].append(ticker)
            continue

        if upsert_latest_price(ticker, price):
            result["success"] += 1
            result["tickers_fetched"].append((ticker, price))
        else:
            result["failed"].append(ticker)

    # FX rate — fetched every click regardless of how many holdings exist,
    # since it's needed for CAD-equivalent totals across the whole dashboard.
    fx_rate = fetch_live_price(FX_TICKER)
    if fx_rate is not None and upsert_latest_price(FX_TICKER, fx_rate):
        result["fx_rate"] = fx_rate
        result["fx_fetched"] = True

    return result