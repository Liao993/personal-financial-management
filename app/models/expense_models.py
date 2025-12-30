
from pydantic import BaseModel, validator # type: ignore
from datetime import date
from typing import Optional
from utils.data import expense_category_options, traveling_category_options

class Expense(BaseModel):
    date: date
    items: str
    amount: float
    category: str
    traveling_category: Optional[str] = None 
    trip: Optional[str] = None 
    source_notes: Optional[str] = None
    payment_method: Optional[str] = None
    house_category: Optional[str] = None
    amount_for_number_of_travelers: Optional[int] = None
    paid_for_number_of_travlerers: Optional[int] = None

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
        if value == "Not Categorized":
            raise ValueError('Category must be defined, "Not Categorized" is not allowed.')
        if value not in expense_category_options:
            raise ValueError(f'Category must be one of {expense_category_options}')
        return value
    
    @validator('traveling_category')
    def traveling_category_in_list(cls, value):
        if value is not None and value not in traveling_category_options:
            raise ValueError(f'Traveling category must be one of {traveling_category_options}')
        return value
    

    @validator('category')
    def category_traveling_check(cls, value, values):
        traveling_category = values.get('traveling_category')
        if value != 'Traveling' and traveling_category is not None:
            raise ValueError("If traveling_category is provided, category must be 'Traveling'")
        return value
    
    @validator('traveling_category')
    def traveling_category_check(cls, value, values):
        category = values.get('category')
        if value is not None and category != 'Traveling':
            raise ValueError("If traveling_category is provided, category must be 'Traveling'")
        if category == 'Traveling' and value is None:
            raise ValueError("If category is 'Traveling', traveling_category cannot be None")
        return value
    
    @validator('trip')
    def trip_check(cls, value, values):
        category = values.get('category')
        if value is not None and category != 'Traveling':
            raise ValueError("If trip is provided, category must be 'Traveling'")
        if category == 'Traveling' and value is None:
            raise ValueError("If category is 'Traveling', trip cannot be None")
        return value