import pytest
import src.services.book_service as book_service
from tests.mocks.mock_book_repository import MockBookRepo

def test_get_all_books_positive():
    # AAA - arrange, act, assert
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    books = svc.get_all_books()
    assert len(books) == 1

def test_find_book_name_negative():
    name = 2
    repo = MockBookRepo()
    svc = book_service.BookService(repo)

    with pytest.raises(TypeError) as e:
        book = svc.find_book_by_name(name)
    assert str(e.value) == 'Expected str, got something else.'
