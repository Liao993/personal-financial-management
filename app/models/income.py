
from pydantic import BaseModel # type: ignore
from datetime import date

class Income(BaseModel):
    date: date
    amount: float
    source: str
    regular: bool = True

    class Config:
        orm_mode = True