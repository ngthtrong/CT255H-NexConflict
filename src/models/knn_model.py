"""Item-based KNN Collaborative Filtering model using scikit-surprise."""

import logging
import time
from pathlib import Path
from typing import Optional

import joblib
from surprise import KNNBaseline, PredictionImpossible

logger = logging.getLogger(__name__)

DEFAULT_K: int = 30
DEFAULT_SIM_NAME: str = "cosine"
DEFAULT_MIN_SUPPORT: int = 10


class ItemKNN:
    """Item-based KNN Collaborative Filtering using Surprise library."""

    def __init__(
        self,
        k: int = DEFAULT_K,
        sim_name: str = DEFAULT_SIM_NAME,
        min_support: int = DEFAULT_MIN_SUPPORT,
    ) -> None:
        """
        Args:
            k: Số neighbors.
            sim_name: 'cosine' hoặc 'pearson'.
            min_support: Số common users tối thiểu để tính similarity.
        """
        self.k = k
        self.sim_name = sim_name
        self.min_support = min_support
        self.algo: Optional[KNNBaseline] = None
        self._trainset = None

    def train(self, trainset) -> None:
        """
        Fit model trên trainset.

        Sử dụng KNNBaseline với item-based cosine/pearson similarity.
        Lưu trainset reference để dùng cho recommend.

        Args:
            trainset: surprise.Trainset object.
        """
        sim_options = {
            "name": self.sim_name,
            "user_based": False,
            "min_support": self.min_support,
        }
        self.algo = KNNBaseline(k=self.k, sim_options=sim_options)
        self._trainset = trainset

        logger.info(
            "Training ItemKNN (k=%d, sim=%s, min_support=%d)...",
            self.k,
            self.sim_name,
            self.min_support,
        )
        start = time.time()
        self.algo.fit(trainset)
        elapsed = time.time() - start
        logger.info("ItemKNN training completed in %.2f seconds.", elapsed)

    def predict(self, user_id: int, movie_id: int) -> Optional[float]:
        """
        Dự đoán rating cho 1 cặp (user, movie).

        Args:
            user_id: Raw user ID.
            movie_id: Raw movie ID.

        Returns:
            Predicted rating (float) hoặc None nếu user/item unknown.
        """
        if self.algo is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")
        try:
            pred = self.algo.predict(str(user_id), str(movie_id))
            return pred.est
        except PredictionImpossible:
            logger.debug("PredictionImpossible cho user=%s, movie=%s", user_id, movie_id)
            return None

    def get_neighbors(self, movie_id: int, k: int = 10) -> list[tuple[int, float]]:
        """
        Tìm k phim tương tự nhất với movie_id.

        Dùng algo.get_neighbors() của Surprise và convert inner_id ↔ raw_id.

        Args:
            movie_id: Raw movie ID.
            k: Số neighbors muốn lấy.

        Returns:
            [(movieId, similarity_score), ...] sorted by similarity desc.
        """
        if self.algo is None or self._trainset is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")

        try:
            inner_iid = self._trainset.to_inner_iid(str(movie_id))
        except ValueError:
            logger.warning("Movie ID %s không có trong trainset.", movie_id)
            return []

        neighbor_inner_ids = self.algo.get_neighbors(inner_iid, k=k)
        sim_matrix = self.algo.sim

        results: list[tuple[int, float]] = []
        for neighbor_inner in neighbor_inner_ids:
            raw_iid = self._trainset.to_raw_iid(neighbor_inner)
            sim_score = float(sim_matrix[inner_iid][neighbor_inner])
            results.append((int(raw_iid), sim_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def recommend(
        self,
        user_id: int,
        n: int = 10,
        candidate_ids: Optional[list[int]] = None,
    ) -> list[tuple[int, float]]:
        """
        Top-N recommendations cho user.

        Lấy tất cả items user chưa rate (hoặc từ candidate_ids),
        predict rating và trả về top-N.

        Args:
            user_id: Raw user ID.
            n: Số gợi ý muốn trả về.
            candidate_ids: Danh sách movie IDs để lọc (nếu None → dùng tất cả).

        Returns:
            [(movieId, predicted_rating), ...] sorted desc.
        """
        if self.algo is None or self._trainset is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")

        raw_uid = str(user_id)

        # Lấy tập phim user đã rate
        try:
            inner_uid = self._trainset.to_inner_uid(raw_uid)
            rated_inner_iids = set(
                iid for iid, _ in self._trainset.ur[inner_uid]
            )
            rated_raw_iids = {
                int(self._trainset.to_raw_iid(iid)) for iid in rated_inner_iids
            }
        except ValueError:
            rated_raw_iids = set()

        # Chọn candidates
        if candidate_ids is not None:
            candidates = [mid for mid in candidate_ids if mid not in rated_raw_iids]
        else:
            candidates = [
                int(self._trainset.to_raw_iid(inner))
                for inner in range(self._trainset.n_items)
                if int(self._trainset.to_raw_iid(inner)) not in rated_raw_iids
            ]

        predictions: list[tuple[int, float]] = []
        for movie_id in candidates:
            score = self.predict(user_id, movie_id)
            if score is not None:
                predictions.append((movie_id, score))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def save(self, path: str) -> None:
        """
        Serialize model bằng joblib.

        Args:
            path: Đường dẫn file đầu ra (.pkl).
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info("ItemKNN model saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "ItemKNN":
        """
        Deserialize model từ file.

        Args:
            path: Đường dẫn file .pkl.

        Returns:
            ItemKNN instance đã được load.
        """
        model = joblib.load(path)
        logger.info("ItemKNN model loaded from %s", path)
        return model
