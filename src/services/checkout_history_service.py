from sqlalchemy.exc import SQLAlchemyError

from src.domain.exceptions import AppErrorException, NotFoundException
import logging


from src.repositories.checkout_history_protocol import CheckoutHistoryRepositoryProtocol
from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.domain.checkout_history import CheckoutHistory
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# passing this db like this is a design smell 
# if we were aiming for perfect SOLID/CLEAN architecture
# our service: knows about SQLAlchemy, knows about sessions, manages transactions
# ^^^ This is our design smell
# our service should only coordinate the business objective (check-in/out)
# our service should NOT manage transactions: commit() + rollback()
# what to do instead? Unit of Work pattern UoW
# devil's advocate: will this catch on fire? no, UoW would be ideal, but this 
# will work for prod even - depending on how picky and stringent you need to be (for enterprise certainly not - small companies probably okay). 
# We lose the flexibility to switch ORM's if we needed to. 
# If we use UoW it will also make tests easier because we can just create a mock UoW
#  
class CheckoutHistoryService:
    def __init__(self,
                 db,
                 book_repo: BookRepositoryProtocol,
                 checkout_history_repo: CheckoutHistoryRepositoryProtocol
        ):
        self.db = db
        self.book_repo = book_repo
        self.checkout_history_repo = checkout_history_repo

    def add_seed_records(self, records: list[CheckoutHistory]) -> None:
        self.checkout_history_repo.add_seed_records(records)
    
    def get_checkout_history_all(self) -> list[CheckoutHistory]:
        return self.checkout_history_repo.get_checkout_history_all()
    
    def get_checkout_history(self, book_id: str) -> list[CheckoutHistory]:
        if not isinstance(book_id, str):
            raise TypeError('Expected str, got something else!')
        return self.checkout_history_repo.get_history_for_book(book_id)
    
    def check_in_book(self, book_id: str) -> str:
        try:
            book = self.book_repo.find_book_by_id(book_id)
            if book is None:
                raise NotFoundException(f"Book not found. ID={book_id}")
            if book.available is True:
                raise AppErrorException(f"This book is already checked in. ID={book_id}")
            
            self.book_repo.check_in_book(book_id)

            record = CheckoutHistory(
                book_id=book_id,
                returned_date=datetime.now(timezone.utc),
                returned=True
            )

            self.checkout_history_repo.add_record(record)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def check_out_book(self, book_id: str) -> str:
        try:
            book = self.book_repo.find_book_by_id(book_id)
            if book is None:
                raise NotFoundException(f"Book not found. ID={book_id}")
            if book.available is False:
                raise AppErrorException(f"Book isn't available for checkout. ID={book_id}")
            self.book_repo.check_out_book(book_id)

            record = CheckoutHistory(
                book_id=book_id,
                checkout_date=datetime.now(timezone.utc),
                returned=False
            )

            self.checkout_history_repo.add_record(record)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
