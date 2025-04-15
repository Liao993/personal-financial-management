from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional
from utils.data import transaction_type_database, account_name_list, usable_fund_categories
class Transaction(BaseModel):
    date: datetime
    account_name: str
    transaction_type: str
    amount: float
    fund_category: str
    source_notes: Optional[str] = None
    transfer_to_account: Optional[str] = None
    transfer_to_fund_category: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('date')
    def date_not_empty(cls, value):
        if not value:
            raise ValueError('Date should not be empty')
        return value

    @validator('account_name')
    def account_name_not_empty(cls, value):
        if not value.strip():
            raise ValueError('Account name should not be empty')
        if value not in account_name_list:
            raise ValueError(f'Account must be one of: {account_name_list}')
        return value
    
    @validator('fund_category')
    def fund_category_not_empty(cls, value):
        if not value.strip():
            raise ValueError('Fund category should not be empty')
        if value not in usable_fund_categories:
            raise ValueError(f"Fund category must be one of: {usable_fund_categories}")
        return value

    @validator('transaction_type')
    def transaction_type_not_empty(cls, value):
        if not value.strip():
            raise ValueError('Transaction type should not be empty')
        if value not in transaction_type_database:
            raise ValueError(f"Transaction type must be one of: {transaction_type_database}")
        return value

    @validator('amount')
    def amount_not_empty(cls, value):
        if value is None:
            raise ValueError('Amount should not be empty')
        return value

    @validator('amount')
    def amount_is_numeric(cls, value):
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError('Amount must be a valid number')
        return value

    @validator('transfer_to_account', pre=True)
    def empty_string_to_none_transfer_account(cls, value):
        return value if value and value.strip() else None

    @validator('transfer_to_fund_category', pre=True)
    def empty_string_to_none_transfer_fund_category(cls, value):
        return value if value and value.strip() else None

    @validator('source_notes', pre=True)
    def empty_string_to_none_source_notes(cls, value):
        return value if value and value.strip() else None