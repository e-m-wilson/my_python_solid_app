from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class CheckoutHistoryCreate(BaseModel):
    book_id: UUID
    checkout_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    returned: Optional[bool] = False

class CheckoutHistoryRead(CheckoutHistoryCreate):
    checkout_id: UUID
    book_id: UUID
    
    class Config:
        from_attributes = True
