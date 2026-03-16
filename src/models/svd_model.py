"""
SVD Matrix Factorization model using scikit-surprise.
"""

import logging
import time

import joblib
import numpy as np
from surprise import SVD, PredictionImpossible

logger = logging.getLogger(__name__)


class SVDModel:
    """SVD Matrix Factorization using Surprise library."""

    def __init__(
        self,
        n_factors: int = 100,
        n_epochs: int = 20,
        lr_all: float = 0.005,
        reg_all: float = 0.02,
    ):
        """
        Args:
            n_factors: Number of latent factors.
            n_epochs: Number of training epochs.
            lr_all: Learning rate for all parameters.
            reg_all: Regularization term for all parameters.
        """
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr_all = lr_all
        self.reg_all = reg_all
        self.algo = None
        self.trainset = None

    def train(self, trainset) -> None:
        """
        Fit the SVD model on a Surprise Trainset.

        Args:
            trainset: surprise.Trainset object.
        """
        self.trainset = trainset
        self.algo = SVD(
            n_factors=self.n_factors,
            n_epochs=self.n_epochs,
            lr_all=self.lr_all,
            reg_all=self.reg_all,
        )
        logger.info(f"Training SVD (n_factors={self.n_factors}, n_epochs={self.n_epochs})...")
        t0 = time.time()
        self.algo.fit(trainset)
        logger.info(f"SVD trained in {time.time() - t0:.1f}s")

    def predict(self, user_id: int, movie_id: int) -> float | None:
        """
        Predict rating for a (user, movie) pair.

        Args:
            user_id: Raw user ID.
            movie_id: Raw movie ID.

        Returns:
            Predicted rating, or None if unknown.
        """
        if self.algo is None:
            raise RuntimeError("Model not trained. Call train() first.")
        try:
            pred = self.algo.predict(str(user_id), str(movie_id))
            return pred.est
        except PredictionImpossible:
            return None

    def recommend(
        self, user_id: int, n: int = 10, candidate_ids: list[int] = None
    ) -> list[tuple[int, float]]:
        """
        Generate top-N recommendations for a user.

        Args:
            user_id: Raw user ID.
            n: Number of recommendations.
            candidate_ids: Optional list of candidate movie IDs.
                           If None, all unrated items are used.

        Returns:
            List of (movieId, predicted_rating) tuples sorted by rating desc.
        """
        if self.algo is None or self.trainset is None:
            return []
        try:
            inner_uid = self.trainset.to_inner_uid(str(user_id))
            rated_inner = {iid for iid, _ in self.trainset.ur[inner_uid]}
        except ValueError:
            rated_inner = set()

        if candidate_ids is not None:
            candidates = [str(mid) for mid in candidate_ids]
        else:
            candidates = []
            for inner in range(self.trainset.n_items):
                if inner not in rated_inner:
                    candidates.append(self.trainset.to_raw_iid(inner))

        predictions = []
        for raw_iid in candidates:
            try:
                pred = self.algo.predict(str(user_id), str(raw_iid))
                predictions.append((int(raw_iid), pred.est))
            except PredictionImpossible:
                continue

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def get_user_factors(self, user_id: int) -> np.ndarray | None:
        """
        Return the latent factor vector for a user.

        Args:
            user_id: Raw user ID.

        Returns:
            numpy array of shape (n_factors,), or None if unknown.
        """
        if self.algo is None or self.trainset is None:
            return None
        try:
            inner_uid = self.trainset.to_inner_uid(str(user_id))
            return self.algo.pu[inner_uid]
        except ValueError:
            return None

    def get_item_factors(self, movie_id: int) -> np.ndarray | None:
        """
        Return the latent factor vector for a movie.

        Args:
            movie_id: Raw movie ID.

        Returns:
            numpy array of shape (n_factors,), or None if unknown.
        """
        if self.algo is None or self.trainset is None:
            return None
        try:
            inner_iid = self.trainset.to_inner_iid(str(movie_id))
            return self.algo.qi[inner_iid]
        except ValueError:
            return None

    def save(self, path: str) -> None:
        """Serialize model to disk using joblib."""
        joblib.dump(self, path)
        logger.info(f"SVDModel saved to {path}")

    @classmethod
    def load(cls, path: str) -> "SVDModel":
        """Deserialize model from file."""
        model = joblib.load(path)
        logger.info(f"SVDModel loaded from {path}")
        return model
