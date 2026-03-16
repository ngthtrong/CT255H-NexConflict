"""
Explanation service for NexConflict Movie Recommender.
Generates human-readable explanations for recommendations.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

TEMPLATES = {
    "knn": "Vì bạn thích '{liked_movie}', phim này có pattern đánh giá tương tự (similarity: {sim:.0%})",
    "svd": "Dựa trên sở thích của bạn, model dự đoán bạn sẽ đánh giá phim này {rating:.1f}/5",
    "genre": "Phù hợp với thể loại yêu thích của bạn: {genres}",
    "popular": "Phim được đánh giá cao bởi {count} người dùng (avg: {avg:.1f}/5)",
}


class ExplainService:
    """Generates explanation text for each recommendation."""

    def __init__(self, knn_model, movies_info: pd.DataFrame):
        """
        Args:
            knn_model: Trained ItemKNN model (used for get_neighbors).
            movies_info: DataFrame with movie metadata.
        """
        self.knn_model = knn_model
        self.movies_info = movies_info
        self._title_map: dict[int, str] = {}
        if movies_info is not None and not movies_info.empty:
            self._title_map = dict(zip(movies_info["movieId"].astype(int), movies_info["title"]))

    def _get_title(self, movie_id: int) -> str:
        return self._title_map.get(movie_id, f"Phim #{movie_id}")

    def explain(
        self,
        user_id: int,
        movie_id: int,
        svd_score: float,
        knn_score: float,
        user_rated_movies: dict[int, float] = None,
        user_genres: list[str] = None,
    ) -> str:
        """
        Generate an explanation for a single recommendation.

        Chooses template based on which model contributed more.

        Args:
            user_id: Raw user ID.
            movie_id: Recommended movie ID.
            svd_score: SVD predicted rating.
            knn_score: KNN predicted rating.
            user_rated_movies: {movieId: rating} for movies the user has rated.
            user_genres: List of genres the user prefers.

        Returns:
            Explanation string in Vietnamese.
        """
        explanation = ""
        if knn_score >= svd_score and user_rated_movies:
            liked = {mid: r for mid, r in user_rated_movies.items() if r >= 3.5}
            if liked:
                neighbors = self.knn_model.get_neighbors(movie_id, k=20)
                best_match: tuple[int, float] | None = None
                for neighbor_id, sim in neighbors:
                    if neighbor_id in liked:
                        best_match = (neighbor_id, sim)
                        break
                if best_match:
                    liked_movie = self._get_title(best_match[0])
                    explanation = TEMPLATES["knn"].format(
                        liked_movie=liked_movie, sim=best_match[1]
                    )

        if not explanation:
            score = svd_score if svd_score > 0 else knn_score
            explanation = TEMPLATES["svd"].format(rating=score)

        if user_genres:
            row = self.movies_info[self.movies_info["movieId"] == movie_id]
            if not row.empty:
                genres_list = row.iloc[0].get("genres_list", [])
                matched = [g for g in genres_list if g in user_genres]
                if matched:
                    explanation += ". " + TEMPLATES["genre"].format(genres=", ".join(matched))

        return explanation

    def explain_popular(self, movie_id: int) -> str:
        """
        Generate explanation for a popularity-based recommendation.

        Args:
            movie_id: Movie ID.

        Returns:
            Explanation string in Vietnamese.
        """
        row = self.movies_info[self.movies_info["movieId"] == movie_id]
        if row.empty:
            return "Phim phổ biến trong hệ thống."
        count = int(row.iloc[0].get("num_ratings", 0))
        avg = float(row.iloc[0].get("avg_rating", 0.0))
        return TEMPLATES["popular"].format(count=count, avg=avg)
