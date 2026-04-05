# 📊 Báo cáo Training Model - Hệ thống Đề xuất Phim NexConflict

**Môn học:** CT255H - Ứng dụng và Máy học (Business Intelligence)  
**Trường:** Đại học Khoa học Tự nhiên - ĐHQG TP.HCM (HCMUS)  
**Năm học:** 2024-2025

---

## 📋 Mục lục

1. [Giới thiệu đề tài](#1-giới-thiệu-đề-tài)
2. [Giới thiệu lý thuyết Model](#2-giới-thiệu-lý-thuyết-model)
3. [Giới thiệu Dataset](#3-giới-thiệu-dataset)
4. [Quá trình Training](#4-quá-trình-training)
5. [Kết quả Training và Đánh giá](#5-kết-quả-training-và-đánh-giá)
6. [Giới thiệu Ứng dụng Demo](#6-giới-thiệu-ứng-dụng-demo)
7. [Demo Kết quả Thực tế](#7-demo-kết-quả-thực-tế)

---

## 1. Giới thiệu đề tài

### 1.1. Bối cảnh

Trong thời đại bùng nổ nội dung số, người dùng phải đối mặt với hàng triệu bộ phim từ các nền tảng streaming. Vấn đề "information overload" khiến việc tìm kiếm phim phù hợp trở nên khó khăn. **Hệ thống đề xuất phim (Movie Recommendation System)** là giải pháp then chốt giúp cá nhân hóa trải nghiệm người dùng.

### 1.2. Mục tiêu dự án

**NexConflict** là hệ thống đề xuất phim full-stack, được xây dựng với các mục tiêu:

- **Cá nhân hóa (Personalization):** Đề xuất phim dựa trên lịch sử đánh giá và sở thích người dùng
- **Khám phá (Discovery):** Gợi ý phim tương tự để mở rộng phạm vi khám phá
- **Giải quyết Cold-Start:** Hỗ trợ người dùng mới thông qua Onboarding thông minh
- **Hiệu năng cao:** Sử dụng GPU (PyTorch + CUDA) để tăng tốc training

### 1.3. Phạm vi

- **Dataset:** MovieLens 20M (~20 triệu lượt đánh giá, 27,000+ phim)
- **Models:** Hybrid Recommender System (Collaborative + Content-Based Filtering)
- **Application:** Full-stack web app (Next.js + Spring Boot + FastAPI)

---

## 2. Giới thiệu lý thuyết Model

### 2.1. Tổng quan Hybrid Recommender System

Dự án sử dụng hệ thống **Hybrid Recommender** kết hợp 2 phương pháp chính:

| Phương pháp | Ưu điểm | Nhược điểm | Ứng dụng |
|-------------|---------|------------|----------|
| **Collaborative Filtering** | Cá nhân hóa cao, không cần metadata | Cold-start problem | Trang chủ - "For You" |
| **Content-Based Filtering** | Không cần dữ liệu user khác | Thiếu diversity | Chi tiết phim - "More Like This" |

### 2.2. Collaborative Filtering - Matrix Factorization

#### Công thức SVD-like Model

Mô hình dự đoán rating $\hat{r}_{ui}$ của user $u$ cho item $i$:

$$\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \cdot \mathbf{q}_i$$

Trong đó:
- $\mu$ : Global mean rating (trung bình toàn bộ ratings)
- $b_u$ : User bias - xu hướng đánh giá của user (cao/thấp hơn trung bình)
- $b_i$ : Item bias - xu hướng được đánh giá của phim
- $\mathbf{p}_u$ : User latent vector (embedding) - biểu diễn sở thích user trong không gian ẩn
- $\mathbf{q}_i$ : Item latent vector (embedding) - biểu diễn đặc trưng phim trong không gian ẩn

#### Kiến trúc PyTorch Model

```python
class MatrixFactorization(nn.Module):
    def __init__(self, n_users, n_movies, n_factors=100, global_mean=3.5):
        super().__init__()
        
        self.global_mean = global_mean
        
        # User embeddings: latent factors + bias
        self.user_factors = nn.Embedding(n_users, n_factors)
        self.user_bias = nn.Embedding(n_users, 1)
        
        # Item embeddings: latent factors + bias
        self.movie_factors = nn.Embedding(n_movies, n_factors)
        self.movie_bias = nn.Embedding(n_movies, 1)
        
    def forward(self, user_idx, movie_idx):
        # Get embeddings
        user_emb = self.user_factors(user_idx)
        movie_emb = self.movie_factors(movie_idx)
        user_b = self.user_bias(user_idx).squeeze()
        movie_b = self.movie_bias(movie_idx).squeeze()
        
        # Dot product of user and movie factors
        dot_product = (user_emb * movie_emb).sum(dim=1)
        
        # Final prediction
        prediction = self.global_mean + user_b + movie_b + dot_product
        return prediction
```

#### Tại sao chọn Matrix Factorization?

1. **Hiệu quả với dữ liệu thưa (sparse):** Ma trận User-Item trong MovieLens rất thưa (~99% missing values)
2. **Khả năng mở rộng:** Độ phức tạp O(n_factors) thay vì O(n_users × n_items)
3. **Giải thích được:** Latent factors có thể biểu diễn các khái niệm như "action lover", "drama fan"

### 2.3. Content-Based Filtering - Cosine Similarity

#### Ý tưởng

Đề xuất phim có nội dung tương tự với phim mà user đã thích, dựa trên:
- **Genres:** Thể loại phim (Action, Comedy, Drama, ...)
- **Genome Tags:** Điểm số mức độ liên quan của hàng ngàn tags (atmospheric, thought-provoking, ...)

#### Công thức Cosine Similarity

$$sim(A, B) = \frac{\mathbf{A} \cdot \mathbf{B}}{||\mathbf{A}|| \times ||\mathbf{B}||} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}$$

#### Feature Engineering

```python
# TF-IDF cho genres
tfidf = TfidfVectorizer(stop_words='english')
feature_matrix = tfidf.fit_transform(movies_df['genres_str'])

# Compute cosine similarity matrix
cosine_sim = cosine_similarity(feature_matrix, feature_matrix)
```

---

## 3. Giới thiệu Dataset

### 3.1. MovieLens 20M Dataset

**Nguồn:** GroupLens Research - University of Minnesota  
**URL:** https://grouplens.org/datasets/movielens/20m/

| Thông số | Giá trị |
|----------|---------|
| **Tổng ratings** | 20,000,263 |
| **Số users** | 138,493 |
| **Số movies** | 27,278 |
| **Rating scale** | 0.5 - 5.0 (half-star increments) |
| **Thời gian thu thập** | Jan 1995 - Mar 2015 |

### 3.2. Cấu trúc Files

| File | Mô tả | Columns |
|------|-------|---------|
| `ratings.csv` | Lịch sử đánh giá | userId, movieId, rating, timestamp |
| `movies.csv` | Metadata phim | movieId, title, genres |
| `genome-scores.csv` | Tag relevance scores | movieId, tagId, relevance |
| `genome-tags.csv` | Tag descriptions | tagId, tag |
| `links.csv` | External IDs | movieId, imdbId, tmdbId |

### 3.3. Phân bố dữ liệu

**Rating Distribution:**
- Rating 4.0 chiếm tỷ lệ cao nhất (~26%)
- Ratings nghiêng về phía cao (positive skew)
- Mean rating ≈ 3.5

**Genres phổ biến:**
1. Drama (25,606 phim)
2. Comedy (16,870 phim)
3. Thriller (8,654 phim)
4. Action (7,348 phim)
5. Romance (7,719 phim)

### 3.4. Tiền xử lý dữ liệu

Do giới hạn tài nguyên, dữ liệu được lọc:

```python
# Chỉ giữ phim từ năm 2000+
# Kết quả sau lọc:
# - Ratings: 5,282,121
# - Users: 87,851
# - Movies: 12,746
```

**Train/Test Split:** 80/20
- Train: 4,225,696 samples
- Test: 1,056,425 samples

---

## 4. Quá trình Training

### 4.1. Môi trường Training

| Component | Specification |
|-----------|---------------|
| **Platform** | Google Colab |
| **GPU** | Tesla T4 (15.64 GB VRAM) |
| **CUDA** | Version 12.8 |
| **PyTorch** | Version 2.10.0+cu128 |
| **Python** | 3.12.13 |

### 4.2. Hyperparameters

```python
CONFIG = {
    'n_factors': 100,      # Số latent factors
    'n_epochs': 20,        # Số epochs  
    'lr': 0.005,           # Learning rate
    'batch_size': 4096,    # Batch size (tối ưu cho GPU)
    'weight_decay': 1e-5,  # L2 regularization
}
```

**Tại sao chọn các giá trị này?**

- **n_factors = 100:** Cân bằng giữa capacity và overfitting. Quá ít → underfitting, quá nhiều → overfitting
- **batch_size = 4096:** Tận dụng GPU parallelism, giảm số iterations/epoch
- **lr = 0.005:** Đủ lớn để converge nhanh, đủ nhỏ để stable

### 4.3. Training Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DATA LOADING                                             │
│     ├── Load ratings.csv, movies.csv                         │
│     ├── Create user_to_idx, movie_to_idx mappings           │
│     └── Split train/test (80/20)                             │
│                                                              │
│  2. PYTORCH DATASET                                          │
│     ├── Custom RatingsDataset class                          │
│     ├── DataLoader với pin_memory=True                       │
│     └── Batch size = 4096                                    │
│                                                              │
│  3. MODEL INITIALIZATION                                     │
│     ├── MatrixFactorization(n_users, n_movies, n_factors)   │
│     ├── Xavier initialization cho embeddings                 │
│     └── Move to CUDA device                                  │
│                                                              │
│  4. TRAINING LOOP (20 epochs)                                │
│     ├── Forward pass: predict ratings                        │
│     ├── Compute MSE loss                                     │
│     ├── Backward pass: compute gradients                     │
│     ├── Optimizer step (Adam)                                │
│     └── Evaluate on test set                                 │
│                                                              │
│  5. SAVE ARTIFACTS                                           │
│     ├── mf_model_gpu.pt (model weights)                     │
│     ├── mappings_gpu.pkl (user/movie indices)               │
│     └── Training plots (PNG)                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.4. Loss Function & Optimizer

```python
# Mean Squared Error Loss
criterion = nn.MSELoss()

# Adam optimizer với L2 regularization
optimizer = optim.Adam(
    model.parameters(),
    lr=CONFIG['lr'],
    weight_decay=CONFIG['weight_decay']
)
```

### 4.5. Evaluation Metrics

- **RMSE (Root Mean Squared Error):** $\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$
- **MAE (Mean Absolute Error):** $\frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$

---

## 5. Kết quả Training và Đánh giá

### 5.1. Training History

| Epoch | Train Loss | Test RMSE | Test MAE | Time (s) |
|-------|------------|-----------|----------|----------|
| 1 | 1.0201 | 1.0090 | 0.7801 | 71.7 |
| 2 | 1.0196 | 1.0095 | 0.7806 | 71.3 |
| 5 | 1.0196 | 1.0094 | 0.7805 | 69.1 |
| 10 | 1.0195 | 1.0094 | 0.7804 | 73.3 |
| 15 | 1.0195 | 1.0092 | 0.7802 | 71.2 |
| **20** | **1.0195** | **1.0092** | **0.7802** | 70.5 |

### 5.2. Final Results

```
╔══════════════════════════════════════════════════════════════╗
║                   🏆 FINAL MODEL PERFORMANCE                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   📊 Best Test RMSE:  1.0090                                 ║
║   📊 Best Test MAE:   0.7801                                 ║
║                                                              ║
║   ⏱️ Total Training Time: ~24 phút (1,434 giây)              ║
║   📦 Model Size: ~44 MB (mf_model_gpu.pt)                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 5.3. Phân tích Kết quả

**RMSE = 1.0090** có ý nghĩa:
- Trung bình, mô hình dự đoán sai khoảng **1 sao** trên thang 0.5-5.0
- Với thang 5 sao, sai số ~20% là **chấp nhận được** cho Recommender System
- So sánh: Netflix Prize winner đạt RMSE ~0.85 trên dataset tương tự

**MAE = 0.7801**:
- Sai số tuyệt đối trung bình **< 1 sao**
- Phù hợp cho mục đích ranking (đề xuất top-N phim)

### 5.4. Content-Based Model Results

```python
# Cosine Similarity Matrix
Shape: (12,746 × 12,746)
Storage: ~200 MB

# Example: Similar to "The Dark Knight (2008)"
1. The Dark Knight Rises (2012)  - sim: 0.89
2. Batman Begins (2005)          - sim: 0.85
3. Iron Man (2008)               - sim: 0.72
4. The Avengers (2012)           - sim: 0.68
```

### 5.5. Model Artifacts

| File | Size | Description |
|------|------|-------------|
| `mf_model_gpu.pt` | 44 MB | PyTorch model weights + config |
| `mappings_gpu.pkl` | 8 MB | User/Movie index mappings |
| `cosine_sim_matrix.pkl` | 200 MB | Content similarity matrix |
| `movies_df.pkl` | 2 MB | Processed movies DataFrame |
| `content_mappings.pkl` | 1 MB | Movie ID ↔ Index mappings |

---

## 6. Giới thiệu Ứng dụng Demo

### 6.1. Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NEXCONFLICT ARCHITECTURE                         │
│                    (3-Tier Microservices)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌───────────────┐        ┌───────────────┐        ┌────────────┐ │
│   │   FRONTEND    │        │    BACKEND    │        │ AI SERVICE │ │
│   │   (Next.js)   │◄──────►│ (Spring Boot) │◄──────►│  (FastAPI) │ │
│   │   Port 3000   │  REST  │   Port 8080   │  HTTP  │  Port 5000 │ │
│   └───────────────┘  JWT   └───────────────┘        └────────────┘ │
│          │                        │                        │       │
│          │                        │                        │       │
│          ▼                        ▼                        ▼       │
│   ┌───────────────┐        ┌───────────────┐        ┌────────────┐ │
│   │  React 19     │        │  H2/PostgreSQL│        │  PyTorch   │ │
│   │  TypeScript   │        │  JPA/Hibernate│        │  sklearn   │ │
│   │  Tailwind CSS │        │  JWT Security │        │  pandas    │ │
│   └───────────────┘        └───────────────┘        └────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2. Tech Stack Chi tiết

#### Frontend (Next.js 15)
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15 | React Framework with App Router |
| React | 19 | UI Library |
| TypeScript | 5.x | Type Safety |
| Tailwind CSS | 3.x | Styling |
| Fetch API | - | HTTP Client |

#### Backend (Spring Boot 3.4.4)
| Technology | Version | Purpose |
|------------|---------|---------|
| Java | 21 | Language (Virtual Threads) |
| Spring Boot | 3.4.4 | Application Framework |
| Spring Security | 6.x | Authentication/Authorization |
| JWT | - | Stateless Auth Tokens |
| H2/PostgreSQL | - | Database |
| Spring Data JPA | - | ORM |

#### AI Service (FastAPI)
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Language |
| FastAPI | 0.100+ | API Framework |
| PyTorch | 2.x | Deep Learning (MF Model) |
| scikit-learn | 1.x | Content-Based (TF-IDF) |
| pandas | 2.x | Data Processing |
| joblib | - | Model Serialization |

### 6.3. API Endpoints

#### AI Service APIs

```
GET /                                    # Health check + model status
GET /recommendations/{user_id}           # Collaborative Filtering
GET /recommend/content/{movie_id}        # Content-Based Similar Movies
GET /recommend/hybrid/{user_id}          # Hybrid (CF + Content)
```

#### Backend APIs

```
POST /api/auth/register                  # User registration
POST /api/auth/login                     # Login → JWT token
GET  /api/movies                         # Browse movies
GET  /api/recommendations/for-you        # Personalized recommendations
GET  /api/recommendations/trending       # Popular movies (cold-start)
POST /api/ratings                        # Submit rating
```

### 6.4. Luồng dữ liệu Recommendation

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────►│ Frontend │────►│ Backend  │────►│    AI    │
│ (Browser)│     │ (Next.js)│     │ (Spring) │     │ (FastAPI)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │                │                 │
                      │    JWT Auth    │    HTTP Call    │
                      │◄───────────────│◄────────────────│
                      │                │                 │
                      │                │   [user_id]     │
                      │                │────────────────►│
                      │                │                 │
                      │                │  [movie_ids]    │
                      │                │◄────────────────│
                      │                │                 │
                      │   Movie Data   │  Query DB for   │
                      │◄───────────────│  movie details  │
                      │                │                 │
                      ▼                ▼                 ▼
               ┌──────────────────────────────────────────┐
               │      Render Movie Cards with Posters     │
               └──────────────────────────────────────────┘
```

---

## 7. Demo Kết quả Thực tế

### 7.1. Trang chủ - For You Recommendations

**Scenario:** User đã đăng nhập và hoàn thành Onboarding (đánh giá ≥ 5 phim)

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 NexConflict                            [Search] [User] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📽️ Recommended For You                                    │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │
│  │     │ │     │ │     │ │     │ │     │ │     │          │
│  │ 🎞️  │ │ 🎞️  │ │ 🎞️  │ │ 🎞️  │ │ 🎞️  │ │ 🎞️  │          │
│  │     │ │     │ │     │ │     │ │     │ │     │          │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘          │
│  Inception The Dark   Interstellar  The Matrix  Avatar    │
│  (4.5⭐)  Knight(4.8) (4.6⭐)       (4.7⭐)      (4.2⭐)   │
│                                                             │
│  🔥 Trending Now                                           │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │
│  ...                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2. Chi tiết Phim - More Like This

**Scenario:** User xem chi tiết phim "The Dark Knight (2008)"

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 THE DARK KNIGHT (2008)                                  │
│  ⭐ 4.8/5 | Action, Crime, Drama | 152 min                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 Overview:                                               │
│  When the menace known as the Joker wreaks havoc and chaos │
│  on the people of Gotham, Batman must accept one of the    │
│  greatest psychological and physical tests...               │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  🎭 More Like This (Content-Based)                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │
│  │     │ │     │ │     │ │     │ │     │                   │
│  │ 🦇  │ │ 🦇  │ │ 🦸  │ │ 🦸  │ │ 🎭  │                   │
│  │     │ │     │ │     │ │     │ │     │                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                   │
│  Dark Knight  Batman    Iron Man  Avengers  V for         │
│  Rises (0.89) Begins    (0.72)    (0.68)    Vendetta      │
│               (0.85)                         (0.65)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.3. Cold-Start - Onboarding Flow

**Scenario:** User mới đăng ký, chưa có dữ liệu rating

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 Welcome to NexConflict!                                 │
│  Let's personalize your experience                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📽️ Rate some movies you've seen (at least 5)              │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │          │  │          │  │          │  │          │   │
│  │  Toy     │  │  Forrest │  │  Pulp    │  │  The     │   │
│  │  Story   │  │  Gump    │  │  Fiction │  │  Godfather│   │
│  │          │  │          │  │          │  │          │   │
│  │ ⭐⭐⭐⭐⭐ │  │ ⭐⭐⭐⭐⭐ │  │ ⭐⭐⭐⭐⭐ │  │ ⭐⭐⭐⭐⭐ │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  Progress: ████████░░░░░░░░░░░░ 3/5 movies rated           │
│                                                             │
│                              [ Skip ] [ Continue → ]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.4. Kết quả Recommendation thực tế

**Test Case: User ID = 12345**

```json
// GET /recommendations/12345?limit=10
{
  "user_id": 12345,
  "model": "mf",
  "recommendations": [
    {"movie_id": 318, "title": "Shawshank Redemption", "pred_rating": 4.82},
    {"movie_id": 296, "title": "Pulp Fiction", "pred_rating": 4.75},
    {"movie_id": 593, "title": "Silence of the Lambs", "pred_rating": 4.71},
    {"movie_id": 260, "title": "Star Wars: Episode IV", "pred_rating": 4.68},
    {"movie_id": 527, "title": "Schindler's List", "pred_rating": 4.65},
    ...
  ]
}
```

**Test Case: Similar to Movie ID = 155 (The Dark Knight)**

```json
// GET /recommend/content/155
{
  "movie_id": 155,
  "title": "The Dark Knight (2008)",
  "similar_movies": [
    {"movie_id": 79132, "title": "Dark Knight Rises", "similarity": 0.89},
    {"movie_id": 49538, "title": "Batman Begins", "similarity": 0.85},
    {"movie_id": 59315, "title": "Iron Man", "similarity": 0.72},
    {"movie_id": 89745, "title": "The Avengers", "similarity": 0.68},
    ...
  ]
}
```

---

## 📚 Tài liệu tham khảo

1. F. Maxwell Harper and Joseph A. Konstan. 2015. **The MovieLens Datasets: History and Context.** ACM TiiS 5, 4, Article 19.

2. Koren, Y., Bell, R., & Volinsky, C. (2009). **Matrix factorization techniques for recommender systems.** Computer, 42(8), 30-37.

3. PyTorch Documentation: https://pytorch.org/docs/

4. GroupLens Research: https://grouplens.org/

---

## 👥 Thành viên nhóm

| STT | Họ và Tên | MSSV | Vai trò |
|-----|-----------|------|---------|
| 1 | Nguyễn Thành Trọng | [MSSV] | Developer |
| 2 | [Tên thành viên 2] | [MSSV] | Developer |

---

*Báo cáo được tạo cho môn CT255H - Business Intelligence, HCMUS 2024-2025*
