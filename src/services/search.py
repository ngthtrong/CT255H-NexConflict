"""
Search service for NexConflict Movie Recommender.
Provides movie search and filtering functionality.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class SearchService:
    """Movie search and filter service."""

    def __init__(self, movies_info: pd.DataFrame):
        """
        Args:
            movies_info: DataFrame with columns:
                movieId, title, genres, year, avg_rating, num_ratings.
        """
        self.movies_info = movies_info.copy()

    def search_movies(
        self,
        query: str = "",
        genre: str = None,
        min_rating: float = None,
        limit: int = 20,
    ) -> pd.DataFrame:
        """
        Search and filter movies by multiple criteria.

        Args:
            query: Partial movie title (case-insensitive). "" returns all.
            genre: Filter by genre. None = no filter.
            min_rating: Minimum avg_rating threshold. None = no filter.
            limit: Maximum number of results.

        Returns:
            DataFrame with columns: title, year, genres, avg_rating, num_ratings,
            sorted by avg_rating descending.
        """
        df = self.movies_info.copy()

        if query:
            mask = df["title"].str.contains(query, case=False, na=False)
            df = df[mask]

        if genre:
            mask = df["genres"].str.contains(genre, case=False, na=False)
            df = df[mask]

        if min_rating is not None:
            df = df[df["avg_rating"] >= min_rating]

        df = df.sort_values("avg_rating", ascending=False).head(limit)

        display_cols = [c for c in ["title", "year", "genres", "avg_rating", "num_ratings"] if c in df.columns]
        return df[display_cols].reset_index(drop=True)

    def get_genre_options(self) -> list[str]:
        """
        Return list of genres for dropdown, with "Tất cả" prepended.

        Returns:
            List of genre strings.
        """
        all_genres: set[str] = set()
        for genres_str in self.movies_info["genres"].dropna():
            for g in str(genres_str).split("|"):
                g = g.strip()
                if g and g != "(no genres listed)":
                    all_genres.add(g)
        return ["Tất cả"] + sorted(all_genres)
