"""
Data loader module for NexConflict Movie Recommender.
Loads raw CSV data from the MovieLens dataset.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def get_data_dir() -> Path:
    """Return the path to the data/ directory."""
    return Path(__file__).resolve().parents[2] / "data"


def load_ratings(data_dir: Path = None) -> pd.DataFrame:
    """
    Load rating.csv from the data directory.

    Args:
        data_dir: Path to data directory. Defaults to project data/.

    Returns:
        pd.DataFrame with columns: userId(int32), movieId(int32),
        rating(float32), timestamp(int64).
    """
    if data_dir is None:
        data_dir = get_data_dir()
    path = Path(data_dir) / "rating.csv"
    logger.info(f"Loading ratings from {path}")
    df = pd.read_csv(path, dtype={
        "userId": "int32",
        "movieId": "int32",
        "rating": "float32",
        "timestamp": "int64",
    })
    logger.info(f"Loaded {len(df):,} ratings")
    return df


def load_movies(data_dir: Path = None) -> pd.DataFrame:
    """
    Load movie.csv from the data directory.

    Args:
        data_dir: Path to data directory. Defaults to project data/.

    Returns:
        pd.DataFrame with columns: movieId(int32), title(str), genres(str).
        genres is pipe-separated, e.g. "Action|Comedy|Drama".
    """
    if data_dir is None:
        data_dir = get_data_dir()
    path = Path(data_dir) / "movie.csv"
    logger.info(f"Loading movies from {path}")
    df = pd.read_csv(path, dtype={"movieId": "int32"})
    logger.info(f"Loaded {len(df):,} movies")
    return df


def sample_data(ratings: pd.DataFrame, n_users: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Randomly sample n_users users and keep all their ratings.

    Args:
        ratings: Full ratings DataFrame.
        n_users: Number of users to sample.
        seed: Random seed for reproducibility.

    Returns:
        Sampled ratings DataFrame.
    """
    all_users = ratings["userId"].unique()
    logger.info(f"Sampling {n_users} users from {len(all_users):,} total users")
    if n_users >= len(all_users):
        logger.info("n_users >= total users, returning full dataset")
        return ratings.copy()
    rng = __import__("numpy").random.default_rng(seed)
    sampled_users = rng.choice(all_users, size=n_users, replace=False)
    sampled = ratings[ratings["userId"].isin(sampled_users)].copy()
    logger.info(
        f"After sampling: {sampled['userId'].nunique():,} users, {len(sampled):,} ratings"
    )
    return sampled


def get_stats(ratings: pd.DataFrame, movies: pd.DataFrame) -> dict:
    """
    Compute basic statistics about the ratings dataset.

    Args:
        ratings: Ratings DataFrame.
        movies: Movies DataFrame.

    Returns:
        dict with keys: n_users, n_items, n_ratings, sparsity,
        avg_ratings_per_user, avg_ratings_per_item, rating_distribution.
    """
    n_users = ratings["userId"].nunique()
    n_items = ratings["movieId"].nunique()
    n_ratings = len(ratings)
    sparsity = 1.0 - n_ratings / (n_users * n_items) if n_users * n_items > 0 else 1.0
    avg_ratings_per_user = n_ratings / n_users if n_users > 0 else 0.0
    avg_ratings_per_item = n_ratings / n_items if n_items > 0 else 0.0
    rating_distribution = ratings["rating"].value_counts().sort_index().to_dict()
    return {
        "n_users": n_users,
        "n_items": n_items,
        "n_ratings": n_ratings,
        "sparsity": sparsity,
        "avg_ratings_per_user": avg_ratings_per_user,
        "avg_ratings_per_item": avg_ratings_per_item,
        "rating_distribution": rating_distribution,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ratings = load_ratings()
    movies = load_movies()
    sampled = sample_data(ratings, n_users=1000)
    stats = get_stats(sampled, movies)
    print(stats)
