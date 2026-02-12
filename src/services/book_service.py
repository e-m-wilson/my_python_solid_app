from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.domain.book import Book
from src.domain.exceptions import NotFoundException
import logging
logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, repo: BookRepositoryProtocol):
        self.repo = repo

    def get_all_books(self) -> list[Book]:
        return self.repo.get_all_books()

    def add_book(self, book:Book) -> str:
        return self.repo.add_book(book)
    
    def find_book_by_id(self, book_id:str) -> Book:
        book = self.repo.find_book_by_id(book_id)
        if book is None:
            raise NotFoundException(f"Book not found with ID:{book_id}.")
        return book


    def find_book_by_name(self, query:str) -> list[Book]:
        if not isinstance(query, str):
            raise TypeError('Expected str, got something else.')
        return self.repo.find_book_by_name(query)

    def add_seed_records(self, books: list[Book]) -> None:
        self.repo.add_seed_records(books)
