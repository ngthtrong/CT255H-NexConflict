# Chi tiết Thuật toán - Movie Recommendation

## Tổng quan Pipeline

```
[User Input] → [Onboarding Quiz] → [User Profile Vector]
                                          ↓
[MovieLens Data] → [Preprocessing] → [Train Models]
                                          ↓
                              ┌───────────┴───────────┐
                              ↓                       ↓
                        [Item-KNN]               [SVD Model]
                              ↓                       ↓
                              └───────────┬───────────┘
                                          ↓
                                  [Hybrid Scoring]
                                          ↓
                                  [Top-N Results]
                                          ↓
                              [Explanation Generator]
                                          ↓
                                  [Gradio UI Display]
```

---

## 1. Item-based KNN (Collaborative Filtering)

### Mô tả
- Tìm các phim tương tự dựa trên pattern đánh giá của tất cả users
- Nếu user thích phim A, gợi ý phim B mà "giống" phim A nhất

### Công thức
```
similarity(i, j) = cosine(r_i, r_j) = (r_i · r_j) / (||r_i|| × ||r_j||)

predicted_rating(u, i) = Σ [sim(i, j) × rating(u, j)] / Σ |sim(i, j)|
                         j∈N(i)
```
- `r_i`: vector rating của tất cả users cho item i
- `N(i)`: K láng giềng gần nhất của item i

### Hyperparameters cần tune
| Parameter | Range thử | Mặc định |
|---|---|---|
| K (số neighbors) | 10, 20, 30, 50, 100 | 30 |
| Similarity metric | cosine, pearson | cosine |
| Min common users | 5, 10, 20 | 10 |

### Thư viện & Implementation
```python
from surprise import KNNBaseline, KNNWithMeans

algo_knn = KNNBaseline(
    k=30,
    sim_options={
        'name': 'cosine',
        'user_based': False  # Item-based
    }
)
```

### Ưu điểm
- Dễ hiểu, dễ giải thích cho user
- Không cần training nặng
- Kết quả tốt với explicit ratings

### Nhược điểm
- Chậm khi scale lên (O(n²) similarity matrix)
- Cold-start: không gợi ý được phim mới chưa ai rate
- Sparse data → similarity không chính xác

---

## 2. SVD (Singular Value Decomposition)

### Mô tả
- Phân tích ma trận rating R(users × items) thành tích của 2 ma trận nhỏ hơn
- Học latent factors (đặc trưng ẩn) cho mỗi user và item
- Ví dụ latent factor: "yêu thích action", "thích phim dài", "prefer classic"

### Công thức
```
R ≈ P × Q^T

predicted_rating(u, i) = μ + b_u + b_i + p_u · q_i
```
- `μ`: rating trung bình toàn hệ thống
- `b_u`: bias của user u (user hay rate cao/thấp)
- `b_i`: bias của item i (phim hay được rate cao/thấp)
- `p_u`: latent vector của user (kích thước f)
- `q_i`: latent vector của item (kích thước f)

### Hyperparameters cần tune
| Parameter | Range thử | Mặc định |
|---|---|---|
| n_factors | 50, 100, 150, 200 | 100 |
| n_epochs | 20, 30, 50 | 20 |
| lr_all (learning rate) | 0.002, 0.005, 0.01 | 0.005 |
| reg_all (regularization) | 0.02, 0.05, 0.1 | 0.02 |

### Thư viện & Implementation
```python
from surprise import SVD

algo_svd = SVD(
    n_factors=100,
    n_epochs=20,
    lr_all=0.005,
    reg_all=0.02
)
```

### Ưu điểm
- Capture latent patterns tốt hơn KNN
- Faster prediction (chỉ cần dot product)
- Xử lý sparsity tốt hơn

### Nhược điểm
- Khó giải thích (latent factors trừu tượng)
- Cần retrain khi có data mới
- Cold-start cho cả user và item mới

---

## 3. Hybrid Scoring

### Công thức kết hợp
```
final_score(u, i) = α × svd_score(u, i) + β × knn_score(u, i)
```

### Trọng số đề xuất
| Cấu hình | α (SVD) | β (KNN) | Khi nào dùng |
|---|---|---|---|
| SVD-heavy | 0.65 | 0.35 | User có nhiều ratings |
| KNN-heavy | 0.35 | 0.65 | User ít ratings, cần giải thích |
| Balanced | 0.50 | 0.50 | Mặc định |

### Tune trọng số
- Dùng validation set
- Grid search trên α ∈ [0.3, 0.4, 0.5, 0.6, 0.7]
- Tối ưu theo NDCG@10

---

## 4. Cold-Start: Onboarding Quiz

### Flow
```
1. User mới → Hiển thị danh sách genres
2. User chọn 2-5 genres yêu thích
3. Hiển thị 10-15 phim phổ biến từ genres đã chọn
4. User đánh giá (1-5 sao) ít nhất 5 phim
5. Tạo user profile tạm → Chạy SVD/KNN predict
```

### Implementation
```python
def onboarding_recommend(selected_genres, rated_movies):
    # Bước 1: Filter phim theo genre
    candidates = movies[movies['genres'].str.contains('|'.join(selected_genres))]

    # Bước 2: Nếu đủ ratings → dùng SVD predict
    if len(rated_movies) >= 5:
        # Tạo pseudo-user, predict cho tất cả candidates
        predictions = [svd.predict(new_user_id, mid) for mid in candidates.movieId]
        return sorted(predictions, key=lambda x: x.est, reverse=True)[:10]

    # Bước 3: Fallback → popularity trong genres
    return candidates.sort_values('avg_rating', ascending=False).head(10)
```

---

## 5. Giải thích Gợi ý (Explainability)

### Template-based Explanations
```python
EXPLANATION_TEMPLATES = {
    'knn': "Vì bạn thích '{liked_movie}', phim này có pattern đánh giá tương tự (similarity: {sim:.0%})",
    'svd': "Dựa trên sở thích của bạn, model dự đoán bạn sẽ đánh giá phim này {rating:.1f}/5",
    'genre': "Phù hợp với thể loại yêu thích của bạn: {genres}",
    'popular': "Phim được đánh giá cao bởi {count} người dùng (avg: {avg:.1f}/5)"
}
```

### Logic chọn explanation
1. Nếu KNN contribution cao → dùng template 'knn' + tên phim tương tự
2. Nếu SVD contribution cao → dùng template 'svd' + predicted rating
3. Nếu có genre match → thêm template 'genre'

---

## 6. Evaluation Metrics

### Regression Metrics (Rating Prediction)
```python
# RMSE - Root Mean Square Error (càng thấp càng tốt)
RMSE = sqrt(mean((actual - predicted)²))

# MAE - Mean Absolute Error (càng thấp càng tốt)
MAE = mean(|actual - predicted|)
```

### Ranking Metrics (Top-N Recommendation)
```python
# Precision@K: Trong K phim gợi ý, bao nhiêu % user thật sự thích
Precision@K = |relevant ∩ recommended@K| / K

# Recall@K: Trong tất cả phim user thích, bao nhiêu % nằm trong top-K
Recall@K = |relevant ∩ recommended@K| / |relevant|

# NDCG@K: Thứ tự quan trọng, phim tốt nên ở vị trí đầu
# DCG@K = Σ (2^rel_i - 1) / log2(i + 1)
# NDCG@K = DCG@K / IDCG@K
```

### Coverage & Diversity
```python
# Coverage: Tỷ lệ phim unique được gợi ý / tổng số phim
Coverage = |unique recommended items| / |all items|

# Diversity: Trung bình khoảng cách giữa các phim trong list gợi ý
Intra-List Diversity = mean(1 - similarity(i, j)) for all pairs in top-K
```

### Baseline so sánh
| Model | Mô tả |
|---|---|
| Random | Gợi ý ngẫu nhiên |
| Popularity | Top phim có nhiều rating cao nhất |
| Item-KNN | Collaborative filtering, item-based |
| SVD | Matrix Factorization |
| Hybrid (KNN+SVD) | Kết hợp weighted score |

### Target Metrics (ước tính)
| Metric | Popularity | KNN | SVD | Hybrid |
|---|---|---|---|---|
| RMSE | ~1.0 | ~0.90 | ~0.87 | ~0.85 |
| Precision@10 | ~0.20 | ~0.30 | ~0.33 | ~0.35 |
| NDCG@10 | ~0.25 | ~0.35 | ~0.38 | ~0.40 |
