"""
Item-based KNN collaborative filtering model using scikit-surprise.
"""

import logging
import time

import joblib
from surprise import KNNWithMeans, PredictionImpossible

logger = logging.getLogger(__name__)


class ItemKNN:
    """Item-based KNN Collaborative Filtering using Surprise library."""

    def __init__(self, k: int = 30, sim_name: str = "cosine", min_support: int = 10):
        """
        Args:
            k: Number of neighbors.
            sim_name: Similarity metric ('cosine' or 'pearson').
            min_support: Minimum number of common users to compute similarity.
        """
        self.k = k
        self.sim_name = sim_name
        self.min_support = min_support
        self.algo = None
        self.trainset = None

    def train(self, trainset) -> None:
        """
        Fit the KNN model on a Surprise Trainset.

        Args:
            trainset: surprise.Trainset object.
        """
        self.trainset = trainset
        sim_options = {
            "name": self.sim_name,
            "user_based": False,
            "min_support": self.min_support,
        }
        self.algo = KNNWithMeans(k=self.k, sim_options=sim_options)
        logger.info(f"Training ItemKNN (k={self.k}, sim={self.sim_name})...")
        t0 = time.time()
        self.algo.fit(trainset)
        logger.info(f"ItemKNN trained in {time.time() - t0:.1f}s")

    def predict(self, user_id: int, movie_id: int) -> float | None:
        """
        Predict rating for a (user, movie) pair.

        Args:
            user_id: Raw user ID.
            movie_id: Raw movie ID.

        Returns:
            Predicted rating as float, or None if prediction is impossible.
        """
        if self.algo is None:
            raise RuntimeError("Model not trained. Call train() first.")
        try:
            pred = self.algo.predict(str(user_id), str(movie_id))
            return pred.est
        except PredictionImpossible:
            return None

    def get_neighbors(self, movie_id: int, k: int = 10) -> list[tuple[int, float]]:
        """
        Find the k most similar movies to movie_id.

        Args:
            movie_id: Raw movie ID.
            k: Number of neighbors to return.

        Returns:
            List of (movieId, similarity_score) tuples sorted by similarity desc.
        """
        if self.algo is None or self.trainset is None:
            return []
        try:
            inner_iid = self.trainset.to_inner_iid(str(movie_id))
        except ValueError:
            return []
        neighbors = self.algo.get_neighbors(inner_iid, k=k)
        result = []
        for inner in neighbors:
            try:
                raw_id = int(self.trainset.to_raw_iid(inner))
                sim = self.algo.sim[inner_iid, inner]
                result.append((raw_id, float(sim)))
            except (ValueError, IndexError):
                continue
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def recommend(
        self, user_id: int, n: int = 10, candidate_ids: list[int] = None
    ) -> list[tuple[int, float]]:
        """
        Generate top-N recommendations for a user.

        Args:
            user_id: Raw user ID.
            n: Number of recommendations.
            candidate_ids: Optional list of candidate movie IDs to score.
                           If None, all unrated items are used.

        Returns:
            List of (movieId, predicted_rating) tuples sorted by rating desc.
        """
        if self.algo is None or self.trainset is None:
            return []
        try:
            inner_uid = self.trainset.to_inner_uid(str(user_id))
            rated_items = {iid for iid, _ in self.trainset.ur[inner_uid]}
        except ValueError:
            rated_items = set()

        if candidate_ids is not None:
            candidates = []
            for mid in candidate_ids:
                try:
                    inner = self.trainset.to_inner_iid(str(mid))
                    if inner not in rated_items:
                        candidates.append(str(mid))
                except ValueError:
                    candidates.append(str(mid))
        else:
            candidates = [
                self.trainset.to_raw_iid(inner)
                for inner in range(self.trainset.n_items)
                if inner not in rated_items
            ]

        predictions = []
        for raw_iid in candidates:
            try:
                pred = self.algo.predict(str(user_id), str(raw_iid))
                predictions.append((int(raw_iid), pred.est))
            except PredictionImpossible:
                continue

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def save(self, path: str) -> None:
        """Serialize model to disk using joblib."""
        joblib.dump(self, path)
        logger.info(f"ItemKNN saved to {path}")

    @classmethod
    def load(cls, path: str) -> "ItemKNN":
        """Deserialize model from file."""
        model = joblib.load(path)
        logger.info(f"ItemKNN loaded from {path}")
        return model
