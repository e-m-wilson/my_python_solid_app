from sqlalchemy.orm import Session
from src.domain.checkout_history import CheckoutHistory
from src.repositories.checkout_history_protocol import CheckoutHistoryRepositoryProtocol

class SQLCheckHistoryRepository(CheckoutHistoryRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def add_record(self, record: CheckoutHistory) -> None:
        self.session.add(record)
        # Do NOT commit here because the service manages transactions
        # Let the service control commit/rollback
        # Because we are also updating another table at the same time (book)

    def get_history_for_book(self, book_id: str) -> list[CheckoutHistory]:
        return (
            self.session.query(CheckoutHistory)
            .filter(CheckoutHistory.book_id == book_id)
            .order_by(CheckoutHistory.timestamp.desc())
            .all()
        )
