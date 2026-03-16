"""
Data loader module for NexConflict Movie Recommender.
Handles loading raw CSV data from the MovieLens dataset.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_N_USERS: int = 5000
DEFAULT_SEED: int = 42

RATINGS_DTYPE: dict = {
    "userId": "int32",
    "movieId": "int32",
    "rating": "float32",
    "timestamp": "int64",
}

MOVIES_DTYPE: dict = {
    "movieId": "int32",
    "title": "str",
    "genres": "str",
}


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def get_data_dir() -> Path:
    """Return the path to the data/ directory (sibling of src/)."""
    return Path(__file__).resolve().parents[2] / "data"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_ratings(data_dir: Path | None = None) -> pd.DataFrame:
    """
    Load rating.csv from *data_dir*.

    Columns returned: userId (int32), movieId (int32),
                      rating (float32), timestamp (int64).

    Args:
        data_dir: Path to the directory containing rating.csv.
                  Defaults to ``get_data_dir()``.

    Returns:
        pd.DataFrame with the ratings data.
    """
    if data_dir is None:
        data_dir = get_data_dir()

    csv_path = Path(data_dir) / "rating.csv"
    logger.info("Loading ratings from %s", csv_path)

    df = pd.read_csv(
        csv_path,
        dtype=RATINGS_DTYPE,
    )

    logger.info("Loaded %d rating rows", len(df))
    return df


def load_movies(data_dir: Path | None = None) -> pd.DataFrame:
    """
    Load movie.csv from *data_dir*.

    Columns returned: movieId (int32), title (str), genres (str).
    genres format: "Action|Comedy|Drama" (pipe-separated).

    Args:
        data_dir: Path to the directory containing movie.csv.
                  Defaults to ``get_data_dir()``.

    Returns:
        pd.DataFrame with the movies data.
    """
    if data_dir is None:
        data_dir = get_data_dir()

    csv_path = Path(data_dir) / "movie.csv"
    logger.info("Loading movies from %s", csv_path)

    df = pd.read_csv(csv_path)
    df["movieId"] = df["movieId"].astype("int32")

    logger.info("Loaded %d movie rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_data(
    ratings: pd.DataFrame,
    n_users: int = DEFAULT_N_USERS,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Randomly sample *n_users* users and keep all of their ratings.

    Args:
        ratings: Full ratings DataFrame.
        n_users: Number of users to sample.
        seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame containing only ratings from the sampled users.
    """
    unique_users = ratings["userId"].unique()
    n_before = len(unique_users)
    n_ratings_before = len(ratings)

    if n_users >= n_before:
        logger.info(
            "Requested %d users but only %d available — returning full dataset",
            n_users,
            n_before,
        )
        return ratings.copy()

    rng = np.random.default_rng(seed)
    sampled_users = rng.choice(unique_users, size=n_users, replace=False)
    sampled = ratings[ratings["userId"].isin(sampled_users)].reset_index(drop=True)

    logger.info(
        "Sampled %d/%d users — ratings: %d → %d",
        n_users,
        n_before,
        n_ratings_before,
        len(sampled),
    )
    return sampled


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def get_stats(ratings: pd.DataFrame, movies: pd.DataFrame) -> dict:
    """
    Compute basic dataset statistics.

    Args:
        ratings: Ratings DataFrame (userId, movieId, rating, …).
        movies:  Movies DataFrame (movieId, title, genres, …).

    Returns:
        dict with keys:
            n_users, n_items, n_ratings, sparsity,
            avg_ratings_per_user, avg_ratings_per_item,
            rating_distribution
    """
    n_users = ratings["userId"].nunique()
    n_items = ratings["movieId"].nunique()
    n_ratings = len(ratings)

    sparsity = 1.0 - n_ratings / (n_users * n_items)

    avg_ratings_per_user = n_ratings / n_users if n_users else 0.0
    avg_ratings_per_item = n_ratings / n_items if n_items else 0.0

    rating_distribution = (
        ratings["rating"].value_counts().sort_index().to_dict()
    )

    return {
        "n_users": n_users,
        "n_items": n_items,
        "n_ratings": n_ratings,
        "sparsity": sparsity,
        "avg_ratings_per_user": avg_ratings_per_user,
        "avg_ratings_per_item": avg_ratings_per_item,
        "rating_distribution": rating_distribution,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    data_dir = get_data_dir()
    logger.info("Data directory: %s", data_dir)

    ratings = load_ratings(data_dir)
    movies = load_movies(data_dir)

    sampled = sample_data(ratings)

    stats = get_stats(sampled, movies)
    for key, value in stats.items():
        if key != "rating_distribution":
            logger.info("  %s = %s", key, value)
    logger.info("  rating_distribution = %s", stats["rating_distribution"])
