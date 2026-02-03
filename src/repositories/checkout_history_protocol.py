from typing import Protocol
from src.domain.checkout_history import CheckoutHistory

class CheckoutHistoryRepositoryProtocol(Protocol):
    def add_record(self, record: CheckoutHistory) -> str:
        ...
    
    def get_history_for_book(self, book_id: str) -> list[CheckoutHistory]:
        ...
    
    def get_checkout_history_all(self) -> list[CheckoutHistory]:
        ...

    def add_seed_records(self, records: list[CheckoutHistory]) -> None:
        ...
