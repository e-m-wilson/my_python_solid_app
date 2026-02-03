from sqlalchemy.orm import Session
from src.domain.checkout_history import CheckoutHistory
from src.repositories.checkout_history_protocol import CheckoutHistoryRepositoryProtocol

class SQLCheckoutHistoryRepository(CheckoutHistoryRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session
    
    def add_record(self, record: CheckoutHistory) -> str:
        self.session.add(record)
        self.session.commit()
    
    def get_history_for_book(self, book_id: str) -> list[CheckoutHistory]:
        return (
            self.session.query(CheckoutHistory)
            .filter(CheckoutHistory.book_id == book_id)
            .order_by(CheckoutHistory.checkout_date.asc())
            .all()
        )
    
    def get_checkout_history_all(self) -> list[CheckoutHistory]:
        return self.session.query(CheckoutHistory).all()
    
    def add_seed_records(self, records: list[CheckoutHistory]) -> None:
        for r in records:
            self.session.add(r)

        self.session.commit()
