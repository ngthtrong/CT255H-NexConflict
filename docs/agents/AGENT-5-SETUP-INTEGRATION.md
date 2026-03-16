# AGENT 5: Project Setup & Integration
# Vai trò: Thiết lập project, tích hợp tất cả components, orchestration scripts

## BỐI CẢNH DỰ ÁN
Ứng dụng gợi ý phim MovieLens. Agent này chạy ĐẦU TIÊN (setup) và CUỐI CÙNG (integration).
- Kiến trúc: docs/ARCHITECTURE.md
- Tech stack: docs/11-tech-stack.md

## NHIỆM VỤ

### PHASE A: Project Setup (chạy ĐẦU TIÊN, trước tất cả agents khác)

#### A1: Tạo cấu trúc thư mục
```
CT255H-NexConflict/
├── data/                     # Placeholder cho CSV files
├── src/
│   ├── data/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── evaluation/
│   │   └── __init__.py
│   └── __init__.py           # Make src a package
├── artifacts/
│   └── plots/
├── notebooks/
├── requirements.txt
├── .gitignore
└── README.md
```

#### A2: Tạo requirements.txt
```
# Web Framework
fastapi==0.109.0
uvicorn==0.27.0
gradio==4.19.0

# ML & Data
scikit-surprise==1.1.3
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.0

# Evaluation & Visualization
matplotlib==3.8.0
seaborn==0.13.0

# Utilities
joblib==1.3.0
python-dotenv==1.0.0
```

#### A3: Tạo .gitignore
```
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/
*.egg

# Data files (too large for git)
data/*.csv

# Model artifacts
artifacts/*.pkl
artifacts/*.joblib

# Environment
.env
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/

# Plots giữ lại (không ignore)
!artifacts/plots/.gitkeep
```

#### A4: Cập nhật README.md
```markdown
# NexConflict - Movie Recommendation System

Hệ thống gợi ý phim sử dụng Collaborative Filtering trên MovieLens 20M Dataset.

## Thuật toán
- Item-based KNN (Cosine Similarity)
- SVD (Matrix Factorization)
- Hybrid (Weighted KNN + SVD)

## Tech Stack
- **Frontend**: Gradio
- **ML**: scikit-surprise, scikit-learn
- **Data**: pandas, numpy
- **Visualization**: matplotlib, seaborn

## Cài đặt

### 1. Clone repository
(git clone command)

### 2. Tạo virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate     # Windows

### 3. Cài dependencies
pip install -r requirements.txt

### 4. Download data
Download MovieLens 20M dataset và đặt các file CSV vào thư mục `data/`:
- rating.csv
- movie.csv

### 5. Train models
python -m src.scripts.train

### 6. Chạy app
python -m src.app

Truy cập: http://localhost:7860

## Cấu trúc thư mục
(xem docs/ARCHITECTURE.md)

## Thành viên
- (Tên sinh viên 1)
- (Tên sinh viên 2)

## Môn học
CT255H - Ứng dụng và Máy học
```

---

### PHASE B: Integration Scripts (chạy SAU tất cả agents khác)

#### B1: Training Script — src/scripts/train.py

```python
"""
Script train tất cả models và save vào artifacts/.

Usage: python -m src.scripts.train [--n-users 5000] [--tune]

Flow:
1. Load data (loader.py)
2. Sample data (n_users)
3. Preprocess (filter, split, create Surprise dataset)
4. Train Item-KNN → save artifacts/knn_model.pkl
5. Train SVD → save artifacts/svd_model.pkl
6. Create Hybrid → tune alpha nếu --tune → save artifacts/hybrid_model.pkl
7. Run evaluation → save artifacts/evaluation_results.json + plots
8. Log tổng kết
"""

import argparse
import logging
import time
from pathlib import Path

from src.data import load_ratings, load_movies, sample_data
from src.data import filter_sparse, enrich_movies, time_split, create_surprise_dataset, get_popular_movies
from src.models import ItemKNN, SVDModel, HybridRecommender
from src.evaluation import EvaluationPipeline, RandomModel, PopularityModel

ARTIFACTS_DIR = Path("artifacts")
PLOTS_DIR = ARTIFACTS_DIR / "plots"

def main():
    parser = argparse.ArgumentParser(description="Train recommendation models")
    parser.add_argument("--n-users", type=int, default=5000, help="Number of users to sample")
    parser.add_argument("--tune", action="store_true", help="Tune hyperparameters")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    # Step 1: Load & Sample
    logger.info("Loading data...")
    ratings = load_ratings()
    movies = load_movies()
    ratings = sample_data(ratings, n_users=args.n_users)

    # Step 2: Preprocess
    logger.info("Preprocessing...")
    ratings = filter_sparse(ratings)
    movies = enrich_movies(movies, ratings)
    train_df, test_df = time_split(ratings)
    trainset, testset = create_surprise_dataset(train_df)
    popular = get_popular_movies(movies)

    # Save processed data for app
    movies.to_pickle(ARTIFACTS_DIR / "movies_info.pkl")
    popular.to_pickle(ARTIFACTS_DIR / "popular_movies.pkl")
    # Save trainset reference cần cho new user prediction
    import joblib
    joblib.dump(trainset, ARTIFACTS_DIR / "trainset.pkl")
    joblib.dump(testset, ARTIFACTS_DIR / "testset.pkl")

    # Step 3: Train KNN
    logger.info("Training Item-KNN...")
    t0 = time.time()
    knn = ItemKNN(k=30, sim_name='cosine')
    knn.train(trainset)
    knn.save(str(ARTIFACTS_DIR / "knn_model.pkl"))
    logger.info(f"KNN trained in {time.time()-t0:.1f}s")

    # Step 4: Train SVD
    logger.info("Training SVD...")
    t0 = time.time()
    svd = SVDModel(n_factors=100, n_epochs=20)
    svd.train(trainset)
    svd.save(str(ARTIFACTS_DIR / "svd_model.pkl"))
    logger.info(f"SVD trained in {time.time()-t0:.1f}s")

    # Step 5: Create Hybrid
    logger.info("Creating Hybrid model...")
    hybrid = HybridRecommender(knn, svd, alpha=0.5)
    if args.tune:
        logger.info("Tuning alpha...")
        best_alpha = hybrid.tune_alpha(testset)
        logger.info(f"Best alpha: {best_alpha}")
    hybrid.save(str(ARTIFACTS_DIR / "hybrid_model.pkl"))

    # Step 6: Evaluate
    logger.info("Running evaluation...")
    evaluator = EvaluationPipeline(trainset, testset, movies)
    models = {
        "Random": RandomModel(movies['movieId'].tolist()),
        "Popularity": PopularityModel(movies),
        "Item-KNN": knn,
        "SVD": svd,
        "Hybrid": hybrid,
    }
    results_df, plots = evaluator.run_full_evaluation(models)
    evaluator.save_results(results_df)

    logger.info("Training complete!")
    logger.info(f"\n{results_df.to_string()}")
```

#### B2: src/scripts/__init__.py
```python
# Empty
```

#### B3: Smoke Test Script — tests/test_smoke.py

```python
"""
Smoke test: kiểm tra tất cả components hoạt động đúng.

Usage: python -m pytest tests/test_smoke.py -v
"""

def test_data_loader():
    """Test loader loads data correctly"""
    from src.data import load_ratings, load_movies, sample_data, get_stats
    ratings = load_ratings()
    movies = load_movies()
    assert len(ratings) > 0
    assert len(movies) > 0
    sampled = sample_data(ratings, n_users=100)
    assert sampled['userId'].nunique() <= 100
    stats = get_stats(sampled, movies)
    assert 'n_users' in stats

def test_preprocessor():
    """Test preprocessing pipeline"""
    from src.data import (load_ratings, load_movies, sample_data,
                           filter_sparse, enrich_movies, time_split,
                           create_surprise_dataset, get_popular_movies, get_all_genres)
    ratings = sample_data(load_ratings(), n_users=100)
    movies = load_movies()
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    movies = enrich_movies(movies, ratings)
    train, test = time_split(ratings)
    assert len(train) > len(test)
    trainset, testset = create_surprise_dataset(train)
    assert trainset is not None
    popular = get_popular_movies(movies, n=10)
    assert len(popular) <= 10
    genres = get_all_genres(movies)
    assert len(genres) > 0

def test_knn_model():
    """Test KNN trains and predicts"""
    from src.data import load_ratings, sample_data, filter_sparse, time_split, create_surprise_dataset
    from src.models import ItemKNN
    ratings = sample_data(load_ratings(), n_users=100)
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    train, _ = time_split(ratings)
    trainset, _ = create_surprise_dataset(train)
    knn = ItemKNN(k=10)
    knn.train(trainset)
    recs = knn.recommend(trainset.to_raw_uid(0), n=5)
    assert len(recs) > 0

def test_svd_model():
    """Test SVD trains and predicts"""
    from src.data import load_ratings, sample_data, filter_sparse, time_split, create_surprise_dataset
    from src.models import SVDModel
    ratings = sample_data(load_ratings(), n_users=100)
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    train, _ = time_split(ratings)
    trainset, _ = create_surprise_dataset(train)
    svd = SVDModel(n_factors=10, n_epochs=5)
    svd.train(trainset)
    recs = svd.recommend(trainset.to_raw_uid(0), n=5)
    assert len(recs) > 0

def test_metrics():
    """Test metric calculations"""
    from src.evaluation.metrics import rmse, mae, precision_at_k, recall_at_k, ndcg_at_k
    preds = [(4.0, 3.5), (3.0, 3.2), (5.0, 4.5)]
    assert rmse(preds) > 0
    assert mae(preds) > 0
    rec = [1, 2, 3, 4, 5]
    rel = {1, 3, 7}
    assert 0 <= precision_at_k(rec, rel, k=5) <= 1
    assert 0 <= recall_at_k(rec, rel, k=5) <= 1

def test_search():
    """Test search service"""
    from src.data import load_movies
    from src.services.search import SearchService
    movies = load_movies()
    # Minimal enrich for search
    movies['avg_rating'] = 3.5
    movies['num_ratings'] = 100
    movies['year'] = 2000
    search = SearchService(movies)
    results = search.search_movies("toy", limit=5)
    assert len(results) >= 0  # May or may not find "Toy Story"
```

---

## THỨ TỰ THỰC HIỆN

```
1. [AGENT 5 - Phase A] Project Setup           ← CHẠY ĐẦU TIÊN
2. [AGENT 1] Data Pipeline                     ← song song
3. [AGENT 2] ML Models                         ← sau Agent 1 (phụ thuộc data)
4. [AGENT 3] Services + UI                     ← sau Agent 2 (phụ thuộc models)
5. [AGENT 4] Evaluation Pipeline               ← sau Agent 2 (phụ thuộc models)
6. [AGENT 5 - Phase B] Integration Scripts     ← CHẠY CUỐI CÙNG
```

## ARTIFACTS DIRECTORY STRUCTURE (sau khi train xong)
```
artifacts/
├── knn_model.pkl          # Trained ItemKNN
├── svd_model.pkl          # Trained SVDModel
├── hybrid_model.pkl       # Trained HybridRecommender
├── movies_info.pkl        # Processed movies DataFrame
├── popular_movies.pkl     # Popular movies for onboarding
├── trainset.pkl           # Surprise Trainset (for new user prediction)
├── testset.pkl            # Test data
├── evaluation_results.json # Metrics comparison table
└── plots/
    ├── rmse_comparison.png
    ├── precision_comparison.png
    ├── ndcg_comparison.png
    └── overview_comparison.png
```

## DELIVERABLES
### Phase A:
1. Cấu trúc thư mục hoàn chỉnh
2. `requirements.txt`
3. `.gitignore`
4. `README.md` (cập nhật)
5. Tất cả `__init__.py` placeholder files

### Phase B:
1. `src/scripts/__init__.py`
2. `src/scripts/train.py` — Training orchestration script
3. `tests/test_smoke.py` — Smoke tests
