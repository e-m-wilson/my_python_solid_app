from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CheckoutHistoryCreate(BaseModel):
    book_id: UUID
    checkout_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    returned: Optional[bool] = False


class CheckoutHistoryRead(CheckoutHistoryCreate):
    checkout_id: UUID
    book_id: UUID
    checkout_date: datetime
    due_date: Optional[datetime]
    return_date: Optional[datetime]
    returned: bool

    class Config:
        from_attributes = True