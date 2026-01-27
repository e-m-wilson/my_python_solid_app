import pytest
from src.domain.book import Book
from src.services.book_analytics_service import BookAnalyticsService as bas

def test_average_price():
    books = [
        Book(title="Book 1", author="Author 1", price_usd=10),
        Book(title="Book 2", author="Author 2", price_usd=20),
    ]

    svc = bas()
    assert svc.average_price(books) == 15.0
