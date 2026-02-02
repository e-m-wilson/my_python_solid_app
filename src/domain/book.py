import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

class Book(Base):
    __tablename__ = "books"

    book_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String, nullable=False)
    author = Column(String, nullable=False)

    genre = Column(String, nullable=True)
    publication_year = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    average_rating = Column(Float, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    price_usd = Column(Float, nullable=True)
    publisher = Column(String, nullable=True)
    language = Column(String, nullable=True)
    format = Column(String, nullable=True)
    in_print = Column(Boolean, nullable=True)
    sales_millions = Column(Float, nullable=True)
    available = Column(Boolean, default=True)
    publisher_email = Column(String, nullable=True)

    def check_out(self):
        if not self.available:
            raise Exception("Book is already checked out.")
        self.available = False

    def check_in(self):
        if self.available:
            raise Exception("Book is already available.")
        self.available = True
