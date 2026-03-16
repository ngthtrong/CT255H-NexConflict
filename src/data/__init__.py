"""Data layer public API."""

from .loader import load_ratings, load_movies, sample_data, get_stats
from .preprocessor import (
    filter_sparse,
    enrich_movies,
    time_split,
    create_surprise_dataset,
    get_popular_movies,
    get_movies_by_genre,
    get_all_genres,
)

__all__ = [
    "load_ratings",
    "load_movies",
    "sample_data",
    "get_stats",
    "filter_sparse",
    "enrich_movies",
    "time_split",
    "create_surprise_dataset",
    "get_popular_movies",
    "get_movies_by_genre",
    "get_all_genres",
]
