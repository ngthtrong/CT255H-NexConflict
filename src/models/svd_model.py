"""SVD Matrix Factorization model using scikit-surprise."""

import logging
import time
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from surprise import SVD, PredictionImpossible

logger = logging.getLogger(__name__)

DEFAULT_N_FACTORS: int = 100
DEFAULT_N_EPOCHS: int = 20
DEFAULT_LR_ALL: float = 0.005
DEFAULT_REG_ALL: float = 0.02


class SVDModel:
    """SVD Matrix Factorization using Surprise library."""

    def __init__(
        self,
        n_factors: int = DEFAULT_N_FACTORS,
        n_epochs: int = DEFAULT_N_EPOCHS,
        lr_all: float = DEFAULT_LR_ALL,
        reg_all: float = DEFAULT_REG_ALL,
    ) -> None:
        """
        Args:
            n_factors: Số latent factors.
            n_epochs: Số epochs training.
            lr_all: Learning rate.
            reg_all: Regularization term.
        """
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr_all = lr_all
        self.reg_all = reg_all
        self.algo: Optional[SVD] = None
        self._trainset = None

    def train(self, trainset) -> None:
        """
        Fit SVD model.

        Args:
            trainset: surprise.Trainset object.
        """
        self.algo = SVD(
            n_factors=self.n_factors,
            n_epochs=self.n_epochs,
            lr_all=self.lr_all,
            reg_all=self.reg_all,
        )
        self._trainset = trainset

        logger.info(
            "Training SVD (n_factors=%d, n_epochs=%d, lr_all=%.4f, reg_all=%.4f)...",
            self.n_factors,
            self.n_epochs,
            self.lr_all,
            self.reg_all,
        )
        start = time.time()
        self.algo.fit(trainset)
        elapsed = time.time() - start
        logger.info(
            "SVD training completed in %.2f seconds (n_factors=%d).",
            elapsed,
            self.n_factors,
        )

    def predict(self, user_id: int, movie_id: int) -> Optional[float]:
        """
        Dự đoán rating cho 1 cặp (user, movie).

        Args:
            user_id: Raw user ID.
            movie_id: Raw movie ID.

        Returns:
            Predicted rating (float) hoặc None nếu unknown.
        """
        if self.algo is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")
        try:
            pred = self.algo.predict(str(user_id), str(movie_id))
            return pred.est
        except PredictionImpossible:
            logger.debug("PredictionImpossible cho user=%s, movie=%s", user_id, movie_id)
            return None

    def recommend(
        self,
        user_id: int,
        n: int = 10,
        candidate_ids: Optional[list[int]] = None,
    ) -> list[tuple[int, float]]:
        """
        Top-N recommendations cho user.

        Predict cho tất cả items user chưa rate (hoặc từ candidate_ids),
        sort và return top-N.

        Args:
            user_id: Raw user ID.
            n: Số gợi ý muốn trả về.
            candidate_ids: Danh sách movie IDs (nếu None → dùng tất cả).

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

    def get_user_factors(self, user_id: int) -> Optional[np.ndarray]:
        """
        Trả về latent vector của user (cho explanation).

        Args:
            user_id: Raw user ID.

        Returns:
            numpy array của latent factors, hoặc None nếu user không tồn tại.
        """
        if self.algo is None or self._trainset is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")
        try:
            inner_uid = self._trainset.to_inner_uid(str(user_id))
            return self.algo.pu[inner_uid]
        except ValueError:
            logger.warning("User ID %s không có trong trainset.", user_id)
            return None

    def get_item_factors(self, movie_id: int) -> Optional[np.ndarray]:
        """
        Trả về latent vector của item (cho explanation).

        Args:
            movie_id: Raw movie ID.

        Returns:
            numpy array của latent factors, hoặc None nếu item không tồn tại.
        """
        if self.algo is None or self._trainset is None:
            raise RuntimeError("Model chưa được train. Gọi train() trước.")
        try:
            inner_iid = self._trainset.to_inner_iid(str(movie_id))
            return self.algo.qi[inner_iid]
        except ValueError:
            logger.warning("Movie ID %s không có trong trainset.", movie_id)
            return None

    def save(self, path: str) -> None:
        """
        Serialize model bằng joblib.

        Args:
            path: Đường dẫn file đầu ra (.pkl).
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info("SVDModel saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "SVDModel":
        """
        Deserialize model từ file.

        Args:
            path: Đường dẫn file .pkl.

        Returns:
            SVDModel instance đã được load.
        """
        model = joblib.load(path)
        logger.info("SVDModel loaded from %s", path)
        return model
