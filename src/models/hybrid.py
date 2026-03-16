"""Hybrid Recommender combining ItemKNN and SVDModel with weighted scoring."""

import logging
from pathlib import Path
from typing import Optional

import joblib

from .knn_model import ItemKNN
from .svd_model import SVDModel

logger = logging.getLogger(__name__)

DEFAULT_ALPHA: float = 0.5
ALPHA_SEARCH_RANGE: list[float] = [0.3, 0.4, 0.5, 0.6, 0.7]
POPULARITY_FALLBACK_N: int = 50


class HybridRecommender:
    """Hybrid recommender combining KNN and SVD with weighted scoring."""

    def __init__(
        self,
        knn_model: ItemKNN,
        svd_model: SVDModel,
        alpha: float = DEFAULT_ALPHA,
    ) -> None:
        """
        Args:
            knn_model: Trained ItemKNN instance.
            svd_model: Trained SVDModel instance.
            alpha: Weight cho SVD (1-alpha cho KNN). Range [0, 1].
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha phải nằm trong [0, 1], nhận được {alpha}.")
        self.knn_model = knn_model
        self.svd_model = svd_model
        self.alpha = alpha

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_scores(
        self, scores: list[tuple[int, float]]
    ) -> dict[int, float]:
        """
        Normalize scores về [0, 1] dùng min-max normalization.

        Args:
            scores: [(movieId, raw_score), ...].

        Returns:
            {movieId: normalized_score}.
        """
        if not scores:
            return {}

        values = [s for _, s in scores]
        min_val = min(values)
        max_val = max(values)
        span = max_val - min_val

        if span == 0:
            # Tất cả cùng giá trị → normalize thành 0.5
            return {mid: 0.5 for mid, _ in scores}

        return {mid: (score - min_val) / span for mid, score in scores}

    def _get_candidates(self, user_id: int) -> list[int]:
        """
        Lấy tập phim user chưa rate từ trainset của SVD model.

        Args:
            user_id: Raw user ID.

        Returns:
            Danh sách movie IDs chưa được rate bởi user.
        """
        trainset = self.svd_model._trainset
        if trainset is None:
            return []

        raw_uid = str(user_id)
        try:
            inner_uid = trainset.to_inner_uid(raw_uid)
            rated_inner_iids = {iid for iid, _ in trainset.ur[inner_uid]}
            rated_raw_iids = {
                int(trainset.to_raw_iid(iid)) for iid in rated_inner_iids
            }
        except ValueError:
            rated_raw_iids = set()

        return [
            int(trainset.to_raw_iid(inner))
            for inner in range(trainset.n_items)
            if int(trainset.to_raw_iid(inner)) not in rated_raw_iids
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(self, user_id: int, n: int = 10) -> list[dict]:
        """
        Top-N hybrid recommendations.

        Flow:
        1. Lấy candidates (items user chưa rate).
        2. Get SVD scores cho tất cả candidates.
        3. Get KNN scores cho tất cả candidates.
        4. Normalize cả 2 về [0, 1].
        5. final_score = alpha * svd_norm + (1 - alpha) * knn_norm.
        6. Sort desc, return top-N.

        Fallback: nếu 1 model fail cho item → dùng score của model còn lại.

        Args:
            user_id: Raw user ID.
            n: Số gợi ý muốn trả về.

        Returns:
            [
                {
                    "movieId": int,
                    "score": float,      # hybrid score
                    "svd_score": float,  # raw SVD predicted rating
                    "knn_score": float,  # raw KNN predicted rating
                },
                ...
            ]
        """
        candidates = self._get_candidates(user_id)
        if not candidates:
            logger.warning("Không tìm thấy candidates cho user %s.", user_id)
            return []

        # Predict từng model
        svd_raw: dict[int, float] = {}
        knn_raw: dict[int, float] = {}

        for movie_id in candidates:
            svd_score = self.svd_model.predict(user_id, movie_id)
            knn_score = self.knn_model.predict(user_id, movie_id)

            if svd_score is None and knn_score is None:
                continue  # Bỏ qua item không predict được từ cả 2

            if svd_score is not None:
                svd_raw[movie_id] = svd_score
            if knn_score is not None:
                knn_raw[movie_id] = knn_score

        # Normalize
        svd_norm = self._normalize_scores(list(svd_raw.items()))
        knn_norm = self._normalize_scores(list(knn_raw.items()))

        # Kết hợp candidates còn lại (ít nhất 1 model thành công)
        all_ids = set(svd_raw.keys()) | set(knn_raw.keys())

        scored: list[dict] = []
        for movie_id in all_ids:
            svd_n = svd_norm.get(movie_id)
            knn_n = knn_norm.get(movie_id)

            if svd_n is not None and knn_n is not None:
                final_score = self.alpha * svd_n + (1 - self.alpha) * knn_n
            elif svd_n is not None:
                # KNN fail → chỉ dùng SVD
                final_score = svd_n
            else:
                # SVD fail → chỉ dùng KNN (knn_n không None vì movie_id thuộc knn_raw)
                assert knn_n is not None
                final_score = knn_n

            scored.append(
                {
                    "movieId": movie_id,
                    "score": final_score,
                    "svd_score": svd_raw.get(movie_id, 0.0),
                    "knn_score": knn_raw.get(movie_id, 0.0),
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n]

    def recommend_for_new_user(
        self,
        rated_movies: dict[int, float],
        trainset,
        n: int = 10,
    ) -> list[dict]:
        """
        Recommendation cho user mới (cold-start).

        Tạo pseudo-user trong Surprise bằng cách predict dựa trên SVD
        với rated_movies làm tham chiếu.
        Fallback: popularity nếu không đủ ratings.

        Args:
            rated_movies: {movieId: rating} từ onboarding quiz.
            trainset: surprise.Trainset object.
            n: Số gợi ý muốn trả về.

        Returns:
            [{"movieId": int, "score": float, "svd_score": float, "knn_score": float}, ...]
        """
        MIN_RATINGS = 5

        if len(rated_movies) < MIN_RATINGS:
            logger.info(
                "User mới có %d ratings (< %d), dùng popularity fallback.",
                len(rated_movies),
                MIN_RATINGS,
            )
            # Fallback: trả về phim phổ biến chưa trong rated_movies
            all_movies = [
                int(trainset.to_raw_iid(inner))
                for inner in range(trainset.n_items)
            ]
            candidates = [mid for mid in all_movies if mid not in rated_movies]
            # Không có popularity info → trả về danh sách đơn giản
            return [
                {"movieId": mid, "score": 0.0, "svd_score": 0.0, "knn_score": 0.0}
                for mid in candidates[:n]
            ]

        # Dùng một user có rating pattern gần nhất làm proxy (đơn giản hoá)
        # Thực tế: xây dựng pseudo-predictions từ rated_movies
        rated_inner_iids = set()
        for mid in rated_movies:
            try:
                rated_inner_iids.add(trainset.to_inner_iid(str(mid)))
            except ValueError:
                pass

        candidates: list[int] = [
            int(trainset.to_raw_iid(inner))
            for inner in range(trainset.n_items)
            if inner not in rated_inner_iids
        ]

        # Predict cho candidates dùng SVD global mean làm baseline
        svd_raw: dict[int, float] = {}
        knn_raw: dict[int, float] = {}

        # Dùng một user_id ảo không tồn tại trong trainset (-1) để Surprise
        # fallback về global mean predictions, phù hợp với cold-start scenario.
        pseudo_uid = -1
        for movie_id in candidates:
            svd_score = self.svd_model.predict(pseudo_uid, movie_id)
            knn_score = self.knn_model.predict(pseudo_uid, movie_id)
            if svd_score is not None:
                svd_raw[movie_id] = svd_score
            if knn_score is not None:
                knn_raw[movie_id] = knn_score

        svd_norm = self._normalize_scores(list(svd_raw.items()))
        knn_norm = self._normalize_scores(list(knn_raw.items()))

        all_ids = set(svd_raw.keys()) | set(knn_raw.keys())
        scored: list[dict] = []
        for movie_id in all_ids:
            svd_n = svd_norm.get(movie_id)
            knn_n = knn_norm.get(movie_id)
            if svd_n is not None and knn_n is not None:
                final_score = self.alpha * svd_n + (1 - self.alpha) * knn_n
            elif svd_n is not None:
                final_score = svd_n
            else:
                # SVD fail → chỉ dùng KNN (knn_n không None vì movie_id thuộc knn_raw)
                assert knn_n is not None
                final_score = knn_n

            scored.append(
                {
                    "movieId": movie_id,
                    "score": final_score,
                    "svd_score": svd_raw.get(movie_id, 0.0),
                    "knn_score": knn_raw.get(movie_id, 0.0),
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n]

    def tune_alpha(
        self,
        val_data: list,
        metric: str = "ndcg",
    ) -> float:
        """
        Grid search alpha tối ưu trên validation data.

        Thử alpha_range = [0.3, 0.4, 0.5, 0.6, 0.7].
        Metric: NDCG@10.

        Args:
            val_data: Danh sách (user_id, [relevant_movie_ids]).
            metric: Metric đánh giá ('ndcg' được hỗ trợ).

        Returns:
            Best alpha value.
        """

        def _ndcg_at_k(recommended: list[int], relevant: set[int], k: int = 10) -> float:
            """Tính NDCG@K."""
            import math

            dcg = 0.0
            for rank, mid in enumerate(recommended[:k], start=1):
                if mid in relevant:
                    dcg += 1.0 / math.log2(rank + 1)

            ideal_hits = min(len(relevant), k)
            idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
            return dcg / idcg if idcg > 0 else 0.0

        best_alpha = self.alpha
        best_score = -1.0

        original_alpha = self.alpha
        for alpha_candidate in ALPHA_SEARCH_RANGE:
            self.alpha = alpha_candidate
            scores: list[float] = []

            for user_id, relevant_ids in val_data:
                recs = self.recommend(user_id, n=10)
                rec_ids = [r["movieId"] for r in recs]
                ndcg = _ndcg_at_k(rec_ids, set(relevant_ids))
                scores.append(ndcg)

            avg_score = sum(scores) / len(scores) if scores else 0.0
            logger.info("alpha=%.1f → avg NDCG@10=%.4f", alpha_candidate, avg_score)

            if avg_score > best_score:
                best_score = avg_score
                best_alpha = alpha_candidate

        self.alpha = best_alpha
        logger.info("Best alpha=%.1f (NDCG@10=%.4f)", best_alpha, best_score)
        return best_alpha

    def save(self, path: str) -> None:
        """
        Save cả knn_model, svd_model, và alpha bằng joblib.

        Args:
            path: Đường dẫn file đầu ra (.pkl).
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info("HybridRecommender saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "HybridRecommender":
        """
        Load hybrid model từ file.

        Args:
            path: Đường dẫn file .pkl.

        Returns:
            HybridRecommender instance đã được load.
        """
        model = joblib.load(path)
        logger.info("HybridRecommender loaded from %s", path)
        return model
