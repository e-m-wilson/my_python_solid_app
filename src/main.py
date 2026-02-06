from uuid import UUID
from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.domain.book import Book
from src.dto.book import BookCreate, BookRead
from src.dto.checkout_history import CheckoutHistoryCreate, CheckoutHistoryRead
from src.repositories.book_repository_sql import SQLBookRepository
from src.repositories.checkout_history_repo import SQLCheckoutHistoryRepository
from src.services.book_analytics_service import BookAnalyticsService
from src.services.book_generator_service_V2 import generate
from src.services.book_service import BookService
from src.services.checkout_history_service import CheckoutHistoryService

app = FastAPI(title="Book API")

def get_book_repository(db: Session = Depends(get_db)) -> SQLBookRepository:
    return SQLBookRepository(db)

def get_book_service(repo: SQLBookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repo)

def get_checkout_history_repository(db: Session = Depends(get_db)) -> SQLCheckoutHistoryRepository:
    return SQLCheckoutHistoryRepository(db)

def get_checkout_history_service(
        db: Session = Depends(get_db),
        book_repo: SQLBookRepository = Depends(get_book_repository),
        checkout_repo: SQLCheckoutHistoryRepository = Depends(get_checkout_history_repository),
        ) -> CheckoutHistoryService:
    return CheckoutHistoryService(db, book_repo, checkout_repo)

def get_book_analytics_service() -> BookAnalyticsService:
    return BookAnalyticsService()


#
#
#    Checkout History Endpoints
#
#
#
@app.post("/checkinbook")
def check_in_book(
    payload: CheckoutHistoryCreate,
    svc: CheckoutHistoryService = Depends(get_checkout_history_service),
):
    svc.check_in_book(payload.book_id)
    return {"status": "checked in"}


@app.post("/checkoutbook")
def check_out_book(
    payload: CheckoutHistoryCreate,
    svc: CheckoutHistoryService = Depends(get_checkout_history_service),
):
    svc.check_out_book(payload.book_id)
    return {"status": "checked out"}


@app.get("/checkouthistory", response_model=list[CheckoutHistoryRead])
def checkout_history(
    book_id: UUID,
    svc: CheckoutHistoryService = Depends(get_checkout_history_service),
):
    return svc.get_checkout_history(str(book_id))


@app.get("/checkouthistoryall", response_model=list[CheckoutHistoryRead])
def checkout_history_all(
    svc: CheckoutHistoryService = Depends(get_checkout_history_service),
):
    return svc.get_checkout_history_all()




#
#
#     Book Endpoints
#
#
@app.post("/generate")
def generate_seed_books(
    book_svc: BookService = Depends(get_book_service),
    checkout_svc: CheckoutHistoryService = Depends(get_checkout_history_service),
):
    books, checkout_histories = generate()
    book_svc.add_seed_records(books)
    checkout_svc.add_seed_records(checkout_histories)
    return "Books were added to DB......"


@app.get("/books", response_model=list[BookRead])
def list_books(svc: BookService = Depends(get_book_service)):
    return svc.get_all_books()

@app.post("/books", response_model=str)
def create_book(payload: BookCreate, 
                svc: BookService = Depends(get_book_service)
    ):
    book = Book(**payload.model_dump())
    book_id = svc.add_book(book)
    return book_id

@app.get("/books/search", response_model=list[BookRead])
def search_books(
    title: str = Query(..., min_length=1),
    svc: BookService = Depends(get_book_service),
):
    return svc.find_book_by_name(title)

#
#
#    Analytics Endpoints
#
#
@app.get("/analytics/average_price")
def average_price(
    svc: BookService = Depends(get_book_service),
    analytics: BookAnalyticsService = Depends(get_book_analytics_service),
):
    books = svc.get_all_books()
    if not books:
        return {"average_price": None}
    return {"average_price": analytics.average_price(books)}



@app.get("/analytics/top_books", response_model=list[BookRead])
def top_books(
    min_ratings: int = 1000,
    limit: int = 10,
    svc: BookService = Depends(get_book_service),
    analytics: BookAnalyticsService = Depends(get_book_analytics_service),
):
    books = svc.get_all_books()
    return analytics.top_rated_with_pandas(books, min_ratings, limit)



@app.get("/analytics/value_scores")
def value_scores(
    limit: int = 10,
    svc: BookService = Depends(get_book_service),
    analytics: BookAnalyticsService = Depends(get_book_analytics_service),
):
    books = svc.get_all_books()
    return analytics.value_scores_with_pandas(books, limit)