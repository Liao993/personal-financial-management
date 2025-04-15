
from pydantic import BaseModel, validator # type: ignore
from datetime import date

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
        return value

    @validator('category')
    def category_not_empty(cls, value):
        if not value.strip():  # Check for whitespace as well
            raise ValueError('Category should not be empty')
        return value