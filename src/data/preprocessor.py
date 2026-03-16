"""
Preprocessing module for NexConflict Movie Recommender.
Cleans, filters, and transforms raw data for model training.
"""

import logging
import re

import numpy as np
import pandas as pd
from surprise import Dataset, Reader

logger = logging.getLogger(__name__)


def filter_sparse(
    ratings: pd.DataFrame,
    min_user_ratings: int = 20,
    min_item_ratings: int = 10,
) -> pd.DataFrame:
    """
    Iteratively filter sparse users and items until stable.

    Args:
        ratings: Ratings DataFrame.
        min_user_ratings: Minimum number of ratings per user.
        min_item_ratings: Minimum number of ratings per item.

    Returns:
        Filtered ratings DataFrame.
    """
    df = ratings.copy()
    iteration = 0
    while True:
        n_before = len(df)
        user_counts = df["userId"].value_counts()
        valid_users = user_counts[user_counts >= min_user_ratings].index
        df = df[df["userId"].isin(valid_users)]

        item_counts = df["movieId"].value_counts()
        valid_items = item_counts[item_counts >= min_item_ratings].index
        df = df[df["movieId"].isin(valid_items)]

        iteration += 1
        n_after = len(df)
        logger.info(
            f"Filter iteration {iteration}: {n_before:,} → {n_after:,} ratings "
            f"({df['userId'].nunique():,} users, {df['movieId'].nunique():,} items)"
        )
        if n_after == n_before:
            break
    return df


def extract_year(title: str) -> int | None:
    """
    Extract year from movie title.

    Args:
        title: Movie title string, e.g. "Toy Story (1995)".

    Returns:
        Year as int, or None if not found.
    """
    match = re.search(r"\((\d{4})\)\s*$", title)
    if match:
        return int(match.group(1))
    return None


def parse_genres(genres_str: str) -> list[str]:
    """
    Parse pipe-separated genres string into a list.

    Args:
        genres_str: e.g. "Action|Comedy|Drama" or "(no genres listed)".

    Returns:
        List of genre strings.
    """
    if not isinstance(genres_str, str) or genres_str == "(no genres listed)":
        return []
    return [g.strip() for g in genres_str.split("|") if g.strip()]


def enrich_movies(movies: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns to movies DataFrame.

    Adds: year, genres_list, avg_rating, num_ratings.

    Args:
        movies: Movies DataFrame.
        ratings: Ratings DataFrame (used to compute avg_rating, num_ratings).

    Returns:
        Enriched movies DataFrame.
    """
    df = movies.copy()
    df["year"] = df["title"].apply(extract_year)
    df["genres_list"] = df["genres"].apply(parse_genres)

    agg = ratings.groupby("movieId")["rating"].agg(
        avg_rating="mean", num_ratings="count"
    ).reset_index()
    agg["avg_rating"] = agg["avg_rating"].astype("float32")
    agg["num_ratings"] = agg["num_ratings"].astype("int32")

    df = df.merge(agg, on="movieId", how="left")
    df["avg_rating"] = df["avg_rating"].fillna(0.0)
    df["num_ratings"] = df["num_ratings"].fillna(0).astype("int32")
    return df


def time_split(
    ratings: pd.DataFrame, train_ratio: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split ratings by timestamp (temporal split).

    Args:
        ratings: Ratings DataFrame with 'timestamp' column.
        train_ratio: Fraction of oldest ratings used for training.

    Returns:
        (train_df, test_df) tuple.
    """
    df = ratings.sort_values("timestamp").reset_index(drop=True)
    split_idx = int(len(df) * train_ratio)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    logger.info(
        f"Time split: {len(train_df):,} train ratings, {len(test_df):,} test ratings"
    )
    return train_df, test_df


def create_surprise_dataset(ratings_df: pd.DataFrame) -> tuple:
    """
    Convert pandas DataFrame to Surprise trainset and testset.

    Args:
        ratings_df: DataFrame with columns userId, movieId, rating.

    Returns:
        (trainset, testset_as_list) where testset is list of (uid, iid, rating).
    """
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(
        ratings_df[["userId", "movieId", "rating"]], reader
    )
    trainset = data.build_full_trainset()
    testset = trainset.build_testset()
    logger.info(
        f"Surprise dataset: {trainset.n_users} users, {trainset.n_items} items"
    )
    return trainset, testset


def get_popular_movies(movies: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    """
    Return the top-N most popular movies by weighted score.

    Popularity score = avg_rating * log(num_ratings).
    Only considers movies with num_ratings >= 100.

    Args:
        movies: Enriched movies DataFrame.
        n: Number of top movies to return.

    Returns:
        DataFrame [movieId, title, genres, avg_rating, num_ratings].
    """
    df = movies[movies["num_ratings"] >= 100].copy()
    df["pop_score"] = df["avg_rating"] * np.log1p(df["num_ratings"])
    df = df.sort_values("pop_score", ascending=False).head(n)
    cols = [c for c in ["movieId", "title", "genres", "avg_rating", "num_ratings"] if c in df.columns]
    return df[cols].reset_index(drop=True)


def get_movies_by_genre(movies: pd.DataFrame, genre: str) -> pd.DataFrame:
    """
    Filter movies by genre (case-insensitive, partial match).

    Args:
        movies: Movies DataFrame with 'genres' column.
        genre: Genre string to filter by.

    Returns:
        Filtered movies DataFrame.
    """
    mask = movies["genres"].str.contains(genre, case=False, na=False)
    return movies[mask].copy()


def get_all_genres(movies: pd.DataFrame) -> list[str]:
    """
    Return all unique genres in the dataset, sorted alphabetically.

    Args:
        movies: Movies DataFrame with 'genres' column.

    Returns:
        Sorted list of unique genre strings.
    """
    all_genres: set[str] = set()
    for genres_str in movies["genres"].dropna():
        for g in parse_genres(str(genres_str)):
            all_genres.add(g)
    return sorted(all_genres)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from src.data.loader import load_ratings, load_movies, sample_data

    ratings = sample_data(load_ratings(), n_users=500)
    movies = load_movies()
    ratings = filter_sparse(ratings)
    movies = enrich_movies(movies, ratings)
    train, test = time_split(ratings)
    trainset, testset = create_surprise_dataset(train)
    popular = get_popular_movies(movies, n=10)
    print(popular[["title", "avg_rating", "num_ratings"]])
    print("Genres:", get_all_genres(movies)[:10])
