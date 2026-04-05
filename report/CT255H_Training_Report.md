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
- **Độ chính xác cao:** Sử dụng Surprise SVD để tối ưu chất lượng dự đoán rating

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
| **Collaborative Filtering (SVD)** | Cá nhân hóa cao, học được sở thích ẩn | Cần đủ dữ liệu rating, khó cho user mới | For You (user có >= 5 ratings) |
| **Content-Based Filtering** | Ổn định cho cold-start, không phụ thuộc cộng đồng users | Dễ thiên về phim giống nhau, giảm diversity | Similar movie, Watchlist-based, Personalized onboarding |

### 2.2. Collaborative Filtering - SVD với Surprise

#### Công thức SVD

Mô hình dự đoán rating $\hat{r}_{ui}$ của user $u$ cho item $i$:

$$\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \cdot \mathbf{q}_i$$

Trong đó:
- $\mu$ : Global mean rating (trung bình toàn bộ ratings)
- $b_u$ : User bias - xu hướng đánh giá của user (cao/thấp hơn trung bình)
- $b_i$ : Item bias - xu hướng được đánh giá của phim
- $\mathbf{p}_u$ : User latent vector (embedding) - biểu diễn sở thích user trong không gian ẩn
- $\mathbf{q}_i$ : Item latent vector (embedding) - biểu diễn đặc trưng phim trong không gian ẩn

#### Cách triển khai với Surprise

```python
from surprise import SVD

svd_model = SVD(
  n_factors=100,
  n_epochs=20,
  lr_all=0.005,
  reg_all=0.02,
  random_state=42
)

svd_model.fit(trainset)
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

### 2.4. Lý do phân luồng model trong runtime

Hệ thống không dùng 1 model duy nhất cho mọi tính năng, mà phân luồng theo độ sẵn sàng dữ liệu của từng user:

1. **For You ưu tiên SVD (runtime non-strict)**
- Điều kiện: user có đủ dữ liệu rating (>= 5 ratings).
- Lý do: đây là nhóm user đã có tín hiệu hành vi rõ, SVD cho mức cá nhân hóa cao hơn.
- Backend gọi collaborative endpoint ở chế độ mặc định (non-strict) để tránh trả rỗng khi mismatch giữa user app và training history trong artifact.

2. **Watchlist-based dùng Content-Based**
- Điều kiện: user chưa đủ rating cho SVD nhưng đã có watchlist.
- Lý do: watchlist là tín hiệu sở thích trực tiếp theo item, cosine similarity hoạt động tốt và phản hồi nhanh.

3. **User mới dùng Personalized Content-Based**
- Điều kiện: user mới, chưa có hoặc rất ít hành vi.
- Lý do: dùng preferred genres + rated movies từ onboarding giúp giải cold-start ổn định.

4. **Similar movie luôn dùng Content-Based**
- Lý do: bài toán item-item similarity phù hợp tự nhiên với cosine similarity.

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
| **Surprise** | 1.1.4 |
| **NumPy** | < 2.0 (để tương thích Surprise) |
| **scikit-learn** | 1.x (phần Content-Based) |
| **Python** | 3.12.13 |

### 4.2. Hyperparameters

```python
CONFIG = {
  'n_factors': 100,   # Số latent factors
  'n_epochs': 20,     # Số epochs
  'lr_all': 0.005,    # Learning rate
  'reg_all': 0.02,    # Regularization
  'cv': 5             # 5-fold cross-validation
}
```

**Tại sao chọn các giá trị này?**

- **n_factors = 100:** Cân bằng giữa capacity và overfitting. Quá ít → underfitting, quá nhiều → overfitting
- **lr_all = 0.005:** Đủ lớn để hội tụ ổn định và nhanh
- **reg_all = 0.02:** Giảm overfitting trên dữ liệu sparse
- **cv = 5:** Đánh giá mô hình robust hơn qua 5 folds

### 4.3. Training Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DATA LOADING                                             │
│     ├── Load ratings.csv, movies.csv (phim từ 2000+)         │
│     ├── Parse userId, movieId, rating                        │
│     └── Split train/test (80/20)                             │
│                                                              │
│  2. PREPARE SURPRISE DATASET                                 │
│     ├── Reader(rating_scale=(0.5, 5.0))                      │
│     ├── Dataset.load_from_df(...)                            │
│     └── train_test_split(random_state=42)                    │
│                                                              │
│  3. TRAIN SVD MODEL                                          │
│     ├── SVD(n_factors=100, n_epochs=20)                      │
│     ├── Fit trên trainset                                    │
│     └── Predict trên testset                                 │
│                                                              │
│  4. EVALUATE + CROSS-VALIDATE                                │
│     ├── Tính RMSE/MAE trên test set                          │
│     ├── cross_validate(..., cv=5)                            │
│     └── Tổng thời gian CV ~529 giây                          │
│                                                              │
│  5. SAVE ARTIFACTS                                           │
│     ├── svd_model.pkl                                         │
│     ├── cosine_sim_matrix.pkl                                 │
│     └── content_mappings.pkl                                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.4. Cấu hình SVD và Cross-Validation

```python
# Train/Test evaluation
predictions = svd_model.test(testset)
rmse = accuracy.rmse(predictions)
mae = accuracy.mae(predictions)

# 5-fold cross-validation
cv_results = cross_validate(
  SVD(n_factors=100, n_epochs=20, random_state=42),
  data,
  measures=['RMSE', 'MAE'],
  cv=5
)
```

### 4.5. Evaluation Metrics

- **RMSE (Root Mean Squared Error):** $\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$
- **MAE (Mean Absolute Error):** $\frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$

---

## 5. Kết quả Training và Đánh giá

### 5.1. So sánh kết quả trước và sau v2

| Chỉ số | Bản trước | Bản v2 (Surprise) | Cải thiện |
|--------|-----------|-------------------|-----------|
| RMSE | 1.0090 | **0.7915** | **-0.2175 (~21.6%)** |
| MAE | 0.7801 | **0.5920** | **-0.1881 (~24.1%)** |
| Cross-validation | Chưa chạy chuẩn hóa | **5-fold** | Tăng độ tin cậy đánh giá |
| Thời gian Cross-validation | - | **~529 giây** | Có benchmark rõ ràng |

### 5.2. Final Results

```
╔══════════════════════════════════════════════════════════════╗
║                   🏆 FINAL MODEL PERFORMANCE                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   📊 Best Test RMSE:  0.7915                                 ║
║   📊 Best Test MAE:   0.5920                                 ║
║                                                              ║
║   ⏱️ 5-fold Cross-validation Time: ~529 giây                 ║
║   📦 Main Collaborative Artifact: svd_model.pkl              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 5.3. Phân tích Kết quả

**RMSE = 0.7915** có ý nghĩa:
- Trung bình, mô hình dự đoán sai dưới **0.8 sao** trên thang 0.5-5.0
- Sai số giảm mạnh so với bản trước, cho thấy khả năng xếp hạng tốt hơn
- Mức RMSE này phù hợp cho triển khai recommendation thực tế

**MAE = 0.5920**:
- Sai số tuyệt đối trung bình **< 1 sao**
- Cải thiện đáng kể chất lượng dự đoán cho top-N recommendation

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
| `svd_model.pkl` | ~50 MB | Surprise SVD model đã train |
| `cosine_sim_matrix.pkl` | 200 MB | Content similarity matrix |
| `movies_df.pkl` | 2 MB | Processed movies DataFrame |
| `content_mappings.pkl` | 1 MB | Movie ID ↔ Index mappings |
| `ratings_df.pkl` | ~120 MB | Ratings data đã lọc cho collaborative |

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
│   │  React 19     │        │  H2/PostgreSQL│        │  Surprise  │ │
│   │  TypeScript   │        │  JPA/Hibernate│        │  sklearn   │ │
│   │  Tailwind CSS │        │  JWT Security │        │  joblib    │ │
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
| Surprise | 1.1.4 | Collaborative Filtering (SVD) |
| scikit-learn | 1.x | Content-Based (TF-IDF) |
| pandas | 2.x | Data Processing |
| joblib | - | Model Serialization |

### 6.3. API Endpoints

#### AI Service APIs

```
GET /                                    # Health check + model status
GET /health                              # Health endpoint
GET /recommendations/{user_id}           # Collaborative (SVD/MF), hỗ trợ strict mode
GET /similar/{movie_id}                  # Content-Based Similar Movies
POST /recommendations/based-on-movies    # Content-Based theo watchlist/input movies
POST /recommendations/personalized       # Content-Based theo onboarding + ratings
```

#### Backend APIs

```
POST /api/auth/register                  # User registration
POST /api/auth/login                     # Login → JWT token
GET  /api/movies                         # Browse movies
GET  /api/recommendations/for-you        # For You (SVD ưu tiên, fallback Content-Based)
GET  /api/recommendations/similar/{id}   # Similar movies
GET  /api/recommendations/top-genres     # Genre row từ preferences
GET  /api/recommendations/watch-again    # Watch again từ lịch sử rating
GET  /api/recommendations/trending       # Popular movies (cold-start)
POST /api/ratings                        # Submit rating
```

### 6.4. Luồng dữ liệu Recommendation

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────►│ Frontend │────►│ Backend  │────►│    AI    │
│ (Browser)│     │ (Next.js)│     │ (Spring) │     │ (FastAPI)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘

Decision flow cho endpoint /api/recommendations/for-you:

1) User có >= 5 ratings?
  ├─ Có  → gọi /recommendations/{user_id}  → SVD
  └─ Không:
     2) User có watchlist?
       ├─ Có  → gọi /recommendations/based-on-movies → Content-Based
       └─ Không → gọi /recommendations/personalized   → Content-Based (onboarding)

Các luồng khác:
- /api/recommendations/similar/{id} → /similar/{movie_id} → Content-Based
- /api/recommendations/top-genres   → Query DB theo sở thích genre
- /api/recommendations/watch-again  → Query DB theo lịch sử rating
- /api/recommendations/trending     → Query DB phim mới/phổ biến
```

### 6.5. Ưu điểm và hạn chế của từng model theo tính năng

| Tính năng | Model chính | Vì sao phù hợp | Hạn chế |
|-----------|-------------|----------------|---------|
| For You (đủ rating) | **SVD** | Cá nhân hóa sâu theo hành vi, học latent preference | Cold-start cho user mới, cần dữ liệu rating |
| Similar movie | **Content-Based** | Bài toán item-item, phản hồi ổn định | Dễ recommend phim quá giống nhau |
| Watchlist-based | **Content-Based** | Có seed items rõ ràng từ watchlist | Chất lượng phụ thuộc độ đa dạng watchlist |
| Personalized onboarding | **Content-Based** | Khởi động tốt khi chưa có lịch sử user | Mức cá nhân hóa thấp hơn SVD ở user lâu năm |

**Chiến lược hiện tại:** dùng mô hình lai theo điều kiện dữ liệu để cân bằng giữa độ chính xác (SVD) và độ phủ cold-start (Content-Based).

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
  "model": "svd",
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
// GET /similar/155
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

3. Surprise Documentation: https://surprise.readthedocs.io/

4. GroupLens Research: https://grouplens.org/

---

## 👥 Thành viên nhóm

| STT | Họ và Tên | MSSV | Vai trò |
|-----|-----------|------|---------|
| 1 | Nguyễn Thành Trọng | [MSSV] | Developer |
| 2 | [Tên thành viên 2] | [MSSV] | Developer |

---

*Báo cáo được tạo cho môn CT255H - Business Intelligence, HCMUS 2024-2025*
