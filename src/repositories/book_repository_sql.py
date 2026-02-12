from sqlalchemy.orm import Session
from src.domain.book import Book
from src.repositories.book_repository_protocol import BookRepositoryProtocol

class SQLBookRepository(BookRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def get_all_books(self) -> list[Book]:
        return self.session.query(Book).all()
    
    def find_book_by_id(self, book_id:str) ->  Book:
        return self.session.get(Book, book_id)

    def add_book(self, book:Book) -> str:
        self.session.add(book)
        self.session.commit()
        return str(book.book_id)

    def find_book_by_name(self, query:str) -> list[Book]:
        return self.session.query(Book).filter(Book.title == query).all()

    def check_out_book(self, book_id: str) -> Book:
        book = self.session.get(Book, book_id)
        book.available = False
        self.session.commit()
        return book

    def check_in_book(self, book_id: str) -> Book:
        book = self.session.get(Book, book_id)
        book.available = True
        self.session.commit()
        return book

    def add_seed_records(self, books: list[Book]) -> None:
        for b in books:
            self.session.add(b)

        self.session.commit()