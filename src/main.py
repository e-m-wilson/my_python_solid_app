import os

from uuid import UUID
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.book import Book
from src.pydantic_schemas.book import BookCreate, BookRead
from src.pydantic_schemas.checkout_history import CheckoutHistoryCreate, CheckoutHistoryRead
from src.repositories.book_repository_sql import SQLBookRepository
from src.repositories.checkout_history_repo import SQLCheckoutHistoryRepository
from src.services.book_analytics_service import BookAnalyticsService
from src.services.book_generator_service_V2 import generate
from src.services.book_service import BookService
from src.services.checkout_history_service import CheckoutHistoryService

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("No database!")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Book API")

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
#
#    Checkout History Endpoints
#
#
#
@app.post("/checkinbook")
def check_in_book(payload: CheckoutHistoryCreate, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckoutHistoryRepository(db)

    svc = CheckoutHistoryService(db, book_repo, check_book_repo)
    svc.check_in_book(payload.book_id)

    return {"status": "checked in"}

@app.post("/checkoutbook")
def check_out_book(payload: CheckoutHistoryCreate, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckoutHistoryRepository(db)

    svc = CheckoutHistoryService(db, book_repo, check_book_repo)
    svc.check_out_book(payload.book_id)

    return {"status": "checked out"}

@app.get("/checkouthistory", response_model=list[CheckoutHistoryRead])
def checkout_history(book_id: UUID, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckoutHistoryRepository(db)

    svc = CheckoutHistoryService(db, book_repo, check_book_repo)
    history = svc.get_checkout_history(str(book_id))

    return history

@app.get("/checkouthistoryall", response_model=list[CheckoutHistoryRead])
def checkout_history_all(db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckoutHistoryRepository(db)

    svc = CheckoutHistoryService(db, book_repo, check_book_repo)
    history = svc.get_checkout_history_all()

    return history



#
#
#     Book Endpoints
#
#
@app.post("/generate")
def generate_seed_books(db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    checkout_repo = SQLCheckoutHistoryRepository(db)
    book_svc = BookService(book_repo)
    checkout_svc = CheckoutHistoryService(db, book_repo, checkout_repo)
    (books, checkout_histories) = generate()
    book_svc.add_seed_records(books)
    checkout_svc.add_seed_records(checkout_histories)
    return 'Books were added to DB......'

@app.get("/books", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    svc = BookService(book_repo)
    return svc.get_all_books()

@app.post("/books", response_model=str)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    book = Book(**payload.model_dump())
    book_id = svc.add_book(book)
    return book_id

@app.get('/books/search', response_model=list[BookRead])
def search_books(title: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    return svc.find_book_by_name(title)




#
#
#    Analytics Endpoints
#
#
@app.get("/analytics/average_price")
def average_price(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    analytics = BookAnalyticsService()
    books = svc.get_all_books()
    if not books:
        return {"average_price": None}
    return {"average_price": analytics.average_price(books)}


@app.get("/analytics/top_books", response_model=list[BookRead])
def top_books(min_ratings: int = 1000, limit: int = 10, db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    analytics = BookAnalyticsService()
    books = svc.get_all_books()
    return analytics.top_rated_with_pandas(books, min_ratings, limit)


@app.get("/analytics/value_scores")
def value_scores(limit: int = 10, db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    analytics = BookAnalyticsService()
    books = svc.get_all_books()
    return analytics.value_scores_with_pandas(books, limit)


@app.get("/joke")
def get_joke():
    import requests
    try:
        r = requests.get("https://api.chucknorris.io/jokes/random", timeout=5)
        r.raise_for_status()
        return {"joke": r.json().get("value")}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e))
