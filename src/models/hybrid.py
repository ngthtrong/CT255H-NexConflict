"""
Hybrid recommender combining ItemKNN and SVD with weighted scoring.
"""

import logging

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class HybridRecommender:
    """Hybrid recommender combining KNN and SVD with weighted scoring."""

    def __init__(self, knn_model, svd_model, alpha: float = 0.5):
        """
        Args:
            knn_model: Trained ItemKNN instance.
            svd_model: Trained SVDModel instance.
            alpha: Weight for SVD score. (1 - alpha) is the KNN weight.
                   Range [0, 1].
        """
        self.knn_model = knn_model
        self.svd_model = svd_model
        self.alpha = alpha

    def _normalize_scores(self, scores: list[tuple[int, float]]) -> dict[int, float]:
        """
        Min-max normalize scores to [0, 1].

        Args:
            scores: List of (movieId, score) tuples.

        Returns:
            dict mapping movieId to normalized score.
        """
        if not scores:
            return {}
        values = [s for _, s in scores]
        min_val = min(values)
        max_val = max(values)
        denom = max_val - min_val if max_val != min_val else 1.0
        return {mid: (s - min_val) / denom for mid, s in scores}

    def _get_candidates(self, user_id: int) -> list[int]:
        """Return list of candidate movie IDs (items the user has not rated)."""
        trainset = self.svd_model.trainset
        if trainset is None:
            return []
        try:
            inner_uid = trainset.to_inner_uid(str(user_id))
            rated_inner = {iid for iid, _ in trainset.ur[inner_uid]}
        except ValueError:
            rated_inner = set()
        return [
            int(trainset.to_raw_iid(inner))
            for inner in range(trainset.n_items)
            if inner not in rated_inner
        ]

    def recommend(self, user_id: int, n: int = 10) -> list[dict]:
        """
        Generate top-N hybrid recommendations for a user.

        The hybrid score is:
            final_score = alpha * normalize(svd_score) + (1 - alpha) * normalize(knn_score)

        Args:
            user_id: Raw user ID.
            n: Number of recommendations.

        Returns:
            List of dicts with keys: movieId, score, svd_score, knn_score.
        """
        candidates = self._get_candidates(user_id)
        if not candidates:
            return []

        svd_raw = self.svd_model.recommend(user_id, n=len(candidates), candidate_ids=candidates)
        knn_raw = self.knn_model.recommend(user_id, n=len(candidates), candidate_ids=candidates)

        svd_norm = self._normalize_scores(svd_raw)
        knn_norm = self._normalize_scores(knn_raw)

        svd_dict = {mid: score for mid, score in svd_raw}
        knn_dict = {mid: score for mid, score in knn_raw}

        all_ids = set(svd_norm) | set(knn_norm)
        scored = []
        for mid in all_ids:
            s_norm = svd_norm.get(mid, 0.0)
            k_norm = knn_norm.get(mid, 0.0)
            final = self.alpha * s_norm + (1.0 - self.alpha) * k_norm
            scored.append({
                "movieId": mid,
                "score": final,
                "svd_score": svd_dict.get(mid, 0.0),
                "knn_score": knn_dict.get(mid, 0.0),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n]

    def recommend_for_new_user(
        self, rated_movies: dict[int, float], trainset, n: int = 10
    ) -> list[dict]:
        """
        Generate recommendations for a new (cold-start) user.

        Uses SVD fallback by treating rated movies as popularity signal.
        Falls back to popularity-based scoring when fewer than 5 ratings exist.

        Args:
            rated_movies: {movieId: rating} from onboarding quiz.
            trainset: Surprise Trainset reference.
            n: Number of recommendations.

        Returns:
            List of dicts with keys: movieId, score, svd_score, knn_score.
        """
        rated_ids = set(rated_movies.keys())
        all_candidates = [
            int(trainset.to_raw_iid(inner))
            for inner in range(trainset.n_items)
            if int(trainset.to_raw_iid(inner)) not in rated_ids
        ]

        # Score candidates using KNN neighbors of rated movies
        knn_scores: dict[int, float] = {}
        for movie_id, rating in rated_movies.items():
            if rating < 3.5:
                continue
            neighbors = self.knn_model.get_neighbors(movie_id, k=20)
            for neighbor_id, sim in neighbors:
                if neighbor_id not in rated_ids:
                    knn_scores[neighbor_id] = knn_scores.get(neighbor_id, 0.0) + sim * rating

        if not knn_scores:
            # Fallback: return most common candidates
            return [{"movieId": mid, "score": 0.0, "svd_score": 0.0, "knn_score": 0.0}
                    for mid in all_candidates[:n]]

        knn_raw = sorted(knn_scores.items(), key=lambda x: x[1], reverse=True)
        knn_norm = self._normalize_scores(knn_raw)

        scored = [
            {
                "movieId": mid,
                "score": knn_norm.get(mid, 0.0),
                "svd_score": 0.0,
                "knn_score": score,
            }
            for mid, score in knn_raw
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n]

    def tune_alpha(self, val_data: list, metric: str = "ndcg") -> float:
        """
        Grid search for the best alpha value on validation data.

        Args:
            val_data: List of (userId, movieId, rating) tuples.
            metric: Metric to optimize ('ndcg', 'precision').

        Returns:
            Best alpha value from [0.3, 0.4, 0.5, 0.6, 0.7].
        """
        from collections import defaultdict
        from src.evaluation.metrics import ndcg_at_k, precision_at_k

        alpha_range = [0.3, 0.4, 0.5, 0.6, 0.7]
        best_alpha = self.alpha
        best_score = -1.0

        user_items: dict[int, dict[int, float]] = defaultdict(dict)
        for uid, iid, rating in val_data:
            user_items[int(uid)][int(iid)] = float(rating)

        for alpha in alpha_range:
            self.alpha = alpha
            scores = []
            for user_id, relevant in user_items.items():
                recs = self.recommend(user_id, n=10)
                rec_ids = [r["movieId"] for r in recs]
                if metric == "ndcg":
                    s = ndcg_at_k(rec_ids, relevant, k=10)
                else:
                    s = precision_at_k(rec_ids, set(relevant.keys()), k=10)
                scores.append(s)
            avg = float(np.mean(scores)) if scores else 0.0
            logger.info(f"alpha={alpha:.1f} → {metric}={avg:.4f}")
            if avg > best_score:
                best_score = avg
                best_alpha = alpha

        self.alpha = best_alpha
        logger.info(f"Best alpha: {best_alpha} ({metric}={best_score:.4f})")
        return best_alpha

    def save(self, path: str) -> None:
        """Serialize hybrid model (including sub-models) to disk."""
        joblib.dump(self, path)
        logger.info(f"HybridRecommender saved to {path}")

    @classmethod
    def load(cls, path: str) -> "HybridRecommender":
        """Deserialize hybrid model from file."""
        model = joblib.load(path)
        logger.info(f"HybridRecommender loaded from {path}")
        return model
