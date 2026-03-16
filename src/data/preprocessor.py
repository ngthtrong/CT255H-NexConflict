"""
Preprocessing module for NexConflict Movie Recommender.
Cleans, filters, splits, and feature-engineers the MovieLens data.
"""
import logging
import re
from math import log

import numpy as np
import pandas as pd
from surprise import Dataset, Reader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NO_GENRES_LABEL: str = "(no genres listed)"
RATING_SCALE: tuple[float, float] = (0.5, 5.0)
POPULAR_MIN_RATINGS: int = 100


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_sparse(
    ratings: pd.DataFrame,
    min_user_ratings: int = 20,
    min_item_ratings: int = 10,
) -> pd.DataFrame:
    """
    Iteratively remove users with fewer than *min_user_ratings* ratings
    and items with fewer than *min_item_ratings* ratings until stable.

    Args:
        ratings: Ratings DataFrame (userId, movieId, rating, …).
        min_user_ratings: Minimum ratings a user must have to be kept.
        min_item_ratings: Minimum ratings an item must have to be kept.

    Returns:
        Filtered pd.DataFrame.
    """
    df = ratings.copy()
    iteration = 0

    while True:
        n_before = len(df)
        n_users_before = df["userId"].nunique()
        n_items_before = df["movieId"].nunique()

        # Filter users
        user_counts = df.groupby("userId")["rating"].count()
        valid_users = user_counts[user_counts >= min_user_ratings].index
        df = df[df["userId"].isin(valid_users)]

        # Filter items
        item_counts = df.groupby("movieId")["rating"].count()
        valid_items = item_counts[item_counts >= min_item_ratings].index
        df = df[df["movieId"].isin(valid_items)]

        iteration += 1
        n_after = len(df)

        logger.info(
            "filter_sparse iteration %d: users %d→%d, items %d→%d, ratings %d→%d",
            iteration,
            n_users_before,
            df["userId"].nunique(),
            n_items_before,
            df["movieId"].nunique(),
            n_before,
            n_after,
        )

        if n_after == n_before:
            break

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Feature extraction helpers
# ---------------------------------------------------------------------------

def extract_year(title: str) -> int | None:
    """
    Extract the release year from a movie title.

    Example: "Toy Story (1995)" → 1995.

    Args:
        title: Movie title string, e.g. "Toy Story (1995)".

    Returns:
        Year as int, or None if not found.
    """
    match = re.search(r"\((\d{4})\)\s*$", str(title))
    if match:
        return int(match.group(1))
    return None


def parse_genres(genres_str: str) -> list[str]:
    """
    Parse a pipe-separated genre string into a list of genre names.

    Examples:
        "Action|Comedy|Drama" → ["Action", "Comedy", "Drama"]
        "(no genres listed)"  → []

    Args:
        genres_str: Pipe-separated genres string.

    Returns:
        List of genre strings (may be empty).
    """
    if not isinstance(genres_str, str) or genres_str.strip() == NO_GENRES_LABEL:
        return []
    return [g.strip() for g in genres_str.split("|") if g.strip()]


# ---------------------------------------------------------------------------
# Movie enrichment
# ---------------------------------------------------------------------------

def enrich_movies(movies: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns to the movies DataFrame:

    * ``year``        – release year extracted from title
    * ``genres_list`` – list[str] of genre names
    * ``avg_rating``  – mean rating across all user ratings
    * ``num_ratings`` – total number of ratings

    Args:
        movies:  Movies DataFrame (movieId, title, genres).
        ratings: Ratings DataFrame (userId, movieId, rating, …).

    Returns:
        Enriched movies DataFrame.
    """
    df = movies.copy()

    df["year"] = df["title"].map(extract_year)
    df["genres_list"] = df["genres"].map(parse_genres)

    agg = (
        ratings.groupby("movieId")["rating"]
        .agg(avg_rating="mean", num_ratings="count")
        .reset_index()
    )
    agg["avg_rating"] = agg["avg_rating"].astype("float32")
    agg["movieId"] = agg["movieId"].astype("int32")

    df = df.merge(agg, on="movieId", how="left")
    df["avg_rating"] = df["avg_rating"].fillna(0.0).astype("float32")
    df["num_ratings"] = df["num_ratings"].fillna(0).astype("int32")

    logger.info("enrich_movies: added year, genres_list, avg_rating, num_ratings columns")
    return df


# ---------------------------------------------------------------------------
# Train / test split
# ---------------------------------------------------------------------------

def time_split(
    ratings: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split ratings by timestamp: oldest *train_ratio* → train, rest → test.

    Args:
        ratings:     Ratings DataFrame (must contain a ``timestamp`` column).
        train_ratio: Fraction of rows (by time) to use for training.

    Returns:
        Tuple of (train_df, test_df).
    """
    sorted_df = ratings.sort_values("timestamp").reset_index(drop=True)
    split_idx = int(len(sorted_df) * train_ratio)

    train_df = sorted_df.iloc[:split_idx].reset_index(drop=True)
    test_df = sorted_df.iloc[split_idx:].reset_index(drop=True)

    logger.info(
        "time_split: train=%d rows, test=%d rows (ratio=%.2f)",
        len(train_df),
        len(test_df),
        train_ratio,
    )
    return train_df, test_df


# ---------------------------------------------------------------------------
# Surprise dataset creation
# ---------------------------------------------------------------------------

def create_surprise_dataset(ratings_df: pd.DataFrame) -> tuple:
    """
    Convert a pandas ratings DataFrame to a Surprise trainset and testset.

    Args:
        ratings_df: DataFrame with at least columns userId, movieId, rating.

    Returns:
        Tuple of (trainset, testset_as_list) where testset is the Surprise
        anti-trainset (all (user, item) pairs not in trainset).
    """
    reader = Reader(rating_scale=RATING_SCALE)
    dataset = Dataset.load_from_df(
        ratings_df[["userId", "movieId", "rating"]], reader
    )
    trainset = dataset.build_full_trainset()
    testset = trainset.build_anti_testset()

    logger.info(
        "create_surprise_dataset: trainset=%d ratings, anti-testset≈%d pairs",
        trainset.n_ratings,
        len(testset),
    )
    return trainset, testset


# ---------------------------------------------------------------------------
# Popular movies
# ---------------------------------------------------------------------------

def get_popular_movies(movies: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    """
    Return the top-*n* popular movies ranked by a weighted popularity score.

    Score = avg_rating × log(num_ratings).
    Only considers movies with at least ``POPULAR_MIN_RATINGS`` ratings.

    Args:
        movies: Enriched movies DataFrame (must have avg_rating, num_ratings).
        n:      Number of movies to return.

    Returns:
        DataFrame with columns [movieId, title, genres, avg_rating, num_ratings].
    """
    df = movies[movies["num_ratings"] >= POPULAR_MIN_RATINGS].copy()
    df["_score"] = df["avg_rating"] * df["num_ratings"].map(
        lambda x: log(x) if x > 0 else 0.0
    )
    top = df.nlargest(n, "_score")[
        ["movieId", "title", "genres", "avg_rating", "num_ratings"]
    ].reset_index(drop=True)

    logger.info("get_popular_movies: returned top %d of %d eligible movies", len(top), len(df))
    return top


# ---------------------------------------------------------------------------
# Genre helpers
# ---------------------------------------------------------------------------

def get_movies_by_genre(movies: pd.DataFrame, genre: str) -> pd.DataFrame:
    """
    Filter movies that contain *genre* (case-insensitive, partial match).

    Args:
        movies: Movies DataFrame (genres column must exist).
        genre:  Genre string to search for.

    Returns:
        Filtered DataFrame.
    """
    mask = movies["genres"].str.contains(genre, case=False, na=False)
    return movies[mask].reset_index(drop=True)


def get_all_genres(movies: pd.DataFrame) -> list[str]:
    """
    Return a sorted list of all unique genre names present in the dataset.

    Args:
        movies: Movies DataFrame (genres column must exist).

    Returns:
        Sorted list of unique genre strings.
    """
    genres: set[str] = set()
    for genres_str in movies["genres"].dropna():
        for g in parse_genres(str(genres_str)):
            genres.add(g)
    return sorted(genres)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from loader import load_ratings, load_movies, sample_data, get_stats, get_data_dir

    data_dir = get_data_dir()

    ratings = load_ratings(data_dir)
    movies = load_movies(data_dir)

    sampled = sample_data(ratings)
    logger.info("Stats after sampling: %s", get_stats(sampled, movies))

    filtered = filter_sparse(sampled)
    logger.info("Stats after filtering: %s", get_stats(filtered, movies))

    enriched = enrich_movies(movies, filtered)
    logger.info("Enriched columns: %s", list(enriched.columns))

    train_df, test_df = time_split(filtered)
    logger.info("Train shape: %s, Test shape: %s", train_df.shape, test_df.shape)

    trainset, testset = create_surprise_dataset(train_df)
    logger.info("Surprise trainset n_ratings: %d", trainset.n_ratings)

    popular = get_popular_movies(enriched)
    logger.info("Popular movies (top 5):\n%s", popular.head())

    all_genres = get_all_genres(enriched)
    logger.info("All genres (%d): %s", len(all_genres), all_genres)
