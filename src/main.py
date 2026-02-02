import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.book import Book
from src.domain.checkout_history import CheckoutHistory
from src.schemas.book import BookCreate, BookRead
from src.schemas.checkout_history import CheckoutHistoryCreate, CheckoutHistoryRead
from src.repositories.book_repository_sql import SQLBookRepository
from src.repositories.checkout_history_repo import SQLCheckHistoryRepository
from src.services.book_analytics_service import BookAnalyticsService
from src.services.book_generator_service_V2 import generate_books
from src.services.book_service import BookService
from src.services.check_book_service import CheckService

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Books API")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/books", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    return svc.get_all_books()


@app.post("/books", response_model=str)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    book = Book(**payload.model_dump())
    new_id = svc.add_book(book)
    return new_id

@app.post("/books/generate")
def generate_seed_books(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    books = generate_books()
    for b in books:
        svc.add_book(b)

    return "Books added to DB..."

@app.post("/checkinbook")
def check_in_book(payload: CheckoutHistoryCreate, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckHistoryRepository(db)

    svc = CheckService(db, book_repo, check_book_repo)
    svc.check_in_book(payload.book_id)

    return {"status": "checked in"}

@app.post("/checkoutbook")
def check_out_book(payload: CheckoutHistoryCreate, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckHistoryRepository(db)

    svc = CheckService(db, book_repo, check_book_repo)
    svc.check_out_book(payload.book_id)

    return {"status": "checked out"}

@app.get("/checkouthistory", response_model=list[CheckoutHistoryRead])
def checkout_history(payload: CheckoutHistoryCreate, db: Session = Depends(get_db)):
    book_repo = SQLBookRepository(db)
    check_book_repo = SQLCheckHistoryRepository(db)

    svc = CheckService(db, book_repo, check_book_repo)
    history = svc.get_checkout_history(payload.book_id)

    return history

@app.get("/books/search", response_model=list[BookRead])
def search_books(title: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    return svc.find_book_by_name(title)


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


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
