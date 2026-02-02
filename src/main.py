import os
from typing import List, Optional
from uuid import UUID

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.book import Book as BookModel
from src.repositories.book_repository_sql import SQLBookRepository
from src.services.book_analytics_service import BookAnalyticsService
from src.services.book_generator_service_V2 import generate_books
from src.services.book_service import BookService

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


class BookCreate(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    page_count: Optional[int] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None
    price_usd: Optional[float] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    format: Optional[str] = None
    in_print: Optional[bool] = True
    sales_millions: Optional[float] = None
    last_checkout: Optional[str] = None
    publisher_email: Optional[str] = None


class BookRead(BookCreate):
    book_id: UUID
    available: Optional[bool] = True

    class Config:
        orm_mode = True


@app.get("/books", response_model=List[BookRead])
def list_books(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    return svc.get_all_books()


@app.post("/books", response_model=str)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    book = BookModel(**payload.dict())
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

@app.get("/books/search", response_model=List[BookRead])
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


@app.get("/analytics/top_books", response_model=List[BookRead])
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
