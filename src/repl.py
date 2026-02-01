from src.services.book_generator_service_V2 import generate_books_json
from src.services.book_generator_bad_data_service import generate_books as get_bad_books
from src.domain.book import Book
from src.services.book_service import BookService
from src.services.book_analytics_service import BookAnalyticsService
from src.repositories.book_repository import BookRepository
import requests

class BookREPL:
    def __init__(self, book_svc, book_analytics_svc):
        self.running = True
        self.book_svc = book_svc
        self.book_analytics_svc = book_analytics_svc

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
        elif cmd == 'getAveragePrice':
            self.get_average_price()
        elif cmd == 'getTopBooks':
            self.get_top_books()
        elif cmd == 'getValueScores':
            self.get_value_scores()
        elif cmd == 'help':
            print('Available commands: addBook, getAllRecords, findByName, getJoke, getAveragePrice, getTopBooks, getValueScores, help, exit')
        else:
            print('Please use a valid command!')

    def get_average_price(self):
        books = self.book_svc.get_all_books()
        avg_price = self.book_analytics_svc.average_price(books)
        print(avg_price)

    def get_top_books(self):
        books = self.book_svc.get_all_books()
        top_rated_books = self.book_analytics_svc.top_rated_with_pandas(books)
        print(top_rated_books)

    def get_value_scores(self):
        books = self.book_svc.get_all_books()
        value_scores = self.book_analytics_svc.value_scores_with_pandas(books)
        print(value_scores)

    def get_joke(self):
        try:
            url = 'https://api.chucknorris.io/jokes/random'
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            print(response.json()['value'])
        except requests.exceptions.Timeout:
            print('Request timed out.')
        except requests.exceptions.HTTPError as e:
            print(f'HTTP Error: {e}')
        except requests.exceptions.RequestException as e:
            print(f'Something else went wrong: {e}')

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

if __name__ == '__main__':
    generate_books_json()
    get_bad_books()
    repo = BookRepository('books.json')
    book_service = BookService(repo)
    book_analytics_service = BookAnalyticsService()
    repl = BookREPL(book_service, book_analytics_service)
    repl.start()
