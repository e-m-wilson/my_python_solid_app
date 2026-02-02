from typing import Protocol
from src.domain.checkout_history import CheckoutHistory

class CheckoutHistoryRepositoryProtocol(Protocol):
    def add_record(self, checkoutHistory: CheckoutHistory) -> str:
        ...

    def get_history_for_book(self, book_id: str) -> list[CheckoutHistory]:
        ...
