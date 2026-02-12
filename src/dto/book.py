from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class BookCreate(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    page_count: Optional[int] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None
    price_usd: Optional[float] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    format: Optional[str] = None
    in_print: Optional[bool] = True
    sales_millions: Optional[float] = None
    available: Optional[bool] = None
    publisher_email: Optional[str] = None


class BookRead(BaseModel):
    book_id: UUID
    title: str
    author: str
    available: bool

    model_config = ConfigDict(
        from_attributes = True
    )
