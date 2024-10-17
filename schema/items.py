from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class ItemCreate(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: date
    
class ItemUpdate(BaseModel):
    email: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    expiry_date: Optional[str] = None 