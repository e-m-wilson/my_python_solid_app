from sqlalchemy.orm import Session
from src.domain.book import Book
from src.repositories.book_repository_protocol import BookRepositoryProtocol

class SQLBookRepository(BookRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def get_all_books(self) -> list[Book]:
        return self.session.query(Book).all()

    def add_book(self, book:Book) -> str:
        self.session.add(book)
        self.session.commit()
        return str(book.book_id)

    def find_book_by_name(self, query:str) -> list[Book]:
        return self.session.query(Book).filter(Book.title == query).all()

    def check_out_book(self, book_id: str) -> Book:
        book = self.session.get(Book, book_id)
        if not book:
            raise Exception("Book now found.")
        book.check_out()
        self.session.commit()
        self.session.refresh(book)
        return book

    def check_in_book(self, book_id: str) -> Book:
        book = self.session.get(Book, book_id)
        if not book:
            raise Exception("Book now found.")
        book.check_in()
        self.session.commit()
        self.session.refresh(book)
        return book
