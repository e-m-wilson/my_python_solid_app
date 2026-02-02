import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.base import Base

class CheckoutHistory(Base):
    __tablename__ = "checkout_history"

    checkout_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Book
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.book_id"), nullable=False)
    
    checkout_date = Column(DateTime, default=datetime.now(timezone.utc))
    return_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    returned = Column(Boolean, default=False)

    # Relationship for easy access from Book
    book = relationship("Book", backref="checkout_records")
