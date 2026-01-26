from src.domain.book import Book

class MockBookRepo:
    def get_all_books(self):
        return [Book(title="Test", author="Author")]

    def add_book(self, book):
        return "mock_id"

    def find_book_by_name(self, query):
        return [Book(title="Test", author="Author")]
