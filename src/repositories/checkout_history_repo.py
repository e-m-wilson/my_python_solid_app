from sqlalchemy.orm import Session
from src.domain.checkout_history import CheckoutHistory
from src.repositories.checkout_history_protocol import CheckoutHistoryRepositoryProtocol

class SQLCheckHistoryRepository(CheckoutHistoryRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def add_record(self, record: CheckoutHistory) -> None:
        self.session.add(record)
        # Do NOT commit here because the service manages transactions
        # Let the service control commit/rollback (no need to call commit, db.begin() + db.rollback() handle it)
        # Because we are also updating another table at the same time (book)

    def get_history_for_book(self, book_id: str) -> list[CheckoutHistory]:
        return (
            self.session.query(CheckoutHistory)
            .filter(CheckoutHistory.book_id == book_id)
            .order_by(CheckoutHistory.checkout_date.asc())
            .all()
        )

    def add_seed_records(self, records: list[CheckoutHistory]) -> None:
        for r in records:
            self.session.add(r)
        
        self.session.commit()

    def get_checkout_history_all(self) -> list[CheckoutHistory]:
        return self.session.query(CheckoutHistory).all()