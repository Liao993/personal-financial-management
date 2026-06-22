from pydantic import BaseModel, validator  # type: ignore
from typing import Optional
from utils.data import account_name_list

ETF_CATEGORY_OPTIONS = ["Global", "US", "Europe", "Asia", "Bond", "Dividend", "Industry"]
STOCK_CATEGORY_OPTIONS = ["Tech", "Finance", "Consumer", "Healthcare", "Energy", "Dividend"]
PURPOSE_OPTIONS = ["Growth", "Dividend", "Bond"]


class Holding(BaseModel):
    ticker: str
    asset_type: str
    account_name: str
    units: float
    currency: str
    etf_category: Optional[str] = None
    stock_category: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True

    @validator("ticker")
    def ticker_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("Ticker should not be empty")
        return value.strip().upper()

    @validator("asset_type")
    def asset_type_valid(cls, value):
        if value not in ("ETF", "Stock"):
            raise ValueError("Asset type must be 'ETF' or 'Stock'")
        return value

    @validator("account_name")
    def account_name_valid(cls, value):
        if not value.strip():
            raise ValueError("Account name should not be empty")
        if value not in account_name_list:
            raise ValueError(f"Account must be one of: {account_name_list}")
        return value

    @validator("units")
    def units_positive(cls, value):
        if value is None or value <= 0:
            raise ValueError("Units must be greater than 0")
        return value

    @validator("currency")
    def currency_valid(cls, value):
        if value not in ("CAD", "USD"):
            raise ValueError("Currency must be 'CAD' or 'USD'")
        return value

    # ETF Category is required for ETF rows, must be empty for Stock rows.
    # NOTE: when purpose='Dividend', the UI form auto-syncs this field to
    # 'Dividend' too (see holding_form.py) — but that sync happens before
    # this model ever sees the data, so this validator just checks the
    # final value is consistent, it doesn't perform the sync itself.
    @validator("etf_category", always=True)
    def etf_category_check(cls, value, values):
        asset_type = values.get("asset_type")
        if asset_type == "ETF":
            if not value:
                raise ValueError("ETF Category is required when Asset Type is 'ETF'")
            if value not in ETF_CATEGORY_OPTIONS:
                raise ValueError(f"ETF Category must be one of: {ETF_CATEGORY_OPTIONS}")
        if asset_type == "Stock" and value:
            raise ValueError("ETF Category must be empty when Asset Type is 'Stock'")
        return value

    @validator("stock_category", always=True)
    def stock_category_check(cls, value, values):
        asset_type = values.get("asset_type")
        if asset_type == "Stock":
            if not value:
                raise ValueError("Stock Industry is required when Asset Type is 'Stock'")
            if value not in STOCK_CATEGORY_OPTIONS:
                raise ValueError(f"Stock Industry must be one of: {STOCK_CATEGORY_OPTIONS}")
        if asset_type == "ETF" and value:
            raise ValueError("Stock Industry must be empty when Asset Type is 'ETF'")
        return value

    # Purpose is now REQUIRED for BOTH ETF and Stock (v3 change).
    @validator("purpose", always=True)
    def purpose_check(cls, value, values):
        asset_type = values.get("asset_type")
        if asset_type in ("ETF", "Stock") and not value:
            raise ValueError(f"Purpose is required for {asset_type} holdings")
        if value is not None and value not in PURPOSE_OPTIONS:
            raise ValueError(f"Purpose must be one of: {PURPOSE_OPTIONS}")
        return value

    @validator("notes", pre=True)
    def empty_string_to_none(cls, value):
        return value if value and value.strip() else None
