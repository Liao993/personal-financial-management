
from pydantic import BaseModel, validator # type: ignore
from datetime import date
from decimal import Decimal
from utils.data import expense_category_options, traveling_category

class Expense(BaseModel):
    date: date
    items: str
    amount: float
    category: str

    class Config:
        orm_mode = True

    @validator('date')
    def date_not_empty(cls, value):
        if not value:
            raise ValueError('Date should not be empty')
        return value

    @validator('items')
    def items_not_empty(cls, value):
        if not value.strip():
            raise ValueError('Items should not be empty')
        return value

    @validator('amount')
    def amount_not_empty(cls, value):
        if value is None:
            raise ValueError('Amount should not be empty')
        if not isinstance(value, (int, float)):  # Allow int or float
            raise TypeError('Amount must be a number')
        return value

    @validator('category')
    def category_in_list(cls, value):
        if not value.strip():
            raise ValueError('Category should not be empty')
        if value not in expense_category_options:
            raise ValueError(f'Category must be one of {expense_category_options}')
        return value
    
    @validator('traveling_category')
    def traveling_category_in_list(cls, value):
        if value is not None and value not in traveling_category:
            raise ValueError(f'Traveling category must be one of {traveling_category}')
        return value
