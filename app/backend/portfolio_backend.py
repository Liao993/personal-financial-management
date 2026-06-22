import streamlit as st  # type: ignore
from utils.connection import get_db_connection  # type: ignore
import psycopg2  # type: ignore
import pandas as pd  # type: ignore

# Reserved "ticker" used to store the latest USD->CAD FX rate inside the
# same etf_prices table that holds security prices. This avoids a schema
# migration — etf_prices already allows any VARCHAR(20) ticker and only
# requires (ticker, price_date) to be unique, and the live-fetch button
# already only writes ticker/price_date/close.
FX_TICKER = "USDCAD=X"


def insert_holding(data: dict) -> bool:
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot insert data.")
        return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO portfolio_holdings (
                ticker, asset_type, account_name, units,
                currency, etf_category, stock_category, purpose, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data["ticker"],
            data["asset_type"],
            data["account_name"],
            data["units"],
            data["currency"],
            data.get("etf_category"),
            data.get("stock_category"),
            data.get("purpose"),
            data.get("notes"),
        )
        cursor.execute(query, values)
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error inserting holding: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def _table_exists(cursor, table_name: str) -> bool:
    cursor.execute("SELECT to_regclass(%s)", (f"public.{table_name}",))
    return cursor.fetchone()[0] is not None


def _get_latest_usd_cad_rate(cursor):
    """
    Reads the most recently fetched USD->CAD rate from etf_prices, where
    it's stored under the reserved ticker FX_TICKER. Returns None if
    etf_prices doesn't exist yet, or no rate has been fetched yet.
    """
    if not _table_exists(cursor, "etf_prices"):
        return None
    cursor.execute(
        """
        SELECT close FROM etf_prices
        WHERE ticker = %s
        ORDER BY price_date DESC
        LIMIT 1
        """,
        (FX_TICKER,),
    )
    row = cursor.fetchone()
    return float(row[0]) if row and row[0] is not None else None


def fetch_usd_cad_rate():
    """
    Public helper so the UI (banners, captions) can show the FX rate
    currently being used for CAD-equivalent calculations, without pulling
    the whole holdings DataFrame.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        return _get_latest_usd_cad_rate(cursor)
    except psycopg2.Error:
        return None
    finally:
        cursor.close()
        conn.close()


def fetch_all_holdings(account_filter: str = None) -> pd.DataFrame:
    """
    Fetches all holdings joined to the latest known price for each ticker,
    plus a market_value_cad column normalized to CAD so percentages and
    totals are comparable across USD and CAD holdings.

    No cost basis / gain-loss is computed — holdings are bought in batches
    without a tracked purchase price, so this returns live market value only.

    Defensive: checks etf_prices exists before joining to it. If it doesn't
    exist yet, current_price, market_value, and market_value_cad come back
    as NULL rather than raising "relation does not exist".
    """
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot retrieve data.")
        return pd.DataFrame()
    try:
        cursor = conn.cursor()

        if _table_exists(cursor, "etf_prices"):
            base_query = """
                WITH latest_price AS (
                    SELECT DISTINCT ON (ticker)
                        ticker, close AS latest_close, price_date
                    FROM etf_prices
                    WHERE ticker != %s
                    ORDER BY ticker, price_date DESC
                )
                SELECT
                    h.id,
                    h.ticker,
                    h.asset_type,
                    h.account_name,
                    h.units,
                    h.currency,
                    h.etf_category,
                    h.stock_category,
                    h.purpose,
                    h.notes,
                    lp.latest_close AS current_price,
                    lp.price_date,
                    (h.units * lp.latest_close) AS market_value
                FROM portfolio_holdings h
                LEFT JOIN latest_price lp ON lp.ticker = h.ticker
            """
            params = [FX_TICKER]
        else:
            # etf_prices doesn't exist yet — return holdings with NULL
            # price/value instead of crashing.
            base_query = """
                SELECT
                    h.id,
                    h.ticker,
                    h.asset_type,
                    h.account_name,
                    h.units,
                    h.currency,
                    h.etf_category,
                    h.stock_category,
                    h.purpose,
                    h.notes,
                    NULL::NUMERIC AS current_price,
                    NULL::DATE AS price_date,
                    NULL::NUMERIC AS market_value
                FROM portfolio_holdings h
            """
            params = []

        if account_filter:
            base_query += " WHERE h.account_name ILIKE %s"
            params.append(f"%{account_filter}%")
        base_query += " ORDER BY h.account_name, h.ticker"

        cursor.execute(base_query, params)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=cols)

        # Ensure numeric columns are floats (psycopg2 returns Decimal for NUMERIC)
        for col in ("units", "current_price", "market_value"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # --- CAD-normalized market value, used by every chart's % math ---
        usd_cad_rate = _get_latest_usd_cad_rate(cursor)
        if not df.empty:
            def _to_cad(row):
                if pd.isna(row["market_value"]):
                    return None
                if row["currency"] == "CAD":
                    return row["market_value"]
                if row["currency"] == "USD" and usd_cad_rate:
                    return row["market_value"] * usd_cad_rate
                return None  # USD holding but no FX rate fetched yet

            df["market_value_cad"] = df.apply(_to_cad, axis=1)
        else:
            df["market_value_cad"] = pd.Series(dtype="float64")

        return df
    except psycopg2.Error as e:
        st.error(f"Error retrieving holdings: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()


def fetch_holding_by_id(holding_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot retrieve data.")
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM portfolio_holdings WHERE id = %s",
            (holding_id,),
        )
        row = cursor.fetchone()
        if not row:
            return {}
        cols = [desc[0] for desc in cursor.description]
        return dict(zip(cols, row))
    except psycopg2.Error as e:
        st.error(f"Error retrieving holding: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def update_holding(holding_id: int, data: dict) -> bool:
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot update data.")
        return False
    try:
        cursor = conn.cursor()
        query = """
            UPDATE portfolio_holdings
            SET ticker = %s,
                asset_type = %s,
                account_name = %s,
                units = %s,
                currency = %s,
                etf_category = %s,
                stock_category = %s,
                purpose = %s,
                notes = %s
            WHERE id = %s
        """
        values = (
            data["ticker"],
            data["asset_type"],
            data["account_name"],
            data["units"],
            data["currency"],
            data.get("etf_category"),
            data.get("stock_category"),
            data.get("purpose"),
            data.get("notes"),
            holding_id,
        )
        cursor.execute(query, values)
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error updating holding: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_holding(holding_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        st.info("Database connection failed, cannot delete data.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM portfolio_holdings WHERE id = %s",
            (holding_id,),
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error deleting holding: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def fetch_last_price_update():
    """
    Returns the most recent price_date across all SECURITY tickers in
    etf_prices (excludes the reserved FX_TICKER row), formatted as a
    string. Returns None if etf_prices doesn't exist yet or has no
    security rows.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        if not _table_exists(cursor, "etf_prices"):
            return None

        cursor.execute(
            "SELECT MAX(price_date) FROM etf_prices WHERE ticker != %s",
            (FX_TICKER,),
        )
        result = cursor.fetchone()
        if result and result[0]:
            return str(result[0])
        return None
    except psycopg2.Error:
        return None
    finally:
        cursor.close()
        conn.close()

def fetch_total_deposit(tab_key: str = None) -> float:
    """
    Sums the 'amount' column directly from the transactions table for
    investment-type accounts. Mirrors the column total Page 10's
    Pivot_Table shows for those same accounts.

    tab_key maps to an account name keyword:
      "tfsa"       -> accounts containing 'TFSA'
      "rrsp"       -> accounts containing 'RRSP'
      "retirement" -> accounts containing 'Retire'
      None (or any other value, e.g. "total") -> combined TFSA + RRSP + Retire
    """
    keyword_map = {
        "tfsa": "TFSA",
        "rrsp": "RRSP",
        "retirement": "Retire",
    }

    conn = get_db_connection()
    if not conn:
        return 0.0
    try:
        cursor = conn.cursor()
        if tab_key in keyword_map:
            query = "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE account_name ILIKE %s"
            params = [f"%{keyword_map[tab_key]}%"]
        else:
            query = """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE account_name ILIKE %s
                   OR account_name ILIKE %s
                   OR account_name ILIKE %s
            """
            params = ["%TFSA%", "%RRSP%", "%Retire%"]
        cursor.execute(query, params)
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] is not None else 0.0
    except psycopg2.Error as e:
        st.error(f"Error retrieving total deposit: {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()