from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.domain.book import Book

class BookService:
    def __init__(self, book_repo: BookRepositoryProtocol):
        self.book_repo = book_repo

    def get_all_books(self) -> list[Book]:
        return self.book_repo.get_all_books()

    def add_book(self, book:Book) -> str:
        return self.book_repo.add_book(book)

    def find_book_by_name(self, query:str) -> list[Book]:
        if not isinstance(query, str):
            raise TypeError('Expected str, got something else.')
        return self.book_repo.find_book_by_name(query)

    def check_out_book(self, book_id:str) -> Book:
        if not isinstance(book_id, str):
            raise TypeError('Expected str, got something else.')
        return self.book_repo.check_out_book(book_id)

    def check_in_book(self, book_id:str) -> Book:
        if not isinstance(book_id, str):
            raise TypeError('Expected str, got something else.')
        return self.book_repo.check_in_book(book_id)

    def add_seed_records(self, books: list[Book]) -> None:
        self.book_repo.add_seed_records(books)
