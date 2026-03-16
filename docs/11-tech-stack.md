# Tech Stack & Kiến trúc hệ thống (Cập nhật)

## Thay đổi so với docs ban đầu
> Frontend đổi từ React sang **Gradio** để tập trung vào ML, phát triển nhanh hơn.
> Bỏ ANN index (Faiss/Annoy) vì dùng sample nhỏ, exact KNN đủ nhanh.

---

## 1. Tech Stack

### Python Packages (requirements.txt)
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
joblib==1.3.0        # Model serialization
python-dotenv==1.0.0
```

### Python Version
- Python 3.10+ (khuyến nghị 3.11)

---

## 2. Kiến trúc hệ thống (Đơn giản hóa)

```
┌─────────────────────────────────────────────────┐
│                   Gradio UI                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐ │
│  │Onboarding│  │Recommendations│  │  Search   │ │
│  │   Tab    │  │     Tab      │  │   Tab     │ │
│  └──────────┘  └──────────────┘  └───────────┘ │
└────────────────────┬────────────────────────────┘
                     │ (Python function calls)
┌────────────────────┴────────────────────────────┐
│              Backend Services                    │
│  ┌──────────────┐  ┌───────────────────────┐    │
│  │ Recommender  │  │   Explanation Service │    │
│  │   Service    │  │                       │    │
│  └──────┬───────┘  └───────────────────────┘    │
│         │                                        │
│  ┌──────┴───────┐  ┌───────────────────────┐    │
│  │  KNN Model   │  │      SVD Model        │    │
│  └──────────────┘  └───────────────────────┘    │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│              Data & Artifacts                    │
│  ┌──────────┐  ┌─────────┐  ┌────────────────┐ │
│  │ CSV Data │  │Processed│  │ Trained Models │ │
│  │ (raw)    │  │ DataFrames│ │ (.pkl files)  │ │
│  └──────────┘  └─────────┘  └────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 3. Cấu trúc thư mục (Cập nhật cho Gradio)

```
CT255H-NexConflict/
├── data/                     # Raw MovieLens data
│   ├── rating.csv
│   ├── movie.csv
│   ├── tag.csv
│   ├── genome_scores.csv
│   ├── genome_tags.csv
│   └── link.csv
├── docs/                     # Tài liệu dự án
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py         # Load & sample data
│   │   └── preprocessor.py   # Clean, split, feature engineering
│   ├── models/
│   │   ├── __init__.py
│   │   ├── knn_model.py      # Item-based KNN wrapper
│   │   ├── svd_model.py      # SVD wrapper
│   │   └── hybrid.py         # Hybrid scoring
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recommender.py    # Main recommendation logic
│   │   ├── explainer.py      # Explanation generation
│   │   └── search.py         # Movie search & filter
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py        # RMSE, MAE, Precision@K, etc.
│   │   └── evaluate.py       # Full evaluation pipeline
│   └── app.py                # Gradio UI entry point
├── artifacts/                 # Trained model files (.pkl)
├── notebooks/                 # Jupyter notebooks (EDA, experiments)
├── requirements.txt
└── README.md
```

---

## 4. Gradio UI Layout

### Tab 1: Onboarding
```
┌────────────────────────────────────────────┐
│  🎬 Chào mừng! Hãy cho chúng tôi biết    │
│     sở thích phim của bạn                  │
│                                            │
│  Chọn thể loại yêu thích:                 │
│  ☐ Action  ☐ Comedy  ☐ Drama  ☐ Sci-Fi  │
│  ☐ Thriller ☐ Romance ☐ Horror ☐ Animation│
│                                            │
│  Đánh giá các phim sau (1-5 sao):         │
│  ┌────────────────────────────┬──────┐     │
│  │ The Shawshank Redemption   │ ⭐⭐⭐⭐⭐│     │
│  │ The Dark Knight            │ ⭐⭐⭐⭐ │     │
│  │ Inception                  │ ⭐⭐⭐  │     │
│  │ Titanic                    │ ⭐⭐   │     │
│  │ ...                        │      │     │
│  └────────────────────────────┴──────┘     │
│                                            │
│  [💡 Gợi ý phim cho tôi]                  │
└────────────────────────────────────────────┘
```

### Tab 2: Recommendations
```
┌────────────────────────────────────────────┐
│  📋 Top 10 phim gợi ý cho bạn             │
│                                            │
│  1. Interstellar (2014)     ⭐ 4.5 dự đoán│
│     Sci-Fi, Adventure                      │
│     💬 "Vì bạn thích Inception, phim này  │
│        có pattern đánh giá tương tự (87%)" │
│                                            │
│  2. The Matrix (1999)       ⭐ 4.3 dự đoán│
│     Action, Sci-Fi                         │
│     💬 "Phù hợp với thể loại yêu thích:  │
│        Action, Sci-Fi"                     │
│  ...                                       │
└────────────────────────────────────────────┘
```

### Tab 3: Search & Filter
```
┌────────────────────────────────────────────┐
│  🔍 Tìm kiếm phim                         │
│  [_________________________] [Tìm]         │
│                                            │
│  Lọc theo:                                 │
│  Genre: [All ▼]  Year: [All ▼]            │
│  Min Rating: [3.0 ▼]                       │
│                                            │
│  Kết quả:                                  │
│  ┌────────────────────────────────────┐    │
│  │ Movie Title | Year | Genre | Rating│    │
│  │ ───────────────────────────────────│    │
│  │ Inception   | 2010 | Sci-Fi| 4.2  │    │
│  │ ...                                │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

### Tab 4: Model Evaluation (Optional)
```
┌────────────────────────────────────────────┐
│  📊 So sánh hiệu suất các thuật toán      │
│                                            │
│  [Biểu đồ bar: RMSE comparison]           │
│  [Biểu đồ bar: Precision@10 comparison]   │
│  [Bảng tổng hợp metrics]                  │
└────────────────────────────────────────────┘
```

---

## 5. Data Flow chi tiết

### Preprocessing Pipeline
```python
# 1. Load raw data
ratings = pd.read_csv('data/rating.csv')
movies = pd.read_csv('data/movie.csv')

# 2. Sample data (giảm từ 20M → ~1M)
sampled_users = ratings.userId.unique()[:N_USERS]
ratings_sampled = ratings[ratings.userId.isin(sampled_users)]

# 3. Filter sparse users/items
# Giữ users có >= 20 ratings, items có >= 10 ratings
user_counts = ratings_sampled.groupby('userId').size()
item_counts = ratings_sampled.groupby('movieId').size()

# 4. Train/Validation split (time-aware)
# 80% cũ nhất → train, 20% mới nhất → validation

# 5. Tạo Surprise Dataset
from surprise import Dataset, Reader
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings_sampled[['userId', 'movieId', 'rating']], reader)
```

### Recommendation Flow
```python
# 1. User hoàn thành onboarding → có rated_movies dict
# 2. Predict rating cho tất cả candidate movies
# 3. SVD score + KNN score → Hybrid score
# 4. Sort by hybrid score → Top-N
# 5. Generate explanation cho mỗi recommendation
# 6. Return to Gradio UI
```
