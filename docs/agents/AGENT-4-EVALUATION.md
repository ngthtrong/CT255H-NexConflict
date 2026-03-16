# AGENT 4: Evaluation Pipeline
# Vai trò: Xây dựng hệ thống đánh giá và so sánh models

## BỐI CẢNH DỰ ÁN
Ứng dụng gợi ý phim cần đánh giá chất lượng của các thuật toán.
- So sánh 5 models: Random, Popularity, Item-KNN, SVD, Hybrid
- Metrics: docs/10-algorithm-detail.md (Section 6)
- Kiến trúc: docs/ARCHITECTURE.md

## PHỤ THUỘC
- **Agent 1**: `src/data/` — data loading, testset
- **Agent 2**: `src/models/` — trained models

## NHIỆM VỤ
Tạo 3 file:
1. `src/evaluation/__init__.py`
2. `src/evaluation/metrics.py` — Các hàm tính metrics
3. `src/evaluation/evaluate.py` — Pipeline đánh giá tổng hợp

## RÀNG BUỘC
- Output: JSON file + PNG charts → `artifacts/`
- Dùng matplotlib + seaborn cho visualizations
- Type hints, docstrings, logging
- Phải handle edge cases (division by zero, empty lists)

---

## FILE 1: src/evaluation/metrics.py

### Regression Metrics

```python
import numpy as np
from typing import List, Tuple

def rmse(predictions: list[tuple[float, float]]) -> float:
    """
    Root Mean Square Error.
    Args:
        predictions: [(actual_rating, predicted_rating), ...]
    Returns: RMSE value (lower is better)
    Formula: sqrt(mean((actual - predicted)²))
    """

def mae(predictions: list[tuple[float, float]]) -> float:
    """
    Mean Absolute Error.
    Args:
        predictions: [(actual_rating, predicted_rating), ...]
    Returns: MAE value (lower is better)
    Formula: mean(|actual - predicted|)
    """
```

### Ranking Metrics

```python
def precision_at_k(recommended: list[int], relevant: set[int], k: int = 10) -> float:
    """
    Precision@K: Trong K phim gợi ý, bao nhiêu % user thật sự thích.

    Args:
        recommended: list movieIds đã được gợi ý (ordered by rank)
        relevant: set movieIds mà user thật sự thích (rating >= threshold)
        k: top-K

    Returns: precision score [0, 1]
    Formula: |relevant ∩ recommended@K| / K
    """

def recall_at_k(recommended: list[int], relevant: set[int], k: int = 10) -> float:
    """
    Recall@K: Trong tất cả phim user thích, bao nhiêu % nằm trong top-K.

    Args: same as precision_at_k
    Returns: recall score [0, 1]
    Formula: |relevant ∩ recommended@K| / |relevant|
    Edge case: nếu |relevant| = 0, return 0.0
    """

def ndcg_at_k(recommended: list[int], relevant: dict[int, float], k: int = 10) -> float:
    """
    Normalized Discounted Cumulative Gain @K.
    Thứ tự quan trọng: phim tốt nên ở vị trí đầu.

    Args:
        recommended: list movieIds ordered by predicted score
        relevant: {movieId: actual_rating} - ground truth ratings
        k: top-K

    Returns: NDCG score [0, 1]

    Formula:
        DCG@K = Σ (2^rel_i - 1) / log2(i + 1)  for i in 1..K
        IDCG@K = DCG of perfect ranking
        NDCG@K = DCG@K / IDCG@K

    Edge case: nếu IDCG = 0, return 0.0
    """
```

### Coverage & Diversity

```python
def coverage(all_recommendations: list[list[int]], total_items: int) -> float:
    """
    Tỷ lệ phim unique được gợi ý / tổng số phim.

    Args:
        all_recommendations: list of recommendation lists (1 per user)
        total_items: tổng số phim trong catalog

    Returns: coverage [0, 1]
    Formula: |unique recommended items| / total_items
    """

def intra_list_diversity(recommended_ids: list[int],
                          similarity_matrix: dict | None = None) -> float:
    """
    Trung bình khoảng cách giữa các phim trong list gợi ý.

    Args:
        recommended_ids: list of movieIds in 1 recommendation
        similarity_matrix: {(id1, id2): similarity} hoặc None

    Returns: ILD score [0, 1] (higher = more diverse)

    Formula: mean(1 - similarity(i, j)) for all pairs in recommendation list

    Nếu similarity_matrix is None:
      → dùng genre-based similarity (Jaccard trên genre sets)
    """

def genre_jaccard_similarity(genres_a: set[str], genres_b: set[str]) -> float:
    """
    Jaccard similarity giữa 2 sets genres.
    Formula: |A ∩ B| / |A ∪ B|
    Edge case: empty sets → return 0.0
    """
```

---

## FILE 2: src/evaluation/evaluate.py

### Baseline Models

```python
import random
import numpy as np
import pandas as pd

class RandomModel:
    """Baseline: gợi ý ngẫu nhiên."""

    def __init__(self, all_movie_ids: list[int], rating_range: tuple = (0.5, 5.0)):
        self.all_movie_ids = all_movie_ids
        self.rating_range = rating_range

    def predict(self, user_id: int, movie_id: int) -> float:
        return random.uniform(*self.rating_range)

    def recommend(self, user_id: int, n: int = 10, exclude: set = None) -> list[tuple[int, float]]:
        candidates = [m for m in self.all_movie_ids if m not in (exclude or set())]
        selected = random.sample(candidates, min(n, len(candidates)))
        return [(mid, self.predict(user_id, mid)) for mid in selected]


class PopularityModel:
    """Baseline: gợi ý theo popularity (avg rating × log(count))."""

    def __init__(self, movies_info: pd.DataFrame):
        # Pre-compute popularity scores
        self.popularity = movies_info.copy()
        self.popularity['pop_score'] = (
            self.popularity['avg_rating'] * np.log1p(self.popularity['num_ratings'])
        )
        self.popularity = self.popularity.sort_values('pop_score', ascending=False)

    def predict(self, user_id: int, movie_id: int) -> float:
        row = self.popularity[self.popularity['movieId'] == movie_id]
        return row['avg_rating'].values[0] if len(row) > 0 else 3.0

    def recommend(self, user_id: int, n: int = 10, exclude: set = None) -> list[tuple[int, float]]:
        candidates = self.popularity[~self.popularity['movieId'].isin(exclude or set())]
        top_n = candidates.head(n)
        return list(zip(top_n['movieId'], top_n['pop_score']))
```

### Main Evaluation Pipeline

```python
class EvaluationPipeline:
    """Chạy đánh giá tổng hợp cho tất cả models."""

    def __init__(self, trainset, testset: list, movies_info: pd.DataFrame):
        """
        Args:
            trainset: Surprise Trainset
            testset: [(userId, movieId, rating), ...]
            movies_info: DataFrame with movie metadata
        """

    def evaluate_rating_prediction(self, model, testset) -> dict:
        """
        Đánh giá rating prediction: RMSE, MAE.

        Flow:
        1. Cho mỗi (user, item, actual) trong testset:
           predicted = model.predict(user, item)
        2. Tính RMSE, MAE từ (actual, predicted) pairs

        Returns: {"rmse": float, "mae": float}
        """

    def evaluate_topn(self, model, testset, n: int = 10,
                      threshold: float = 3.5) -> dict:
        """
        Đánh giá ranking quality.

        Flow:
        1. Group testset by user
        2. Cho mỗi user:
           - relevant = {items user rated >= threshold}
           - recommended = model.recommend(user, n)
           - Tính precision@k, recall@k, ndcg@k
        3. Average across all users

        Returns: {
            "precision@{n}": float,
            "recall@{n}": float,
            "ndcg@{n}": float
        }
        """

    def evaluate_coverage_diversity(self, model, test_users: list[int],
                                     n: int = 10) -> dict:
        """
        Đánh giá coverage và diversity.

        Flow:
        1. Chạy recommend() cho mỗi test user
        2. Coverage = unique items / total items
        3. Diversity = average ILD across all recommendations

        Returns: {"coverage": float, "diversity": float}
        """

    def compare_all_models(self, models: dict[str, object], n: int = 10) -> pd.DataFrame:
        """
        So sánh tất cả models.

        Args:
            models: {"Random": RandomModel, "Popularity": PopModel,
                     "Item-KNN": knn, "SVD": svd, "Hybrid": hybrid}

        Flow:
        1. Cho mỗi model → evaluate_rating_prediction + evaluate_topn + evaluate_coverage_diversity
        2. Aggregate thành 1 DataFrame

        Returns: pd.DataFrame
            columns: [Model, RMSE, MAE, Precision@10, Recall@10, NDCG@10, Coverage, Diversity]
            rows: 1 per model
        """

    def plot_comparison(self, results_df: pd.DataFrame, save_dir: str = "artifacts/plots") -> dict:
        """
        Tạo biểu đồ so sánh.

        Plots:
        1. Bar chart: RMSE comparison (lower is better)
        2. Bar chart: Precision@10 comparison (higher is better)
        3. Bar chart: NDCG@10 comparison (higher is better)
        4. Grouped bar chart: All metrics overview

        Returns: dict of matplotlib Figure objects {"rmse": fig1, "precision": fig2, ...}

        Style:
        - seaborn style: "whitegrid"
        - Color palette: "Set2" hoặc "husl"
        - Title tiếng Việt
        - Save PNG files vào save_dir
        """

    def save_results(self, results_df: pd.DataFrame, path: str = "artifacts/evaluation_results.json") -> None:
        """Save kết quả ra JSON"""

    def run_full_evaluation(self, models: dict) -> tuple[pd.DataFrame, dict]:
        """
        Chạy toàn bộ evaluation pipeline.
        Returns: (results_df, plot_figures_dict)
        """
```

## FILE 3: src/evaluation/__init__.py

```python
from .metrics import rmse, mae, precision_at_k, recall_at_k, ndcg_at_k, coverage, intra_list_diversity
from .evaluate import EvaluationPipeline, RandomModel, PopularityModel
```

---

## TARGET METRICS (Ước tính để reference)

| Metric | Random | Popularity | KNN | SVD | Hybrid |
|---|---|---|---|---|---|
| RMSE | ~1.5 | ~1.0 | ~0.90 | ~0.87 | ~0.85 |
| MAE | ~1.2 | ~0.80 | ~0.70 | ~0.67 | ~0.65 |
| Precision@10 | ~0.05 | ~0.20 | ~0.30 | ~0.33 | ~0.35 |
| Recall@10 | ~0.02 | ~0.10 | ~0.15 | ~0.18 | ~0.20 |
| NDCG@10 | ~0.05 | ~0.25 | ~0.35 | ~0.38 | ~0.40 |
| Coverage | ~0.90 | ~0.05 | ~0.30 | ~0.40 | ~0.45 |
| Diversity | ~0.90 | ~0.30 | ~0.50 | ~0.55 | ~0.60 |

## CHART STYLING

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Cài đặt chung
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
sns.set_style("whitegrid")
palette = sns.color_palette("Set2")

# Ví dụ bar chart
fig, ax = plt.subplots()
bars = ax.bar(model_names, rmse_values, color=palette[:len(model_names)])
ax.set_title("So sánh RMSE giữa các Model")
ax.set_ylabel("RMSE (thấp hơn = tốt hơn)")
ax.set_xlabel("Model")
# Thêm value labels trên mỗi bar
for bar, val in zip(bars, rmse_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', va='bottom')
```

## DELIVERABLES
1. `src/evaluation/__init__.py`
2. `src/evaluation/metrics.py` — Tất cả metric functions
3. `src/evaluation/evaluate.py` — baseline models + EvaluationPipeline + plotting
4. Output files (sinh bởi pipeline):
   - `artifacts/evaluation_results.json`
   - `artifacts/plots/rmse_comparison.png`
   - `artifacts/plots/precision_comparison.png`
   - `artifacts/plots/ndcg_comparison.png`
   - `artifacts/plots/overview_comparison.png`
