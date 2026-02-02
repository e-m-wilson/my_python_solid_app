from src.repositories.checkout_history_protocol import CheckoutHistoryRepositoryProtocol
from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.domain.checkout_history import CheckoutHistory
from datetime import datetime, timezone

class CheckService:
    def __init__(self,
                 db,
                 book_repo: BookRepositoryProtocol,
                 check_book_repo: CheckoutHistoryRepositoryProtocol
        ):
        self.db = db
        self.book_repo = book_repo
        self.check_book_repo = check_book_repo

    def check_in_book(self, book_id: str) -> str:
        try:
            with self.db.begin():
                self.book_repo.check_in_book(book_id)

                record = CheckoutHistory(
                    book_id=book_id,
                    returned_date=datetime.now(timezone.utc),
                    returned=True
                )

            self.check_book_repo.add_record(record)
        except Exception:
            self.db.rollback()
            raise

    def check_out_book(self, book_id: str) -> str:
        try:
            with self.db.begin():
                self.book_repo.check_out_book(book_id)

                record = CheckoutHistory(
                    book_id = book_id,
                    checkout_date = datetime.now(timezone.utc),
                    returned = False
                )

            self.check_book_repo.add_record(record)
        except Exception:
            self.db.rollback()
            raise

    def get_checkout_history(self, book_id: str) -> list[CheckoutHistory]:
        if not isinstance(book_id, str):
            raise TypeError('Expected str, got something else.')

        return self.check_book_repo.get_history_for_book(book_id)
