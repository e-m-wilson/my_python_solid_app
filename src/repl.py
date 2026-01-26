import requests

from src.domain.book import Book
from src.repositories.book_repository import BookRepository
from src.services import generate_books
from src.services.book_service import BookService


class BookREPL:
    def __init__(self, book_svc):
        self.running = True
        self.book_svc = book_svc

    def start(self):
        print('Welcome to the book app! Type \'Help\' for a list of commands!')
        while self.running:
            cmd = input('>>>').strip()
            self.handle_command(cmd)

    def handle_command(self, cmd):
        if cmd == 'exit':
            self.running = False
            print('Goodbye!')
        elif cmd == 'getAllRecords':
            self.get_all_records()
        elif cmd == 'addBook':
            self.add_book()
        elif cmd == 'findByName':
            self.find_book_by_name()
        elif cmd == 'getJoke':
            self.get_joke()
        elif cmd == 'help':
            print('Available commands: addBook, getAllRecords, findByName, getJoke, help, exit')
        else:
            print('Please use a valid command!')

    def find_book_by_name(self):
        query = input('Please enter book name: ')
        books = self.book_svc.find_book_by_name(query)
        print(books)

    def get_all_records(self):
        books = self.book_svc.get_all_books()
        print(books)

    def add_book(self):
        try:
            print('Enter Book Details:')
            title = input('Title: ')
            author = input('Author: ')
            book = Book(title= title, author=author)
            new_book_id = self.book_svc.add_book(book)
            print(new_book_id)
        except Exception as e:
            print(f'An unexpected error has occurred: {e}')

    def get_joke(self):
        try:
            url = 'https://api.chucknorris.io/jokes/random'
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            print(response.json()['value'])
        except requests.exceptions.Timeout:
            print('Request timed out.')
        except requests.exceptions.HTTPError as e:
            print(f'HTTP error: {e}')
        except requests.exceptions.RequestException as e:
            print(f'Something else went wrong: {e}')


if __name__ == '__main__':
    generate_books()
    repo = BookRepository('books.json')
    book_service = BookService(repo)
    repl = BookREPL(book_service)
    repl.start()
