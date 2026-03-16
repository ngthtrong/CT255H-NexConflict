# Kiến trúc & Phân tích chi tiết - NexConflict Movie Recommender

## 1. TỔNG QUAN DỰ ÁN

### Mục tiêu
Web App gợi ý phim sử dụng Collaborative Filtering trên MovieLens 20M Dataset (sampled).
Chạy local, phục vụ demo cho môn Ứng dụng và Máy học.

### Ràng buộc cứng
| Ràng buộc | Chi tiết |
|---|---|
| Thời gian | 3 tuần |
| Nhóm | 2 sinh viên |
| Deploy | Local only (localhost) |
| Dataset | MovieLens 20M, sample ~1M ratings / ~10K movies |
| Python | 3.10+ (khuyến nghị 3.11) |
| Không có poster/ảnh phim | Chỉ hiển thị text |
| Không cloud deploy | Không Docker, không cloud |

---

## 2. TÍNH NĂNG CHI TIẾT

### 2.1 Tính năng CORE (Bắt buộc)

#### F1: Onboarding Quiz (Cold-start)
- **Input**: User mới truy cập app
- **Flow**:
  1. Hiển thị danh sách tất cả genres có trong dataset (Action, Comedy, Drama, Sci-Fi, Thriller, Romance, Horror, Animation, ...)
  2. User chọn 2-5 genres yêu thích (CheckboxGroup)
  3. Hệ thống hiển thị 10-15 phim phổ biến nhất từ genres đã chọn
  4. User đánh giá ít nhất 5 phim (1-5 sao, bước 0.5)
  5. Nhấn "Gợi ý phim cho tôi" → chạy recommendation
- **Output**: Top-10 phim gợi ý kèm explanation
- **Fallback**: Nếu user rate < 5 phim → dùng popularity-based trong genres đã chọn

#### F2: Gợi ý phim cho Existing User
- **Input**: Chọn user_id từ dropdown (users có trong dataset)
- **Flow**: Chạy Hybrid model (SVD + KNN) → Top-N
- **Output**: Danh sách phim gợi ý kèm predicted rating và explanation
- **Config**: Slider chọn số lượng N (5-20, default 10)

#### F3: Giải thích gợi ý (XAI)
- **Mỗi phim gợi ý** đều kèm 1 câu giải thích
- **Templates**:
  - KNN: "Vì bạn thích '{liked_movie}', phim này có pattern đánh giá tương tự (similarity: {sim:.0%})"
  - SVD: "Dựa trên sở thích của bạn, model dự đoán bạn sẽ đánh giá phim này {rating:.1f}/5"
  - Genre: "Phù hợp với thể loại yêu thích của bạn: {genres}"
  - Popular: "Phim được đánh giá cao bởi {count} người dùng (avg: {avg:.1f}/5)"
- **Logic chọn**: dựa vào model nào contribute nhiều hơn trong hybrid score

#### F4: Tìm kiếm & Lọc phim
- **Search**: Tìm theo tên phim (case-insensitive, partial match)
- **Filter**: Genre (dropdown), Min rating (slider 0.5-5.0)
- **Sort**: Theo relevance hoặc avg rating
- **Output**: Dataframe kết quả (title, year, genres, avg_rating, num_ratings)

#### F5: Model Evaluation Dashboard
- **Hiển thị**: Biểu đồ so sánh 5 models (Random, Popularity, KNN, SVD, Hybrid)
- **Metrics hiển thị**: RMSE, MAE, Precision@10, Recall@10, NDCG@10, Coverage, Diversity
- **Format**: Bar charts (gr.Plot) + Bảng tổng hợp (gr.Dataframe)

### 2.2 Tính năng KHÔNG LÀM
- Poster/ảnh phim (không có API key TMDb)
- User authentication/login
- Lưu user session/history
- Cloud deployment
- Real-time model retraining
- Content-based filtering (chỉ dùng collaborative)

---

## 3. KIẾN TRÚC HỆ THỐNG

### 3.1 Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────┐
│                   GRADIO UI (app.py)                │
│  ┌────────────┐ ┌──────────┐ ┌───────┐ ┌────────┐ │
│  │ Onboarding │ │ Recommend│ │Search │ │  Eval  │ │
│  │    Tab     │ │   Tab    │ │  Tab  │ │  Tab   │ │
│  └─────┬──────┘ └────┬─────┘ └───┬───┘ └───┬────┘ │
└────────┼──────────────┼──────────┼──────────┼──────┘
         │              │          │          │
         ▼              ▼          ▼          ▼
┌─────────────────────────────────────────────────────┐
│                  SERVICES LAYER                     │
│  ┌──────────────────┐ ┌───────────┐ ┌───────────┐  │
│  │RecommenderService│ │ Explainer │ │  Search   │  │
│  │  (singleton)     │ │  Service  │ │  Service  │  │
│  └────────┬─────────┘ └───────────┘ └───────────┘  │
└───────────┼─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│                   MODELS LAYER                      │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐   │
│  │ ItemKNN  │  │ SVDModel │  │HybridRecommender│   │
│  │ (.pkl)   │  │ (.pkl)   │  │  (orchestrator) │   │
│  └──────────┘  └──────────┘  └─────────────────┘   │
└───────────┬─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│                    DATA LAYER                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  loader  │  │ preprocessor │  │  CSV files   │  │
│  │  .py     │  │    .py       │  │  (data/)     │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
[CSV files] → loader.py → raw DataFrames
                              ↓
                        preprocessor.py
                              ↓
                    ┌─────────┴──────────┐
                    ↓                    ↓
            Surprise Dataset      Pandas DataFrames
            (for training)        (for search/filter)
                    ↓
            ┌───────┴───────┐
            ↓               ↓
        KNN.train()     SVD.train()
            ↓               ↓
        knn.pkl         svd.pkl
            ↓               ↓
            └───────┬───────┘
                    ↓
            HybridRecommender
                    ↓
            RecommenderService
                    ↓
              Gradio UI
```

### 3.3 Giao tiếp giữa các layer

**Quan trọng**: Gradio gọi trực tiếp Python functions, KHÔNG qua HTTP API.
FastAPI chỉ là optional wrapper nếu muốn expose REST endpoints sau này.
Trong MVP này, Gradio → Python function calls → Services → Models.

---

## 4. DATA CONTRACTS (Interfaces giữa các module)

### 4.1 Data Layer → Models Layer

```python
# loader.py outputs:
ratings_df: pd.DataFrame  # columns: userId(int32), movieId(int32), rating(float32), timestamp(int64)
movies_df: pd.DataFrame   # columns: movieId(int32), title(str), genres(str - pipe-separated)

# preprocessor.py outputs:
trainset: surprise.Trainset           # Surprise training format
testset: list[tuple]                  # [(uid, iid, rating), ...]
movies_info: pd.DataFrame             # movieId, title, genres, avg_rating, num_ratings, year
popular_movies: pd.DataFrame           # Top-50 popular movies for onboarding
genre_list: list[str]                  # Unique genres extracted from dataset
```

### 4.2 Models Layer → Services Layer

```python
# Mỗi model class cung cấp:
class ItemKNN:
    def predict(self, user_id: int, movie_id: int) -> float  # predicted rating
    def recommend(self, user_id: int, n: int = 10) -> list[tuple[int, float]]  # [(movieId, score), ...]
    def get_neighbors(self, movie_id: int, k: int = 10) -> list[tuple[int, float]]  # [(movieId, sim), ...]

class SVDModel:
    def predict(self, user_id: int, movie_id: int) -> float
    def recommend(self, user_id: int, n: int = 10, candidate_ids: list[int] = None) -> list[tuple[int, float]]

class HybridRecommender:
    def recommend(self, user_id: int, n: int = 10) -> list[dict]
    # Returns: [{"movieId": int, "score": float, "svd_score": float, "knn_score": float}, ...]
```

### 4.3 Services Layer → UI Layer

```python
# RecommenderService outputs:
class RecommenderService:
    def recommend_for_new_user(self, genres: list[str], ratings: dict[int, float]) -> list[dict]
    # Returns: [{"movieId", "title", "genres", "predicted_rating", "explanation"}, ...]

    def recommend_for_user(self, user_id: int, n: int = 10) -> list[dict]
    # Returns: same format as above

# SearchService outputs:
class SearchService:
    def search_movies(self, query: str, genre: str = None, min_rating: float = None, limit: int = 20) -> pd.DataFrame
    # Returns: DataFrame with columns [title, year, genres, avg_rating, num_ratings]
```

---

## 5. RÀNG BUỘC KỸ THUẬT

### 5.1 Dependencies chính xác
```
fastapi==0.109.0
uvicorn==0.27.0
gradio==4.19.0
scikit-surprise==1.1.3
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.0
matplotlib==3.8.0
seaborn==0.13.0
joblib==1.3.0
python-dotenv==1.0.0
```

### 5.2 Cấu trúc thư mục bắt buộc
```
CT255H-NexConflict/
├── data/                     # Raw MovieLens CSV files
│   ├── rating.csv
│   ├── movie.csv
│   ├── tag.csv
│   ├── genome_scores.csv
│   ├── genome_tags.csv
│   └── link.csv
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── knn_model.py
│   │   ├── svd_model.py
│   │   └── hybrid.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recommender.py
│   │   ├── explainer.py
│   │   └── search.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── evaluate.py
│   └── app.py
├── artifacts/                # Trained models (.pkl)
├── notebooks/                # Jupyter notebooks
├── requirements.txt
└── README.md
```

### 5.3 Dataset CSV format
```
rating.csv:  userId,movieId,rating,timestamp
movie.csv:   movieId,title,genres  (genres pipe-separated: "Action|Comedy|Drama")
tag.csv:     userId,movieId,tag,timestamp
link.csv:    movieId,imdbId,tmdbId
genome_scores.csv: movieId,tagId,relevance
genome_tags.csv:   tagId,tag
```

### 5.4 Giới hạn & Trade-offs
- **Không dùng ANN index** (Faiss/Annoy) → exact KNN, chấp nhận chậm hơn nhưng đơn giản
- **Similarity matrix lưu trong RAM** → giới hạn ~10K movies
- **Model load 1 lần** khi app start (singleton) → startup chậm nhưng runtime nhanh
- **Không persistent storage** cho user mới → mất data khi restart app
- **Genre extraction từ title**: sử dụng regex parse year từ title (e.g., "Toy Story (1995)")

---

## 6. QUY TẮC CODING

### 6.1 Conventions
- Python type hints cho tất cả function signatures
- Docstrings cho tất cả class và public methods
- Logging dùng `logging` module (không print)
- Error handling: try/except ở service layer, raise ở model layer
- Dùng `pathlib.Path` cho file paths
- Constants/configs đặt ở đầu file hoặc trong file config riêng

### 6.2 Naming
- Files: snake_case (knn_model.py)
- Classes: PascalCase (ItemKNN, SVDModel)
- Functions/methods: snake_case (get_neighbors)
- Constants: UPPER_SNAKE_CASE (DEFAULT_K = 30)

### 6.3 Import order
1. Standard library
2. Third-party (pandas, numpy, surprise, gradio)
3. Local modules (src.data, src.models, src.services)
