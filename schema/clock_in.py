
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClockInRecord(BaseModel):
    email: str
    location: str


class UpdateClockInRecord(BaseModel):
    email: Optional[str] = None
    location: Optional[str] = None