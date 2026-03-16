# AGENT 2: ML Models
# Vai trò: Xây dựng toàn bộ model layer (KNN, SVD, Hybrid)

## BỐI CẢNH DỰ ÁN
Ứng dụng gợi ý phim dùng Collaborative Filtering.
- Thư viện ML chính: scikit-surprise
- Thuật toán: Item-based KNN + SVD + Hybrid weighted
- Chi tiết thuật toán: docs/10-algorithm-detail.md
- Kiến trúc: docs/ARCHITECTURE.md

## PHỤ THUỘC
- **Phụ thuộc Agent 1**: Cần `src/data/` đã hoàn thành
- Input: `trainset` (surprise.Trainset), `testset` (list of tuples)
- Models serialize vào `artifacts/`

## NHIỆM VỤ
Tạo 4 file trong `src/models/`:
1. `src/models/__init__.py`
2. `src/models/knn_model.py`
3. `src/models/svd_model.py`
4. `src/models/hybrid.py`

## RÀNG BUỘC
- Dùng `scikit-surprise` cho KNN và SVD (KHÔNG implement từ scratch)
- Serialize models bằng `joblib` vào `artifacts/`
- Type hints và docstrings cho tất cả public methods
- Logging thông qua `logging` module
- Handle errors gracefully: unknown user/item → return None hoặc fallback
- Normalize scores về [0, 1] trước khi combine trong Hybrid

## FILE 1: src/models/knn_model.py

### Class ItemKNN:

```python
class ItemKNN:
    """Item-based KNN Collaborative Filtering using Surprise library."""

    def __init__(self, k: int = 30, sim_name: str = 'cosine', min_support: int = 10):
        """
        Args:
            k: Số neighbors
            sim_name: 'cosine' hoặc 'pearson'
            min_support: Số common users tối thiểu để tính similarity
        """

    def train(self, trainset) -> None:
        """
        Fit model trên trainset.
        - Dùng surprise.KNNBaseline hoặc KNNWithMeans
        - sim_options = {'name': sim_name, 'user_based': False, 'min_support': min_support}
        - Lưu trainset reference để dùng cho recommend
        - Log training time
        """

    def predict(self, user_id: int, movie_id: int) -> float | None:
        """
        Dự đoán rating cho 1 cặp (user, movie).
        - Return predicted rating (float)
        - Return None nếu user/item unknown
        """

    def get_neighbors(self, movie_id: int, k: int = 10) -> list[tuple[int, float]]:
        """
        Tìm k phim tương tự nhất với movie_id.
        - Dùng algo.get_neighbors() của Surprise
        - Convert inner_id ↔ raw_id
        Returns: [(movieId, similarity_score), ...] sorted by similarity desc
        """

    def recommend(self, user_id: int, n: int = 10, candidate_ids: list[int] = None) -> list[tuple[int, float]]:
        """
        Top-N recommendations cho user.
        - Lấy tất cả items mà user CHƯA rate (hoặc từ candidate_ids)
        - Predict rating cho mỗi item
        - Sort desc, return top-N
        Returns: [(movieId, predicted_rating), ...]
        """

    def save(self, path: str) -> None:
        """Serialize model bằng joblib"""

    @classmethod
    def load(cls, path: str) -> 'ItemKNN':
        """Deserialize model từ file"""
```

### Hyperparameters
| Parameter | Mặc định | Ghi chú |
|---|---|---|
| k | 30 | Số neighbors |
| sim_name | 'cosine' | Metric tương đồng |
| min_support | 10 | Min common users |

## FILE 2: src/models/svd_model.py

### Class SVDModel:

```python
class SVDModel:
    """SVD Matrix Factorization using Surprise library."""

    def __init__(self, n_factors: int = 100, n_epochs: int = 20,
                 lr_all: float = 0.005, reg_all: float = 0.02):
        """
        Args:
            n_factors: Số latent factors
            n_epochs: Số epochs training
            lr_all: Learning rate
            reg_all: Regularization term
        """

    def train(self, trainset) -> None:
        """
        Fit SVD model.
        - Dùng surprise.SVD
        - Log training time và n_factors
        """

    def predict(self, user_id: int, movie_id: int) -> float | None:
        """
        Dự đoán rating. Return None nếu unknown.
        """

    def recommend(self, user_id: int, n: int = 10, candidate_ids: list[int] = None) -> list[tuple[int, float]]:
        """
        Top-N recommendations.
        - Predict cho tất cả items user chưa rate (hoặc candidates)
        - Sort và return top-N
        Returns: [(movieId, predicted_rating), ...]
        """

    def get_user_factors(self, user_id: int) -> np.ndarray | None:
        """Trả về latent vector của user (cho explanation)"""

    def get_item_factors(self, movie_id: int) -> np.ndarray | None:
        """Trả về latent vector của item (cho explanation)"""

    def save(self, path: str) -> None:
        """Serialize model bằng joblib"""

    @classmethod
    def load(cls, path: str) -> 'SVDModel':
        """Deserialize model từ file"""
```

### Hyperparameters
| Parameter | Mặc định | Ghi chú |
|---|---|---|
| n_factors | 100 | Latent dimensions |
| n_epochs | 20 | Training iterations |
| lr_all | 0.005 | Learning rate |
| reg_all | 0.02 | L2 regularization |

## FILE 3: src/models/hybrid.py

### Class HybridRecommender:

```python
class HybridRecommender:
    """Hybrid recommender combining KNN and SVD with weighted scoring."""

    def __init__(self, knn_model: ItemKNN, svd_model: SVDModel, alpha: float = 0.5):
        """
        Args:
            knn_model: Trained ItemKNN instance
            svd_model: Trained SVDModel instance
            alpha: Weight cho SVD (1-alpha cho KNN). Range [0, 1].
        """

    def _normalize_scores(self, scores: list[tuple[int, float]]) -> dict[int, float]:
        """
        Normalize scores về [0, 1] dùng min-max normalization.
        Returns: {movieId: normalized_score}
        """

    def recommend(self, user_id: int, n: int = 10) -> list[dict]:
        """
        Top-N hybrid recommendations.
        Flow:
        1. Lấy candidates (items user chưa rate)
        2. Get SVD scores cho tất cả candidates
        3. Get KNN scores cho tất cả candidates
        4. Normalize cả 2 về [0, 1]
        5. final_score = alpha * svd_norm + (1 - alpha) * knn_norm
        6. Sort desc, return top-N

        Returns: [
            {
                "movieId": int,
                "score": float,         # hybrid score
                "svd_score": float,     # raw SVD predicted rating
                "knn_score": float,     # raw KNN predicted rating
            },
            ...
        ]

        Fallback: nếu 1 model fail cho item → dùng score của model còn lại
        """

    def recommend_for_new_user(self, rated_movies: dict[int, float],
                                trainset, n: int = 10) -> list[dict]:
        """
        Recommendation cho user mới (cold-start).
        - rated_movies: {movieId: rating} từ onboarding quiz
        - Tạo pseudo-user trong Surprise, predict cho candidates
        - Fallback: popularity nếu không đủ ratings
        """

    def tune_alpha(self, val_data: list, metric: str = 'ndcg') -> float:
        """
        Grid search alpha tối ưu trên validation data.
        - alpha_range: [0.3, 0.4, 0.5, 0.6, 0.7]
        - Metric: NDCG@10
        Returns: best alpha value
        """

    def save(self, path: str) -> None:
        """Save cả knn_model, svd_model, và alpha"""

    @classmethod
    def load(cls, path: str) -> 'HybridRecommender':
        """Load hybrid model"""
```

### Hybrid Scoring Logic
```
final_score = α × normalize(svd_score) + (1-α) × normalize(knn_score)

Normalize: min-max scaling về [0, 1]
  norm(x) = (x - min) / (max - min)

Fallback logic:
  - Nếu SVD fail cho item → dùng KNN score * 1.0
  - Nếu KNN fail cho item → dùng SVD score * 1.0
  - Nếu cả 2 fail → skip item
```

## FILE 4: src/models/__init__.py

```python
from .knn_model import ItemKNN
from .svd_model import SVDModel
from .hybrid import HybridRecommender
```

## LƯU Ý QUAN TRỌNG

### Surprise inner_id vs raw_id
Surprise dùng inner_id (0-indexed) nội bộ. Khi giao tiếp với bên ngoài, PHẢI convert:
```python
# raw_id → inner_id
inner_id = trainset.to_inner_uid(raw_user_id)
inner_iid = trainset.to_inner_iid(raw_movie_id)

# inner_id → raw_id
raw_id = trainset.to_raw_uid(inner_id)
raw_iid = trainset.to_raw_iid(inner_iid)
```

### Predict cho unknown user/item
```python
from surprise import PredictionImpossible
try:
    pred = algo.predict(uid, iid)
    return pred.est
except PredictionImpossible:
    return None
```

## DELIVERABLES
1. `src/models/__init__.py`
2. `src/models/knn_model.py` — ItemKNN class hoàn chỉnh
3. `src/models/svd_model.py` — SVDModel class hoàn chỉnh
4. `src/models/hybrid.py` — HybridRecommender class hoàn chỉnh
