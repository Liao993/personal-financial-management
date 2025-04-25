
from pydantic import BaseModel, validator # type: ignore
from datetime import date
from utils.data import expense_category_options
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
        if not value.strip():  # Check for whitespace as well
            raise ValueError('Items should not be empty')
        return value

    @validator('amount')
    def amount_not_empty(cls, value):
        if value is None:
            raise ValueError('Amount should not be empty')
        if isinstance(value, (int, float)):
            value = float(f"{value:.2f}")  # Ensure 2 decimal places
            return value
        return value

   

    @validator('category')
    def category_not_empty(cls, value):
        if not value.strip():  # Check for whitespace as well
            raise ValueError('Category should not be empty')
        if value not in expense_category_options:
            raise ValueError(f"Transaction type must be one of: {expense_category_options}")
        return value