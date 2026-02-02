import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.book import Book
from src.pydantic_schemas.book import BookCreate, BookRead
from src.repositories.book_repository_sql import SQLBookRepository
from src.services.book_analytics_service import BookAnalyticsService
from src.services.book_generator_service_V2 import generate_books
from src.services.book_service import BookService

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

@app.post("/books/generate")
def generate_seed_books(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    books = generate_books()

    for b in books:
        svc.add_book(b)
    
    return 'Books were added to DB...'

@app.get("/books", response_model=list[BookCreate])
def list_books(db: Session = Depends(get_db)):
    repo = SQLBookRepository(db)
    svc = BookService(repo)
    return svc.get_all_books()
