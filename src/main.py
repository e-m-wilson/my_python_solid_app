from uuid import UUID
from fastapi import Depends, FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from src.domain.exceptions import AppErrorException, NotFoundException, PermissionDeniedException
from src.logging_config import setup_logging
import logging

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

# each module gets its own logger, 
# but this is only called once to setup our config
setup_logging()

# __name__ resolved to __main__ if run directly
# my_package.my_module if run from another file via imports
# common for each module to have it's own logger/separation of concerns 
logger = logging.getLogger(__name__)

app = FastAPI(title="Book API")


#
#      Setting up dependency injection for each of the endpoints
#      Depends() function from FastAPI is key, notice how each endpoint depends on the following 
#      Central location to swap out concretions    
#
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
#    These are FastAPI global exception handlers
#      We have one for HTTP exceptions (defensive, we SHOULD return HTTPExceptions from the endpoint as well)
#      The HTTPExcepction handler will take/handle our HTTPExceptions we throw in our endpoints - no try-except
#      These are controlled and expected errors.
#
#      The generic exception handler acts as a safety net for any other unhandled exceptions
#    Both of these will be called automatically by FastAPI
#    (assuming the exception isn't explicitly handled with try-except)
#    Order matters: notice that we declare the HTTP one FIRST; More specific > more general
#
# Controlled exceptions handled by the application:
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.exception("HTTP Exception occurred.")
    return JSONResponse(
        status_code=exc.status_code,
        # safe to return detail here - this is intentional
        content={"detail": exc.detail},
    )

# unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        # here we give a vague message; we are NOT exposing execution details to the client
        content={"detail": "Internal server error"},
    )


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
    try:
        logger.info("Checking out book id=%s", payload.book_id)
        svc.check_out_book(payload.book_id)
        return {"status": "checked out"}
    except NotFoundException:
        logger.warning("Book not found id=%s", payload.book_id)
        raise HTTPException(status_code=500, detail="Book not found.")
    except AppErrorException:
        logger.warning("Book already check out. id=%s", payload.book_id)
        raise HTTPException(status_code=400, detail="Book already checked out.")
    except Exception:
        logger.exception("Unexpected checkout failure")
        raise HTTPException(status_code=500, detail="Internal server error")

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
