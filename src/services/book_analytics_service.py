import numpy as np
from src.domain.book import Book

# Rules:
# keep numpy in service layer. it should NOT enter domain EVER
# if any numpy imports are in domain or repo layers - this is a design smell
# notice how each method takes in List[Book] and returns normal datatypes NOT ndarrays!
# -- this keeps our tests CLEAN and our functions PURE

class BookAnalyticsService:
    def average_price(self, books: list[Book]) -> float:
        prices = np.array([b.price_usd for b in books], dtype=float)
        return float(prices.mean())

    def top_rated(self, books: list[Book], min_ratings: int = 1000) -> list[Book]:
        ratings = np.array([b.average_rating for b in books])
        counts = np.array([b.ratings_count for b in books])

        # this says: "get me all books that have a minimum of 1000 ratings"
        mask = counts >= min_ratings
        filtered = np.array(books)[mask]

        # what we have now:
        # books -> book objects
        # ratings -> numbers
        # counts -> numbers
        #
        # its important that arrays stay 'in alignment' 
        # until the next line of code, 'ratings' technically still has ALL ratings from ALL books
        # so we need to put the mask to ratings as well to end up with an array 
        # of books that have over 1000 ratings and all of their scores only (instead of all books)
        scores = ratings[mask]
        # 'np.argsort(scores)' <- returns indexes that would sort our array
        # '[::-1]' <- sort in descending order
        sorted_idx = np.argsort(scores)[::-1]
        # return our filtered records that are sorted, converted to List[Book]
        return filtered[sorted_idx].tolist()

    # Value Score = rating × log(ratings_count) ÷ price
    def value_scores(self, books: list[Book]) -> dict[str, float]:
        ratings = np.array([b.average_rating for b in books])
        counts = np.array([b.ratings_count for b in books])
        prices = np.array([b.price_usd for b in books])

        scores = (ratings * np.log1p(counts)) / prices

        # this is a dictionary comprehension:
        return {
            # key : value
            book.book_id: float(score)
            # zip() iterates both lists in parallel, 
            # pairing each book with its corresponding score
            # zip stops if one list is shorter
            # if same key appears more than once, later entries overwrite earlier ones
            for book, score in zip(books, scores)
        }
