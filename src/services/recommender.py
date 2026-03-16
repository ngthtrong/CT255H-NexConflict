"""
RecommenderService — singleton orchestrator for the NexConflict app.
Loads models and data once; exposes high-level recommendation methods.
"""

import logging
from pathlib import Path

import joblib
import pandas as pd

from src.models import ItemKNN, SVDModel, HybridRecommender
from src.services.explainer import ExplainService

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path("artifacts")


class RecommenderService:
    """
    Main service connecting the data and model layers.
    Implemented as a singleton — models are loaded once on first instantiation.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info("Initializing RecommenderService…")
        self._load_data()
        self._load_models()
        self._initialized = True
        logger.info("RecommenderService ready.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        """Load pre-computed data artifacts."""
        movies_path = ARTIFACTS_DIR / "movies_info.pkl"
        popular_path = ARTIFACTS_DIR / "popular_movies.pkl"
        trainset_path = ARTIFACTS_DIR / "trainset.pkl"

        if movies_path.exists():
            self.movies_info: pd.DataFrame = pd.read_pickle(movies_path)
        else:
            logger.warning("movies_info.pkl not found — using empty DataFrame")
            self.movies_info = pd.DataFrame(
                columns=["movieId", "title", "genres", "year", "avg_rating", "num_ratings", "genres_list"]
            )

        if popular_path.exists():
            self.popular_movies: pd.DataFrame = pd.read_pickle(popular_path)
        else:
            self.popular_movies = self.movies_info.copy()

        if trainset_path.exists():
            self.trainset = joblib.load(trainset_path)
        else:
            self.trainset = None
            logger.warning("trainset.pkl not found — new-user predictions unavailable")

        self.genre_list: list[str] = self._extract_genres()

    def _extract_genres(self) -> list[str]:
        all_genres: set[str] = set()
        for genres_str in self.movies_info.get("genres", pd.Series([], dtype=str)).dropna():
            for g in str(genres_str).split("|"):
                g = g.strip()
                if g and g != "(no genres listed)":
                    all_genres.add(g)
        return sorted(all_genres)

    def _load_models(self) -> None:
        """Load trained model artifacts."""
        knn_path = ARTIFACTS_DIR / "knn_model.pkl"
        svd_path = ARTIFACTS_DIR / "svd_model.pkl"
        hybrid_path = ARTIFACTS_DIR / "hybrid_model.pkl"

        self.knn: ItemKNN | None = ItemKNN.load(str(knn_path)) if knn_path.exists() else None
        self.svd: SVDModel | None = SVDModel.load(str(svd_path)) if svd_path.exists() else None
        self.hybrid: HybridRecommender | None = (
            HybridRecommender.load(str(hybrid_path)) if hybrid_path.exists() else None
        )
        if self.knn is None:
            logger.warning("knn_model.pkl not found")
        if self.svd is None:
            logger.warning("svd_model.pkl not found")
        if self.hybrid is None:
            logger.warning("hybrid_model.pkl not found")

        self.explainer = ExplainService(self.knn, self.movies_info)

    def _enrich_results(
        self,
        raw_results: list[dict],
        user_rated_movies: dict[int, float] = None,
        user_genres: list[str] = None,
    ) -> list[dict]:
        """Attach movie metadata and explanation to each raw result dict."""
        enriched = []
        for rank, item in enumerate(raw_results, start=1):
            mid = item["movieId"]
            row = self.movies_info[self.movies_info["movieId"] == mid]
            if row.empty:
                title = f"Phim #{mid}"
                genres_str = ""
            else:
                r = row.iloc[0]
                title = r.get("title", f"Phim #{mid}")
                genres_str = ", ".join(r.get("genres_list", [])) or r.get("genres", "")

            explanation = self.explainer.explain(
                user_id=-1,
                movie_id=mid,
                svd_score=item.get("svd_score", 0.0),
                knn_score=item.get("knn_score", 0.0),
                user_rated_movies=user_rated_movies,
                user_genres=user_genres,
            )
            enriched.append({
                "rank": rank,
                "title": title,
                "genres": genres_str,
                "predicted_rating": round(item.get("score", 0.0) * 5, 2),
                "explanation": explanation,
            })
        return enriched

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend_for_new_user(
        self, genres: list[str], ratings: dict[int, float], n: int = 10
    ) -> list[dict]:
        """
        Recommend movies for a new user (cold-start) based on quiz ratings.

        Args:
            genres: Selected genre preferences.
            ratings: {movieId: rating} from onboarding.
            n: Number of recommendations.

        Returns:
            List of recommendation dicts with rank, title, genres,
            predicted_rating, explanation.
        """
        if len(ratings) >= 5 and self.hybrid is not None and self.trainset is not None:
            try:
                raw = self.hybrid.recommend_for_new_user(ratings, self.trainset, n=n)
                return self._enrich_results(raw, user_rated_movies=ratings, user_genres=genres)
            except Exception as e:
                logger.warning(f"Hybrid new-user recommendation failed: {e}")

        # Fallback: popularity within selected genres
        logger.info("Using popularity fallback for new user")
        df = self.popular_movies.copy()
        if genres:
            mask = df["genres"].apply(
                lambda g: any(genre.lower() in str(g).lower() for genre in genres)
            )
            df = df[mask]
        df = df.head(n)
        results = []
        for rank, (_, row) in enumerate(df.iterrows(), start=1):
            mid = int(row["movieId"])
            explanation = self.explainer.explain_popular(mid)
            results.append({
                "rank": rank,
                "title": row.get("title", f"Phim #{mid}"),
                "genres": ", ".join(row.get("genres_list", [])) if isinstance(row.get("genres_list"), list) else row.get("genres", ""),
                "predicted_rating": round(float(row.get("avg_rating", 0.0)), 2),
                "explanation": explanation,
            })
        return results

    def recommend_for_user(self, user_id: int, n: int = 10) -> list[dict]:
        """
        Recommend movies for an existing user in the dataset.

        Args:
            user_id: Raw user ID.
            n: Number of recommendations.

        Returns:
            List of recommendation dicts.
        """
        if self.hybrid is None:
            return []
        try:
            raw = self.hybrid.recommend(user_id, n=n)
            return self._enrich_results(raw)
        except Exception as e:
            logger.error(f"recommend_for_user failed for user {user_id}: {e}")
            return []

    def get_movie_details(self, movie_id: int) -> dict | None:
        """Return metadata for a movie by ID."""
        row = self.movies_info[self.movies_info["movieId"] == movie_id]
        if row.empty:
            return None
        r = row.iloc[0]
        return {
            "movieId": movie_id,
            "title": r.get("title", ""),
            "genres": r.get("genres", ""),
            "year": r.get("year"),
            "avg_rating": r.get("avg_rating", 0.0),
            "num_ratings": r.get("num_ratings", 0),
        }

    def get_genres(self) -> list[str]:
        """Return the list of all genres in the dataset."""
        return self.genre_list

    def get_popular_movies_for_onboarding(
        self, genres: list[str] = None, n: int = 15
    ) -> pd.DataFrame:
        """
        Return popular movies for the onboarding quiz.

        Args:
            genres: If provided, filter movies to these genres.
            n: Number of movies to return.

        Returns:
            DataFrame [movieId, title, genres, avg_rating].
        """
        df = self.popular_movies.copy()
        if genres:
            mask = df["genres"].apply(
                lambda g: any(genre.lower() in str(g).lower() for genre in genres)
            )
            df = df[mask]
        cols = [c for c in ["movieId", "title", "genres", "avg_rating"] if c in df.columns]
        return df.head(n)[cols].reset_index(drop=True)

    def get_user_ids(self, limit: int = 100) -> list[int]:
        """Return a list of user IDs present in the trainset."""
        if self.trainset is None:
            return []
        raw_uids = [int(self.trainset.to_raw_uid(inner)) for inner in range(self.trainset.n_users)]
        return raw_uids[:limit]
