from pydantic import BaseModel, validator # type: ignore
from datetime import date
from typing import Optional

class Income(BaseModel):
    date: date
    amount: float
    source: str
    regular: bool = True
    notes: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('date')
    def date_not_empty(cls, value):
        if not value:
            raise ValueError('Date should not be empty')
        return value

    @validator('amount')
    def amount_not_empty(cls, value):
        if value is None:
            raise ValueError('Amount should not be empty')
        return value

    @validator('source')
    def source_not_empty(cls, value):
        if not value.strip():  # Check for whitespace as well
            raise ValueError('Source should not be empty')
        return value

    @validator('amount')
    def amount_is_numeric(cls, value):
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError('Amount must be a valid number')
        return value

    @validator('notes', pre=True)
    def empty_string_to_none(cls, value):
        return value if value and value.strip() else None


