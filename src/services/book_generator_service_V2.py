import json
import random
import uuid
from datetime import datetime, timedelta
import numpy as np
from src.domain.book import Book
from src.domain.checkout_history import CheckoutHistory


def generate(filename="books.json", count=500, seed=None) -> tuple[list[Book], list[CheckoutHistory]]:
    rng = np.random.default_rng(seed)
    random.seed(seed)

    genres = [
        "Fantasy",
        "Sci-Fi",
        "Non-Fiction",
        "Mystery",
        "Romance",
        "Technology",
        "History",
    ]
    # make Fantasy and Sci-Fi more popular
    genre_weights = np.array([0.28, 0.24, 0.12, 0.10, 0.08, 0.10, 0.08])
    genre_weights = genre_weights / genre_weights.sum()

    publishers = [
        "North Star Press",
        "Emerald House",
        "Atlas Publishing",
        "Blue River Books",
    ]

    formats = ["Hardcover", "Paperback", "Ebook", "Audiobook"]

    # Publication year distribution: fewer before 1950, increasing after 1950
    years = np.arange(1850, 2026)
    year_weights = np.where(years <= 1950, 0.2, 1.0 + (years - 1950) / (2025 - 1950))
    year_weights = year_weights / year_weights.sum()

    # make popularity multipliers from genre_weights (centered on 1.0)
    # positive values boost ratings_count and sales for popular genres
    # strengthen the effect so popular genres (Fantasy, Sci‑Fi) get noticeably higher counts
    genre_pop_mult = 1.0 + (genre_weights - genre_weights.mean()) * 4.0
    # stronger per-genre rating bias so popular genres tend to be rated higher
    genre_rating_bias = (genre_weights - genre_weights.mean()) * 1.2

    # Build correlated latent variables:
    # z0 -> price latent, z1 -> average_rating latent, z2 -> ratings_count latent
    cov = np.array([[1.0, 0.7, 0.3], [0.7, 1.0, 0.6], [0.3, 0.6, 1.0]])
    z = rng.multivariate_normal(mean=np.zeros(3), cov=cov, size=count)

    price_raw = z[:, 0]
    rating_raw = z[:, 1]
    rc_raw = z[:, 2]

    # Transform rating_raw -> average_rating in [1.0, 5.0] (target ~ mean 3.2, sd ~0.6)
    rating = (rating_raw - rating_raw.mean()) / (rating_raw.std() + 1e-9)
    average_rating = np.clip(np.round(rating * 0.6 + 3.2, 2), 1.0, 5.0)

    # Transform price_raw -> price_usd (log-scale so higher latent => substantially higher price)
    price_norm = (price_raw - price_raw.mean()) / (price_raw.std() + 1e-9)
    price_usd = np.round(np.clip(np.exp(price_norm * 0.45 + 2.2), 3.99, 299.99), 2)

    # Transform rc_raw -> ratings_count (positive, heavy-tail via exp)
    rc_norm = (rc_raw - rc_raw.mean()) / (rc_raw.std() + 1e-9)
    ratings_count = np.round(np.clip(np.exp(rc_norm * 0.9 + 4.5), 0, 200000)).astype(
        int
    )

    # sales_millions tends to be higher with average_rating + ratings_count
    # combine rating and log1p(ratings_count), then scale and add some noise
    score = (average_rating / 5.0) * 0.6 + (
        np.log1p(ratings_count) / np.log1p(ratings_count).max()
    ) * 0.4
    sales_loc = score * 10.0  # base scale so typical values are in 0..10 range
    sales_millions = np.round(
        np.clip(rng.normal(loc=sales_loc, scale=1.5), 0.01, 200.0), 2
    )

    books = []
    checkout_histories = []
    now = datetime.now()
    six_months_ago = now - timedelta(days=182)

    for i in range(1, count + 1):
        # publication year from weighted distribution
        pub_year = int(rng.choice(years, p=year_weights))

        idx = i - 1

        # choose genre and apply stronger popularity multiplier to ratings_count and sales
        genre_choice = str(rng.choice(genres, p=genre_weights))
        gidx = genres.index(genre_choice)

        adj_ratings_count = int(
            np.round(np.clip(ratings_count[idx] * genre_pop_mult[gidx], 0, 200000))
        )
        # compute sales based on the adjusted rating and adjusted ratings_count
        # keep the same weighting so rating => ~0.6 of sales influence
        rating_adj = float(
            np.clip(round(average_rating[idx] + genre_rating_bias[gidx], 2), 1.0, 5.0)
        )

        score_adj = (rating_adj / 5.0) * 0.6 + (
            np.log1p(adj_ratings_count) / np.log1p(ratings_count).max()
        ) * 0.4
        adj_sales_millions = float(
            np.round(
                np.clip(rng.normal(loc=score_adj * 10.0, scale=1.5), 0.01, 200.0), 2
            )
        )

        # apply a small genre-specific bias to average_rating so popularity shows in Bayesian avg
        # rating_adj already computed above for sales calculation
        book_id = str(uuid.uuid4())
        book = Book(
                book_id = book_id,
                title = f"Book Title {i}",
                author = f"Author {rng.integers(1, 80)}",
                genre = genre_choice,
                publication_year = pub_year,
                page_count = int(rng.integers(80, 1200)),
                average_rating = rating_adj,
                ratings_count = int(adj_ratings_count),
                price_usd = float(price_usd[idx]),
                publisher = random.choice(publishers),
                language = "English",
                format = random.choice(formats),
                in_print = bool(rng.choice([True, True, True, True, False])),
                sales_millions = float(adj_sales_millions),
                available = bool(rng.choice([True, False])),
            )
        books.append(book)

     # Generate checkout history for the book
        num_checkouts = rng.integers(0, 50)  # Random number of checkouts per book
        for _ in range(num_checkouts):
            checkout_date = datetime.now() - timedelta(
                days=int(rng.integers(0, 365)), seconds=int(rng.integers(0, 86400))
            )
            due_date = checkout_date + timedelta(days=14)
            return_date = (
                due_date + timedelta(days=int(rng.integers(0, 7)))
                if rng.choice([True, False])
                else None
            )
            returned = return_date is not None

            checkout_history = CheckoutHistory(
                checkout_id=uuid.uuid4(),
                book_id=book_id,
                checkout_date=checkout_date,
                due_date=due_date,
                return_date=return_date,
                returned=returned,
            )
            checkout_histories.append(checkout_history)

    return books, checkout_histories
