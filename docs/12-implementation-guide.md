# Hướng dẫn Implementation - Vibe Coding Guide

> File này chứa các prompt/hướng dẫn chi tiết cho từng bước coding.
> Dùng file này khi bắt đầu code từng phần của dự án.

---

## Phase 1: Setup & Data Preprocessing

### Step 1.1: Project Setup
```
Mục tiêu: Tạo cấu trúc thư mục, cài dependencies
Thời gian: ~30 phút

Việc cần làm:
1. Tạo cấu trúc thư mục theo docs/11-tech-stack.md
2. Tạo requirements.txt và pip install
3. Tạo file __init__.py cho các package
4. Test import thành công
```

### Step 1.2: Data Loader
```
Mục tiêu: Load MovieLens data, sampling, basic EDA
File: src/data/loader.py
Thời gian: ~1 giờ

Việc cần làm:
1. Hàm load_ratings(): đọc rating.csv, parse timestamp
2. Hàm load_movies(): đọc movie.csv, parse genres thành list
3. Hàm sample_data(n_users=5000): lấy mẫu ngẫu nhiên users
4. Hàm get_stats(): in thống kê cơ bản (số users, items, sparsity)

Lưu ý:
- Dùng dtype tối ưu (int32 cho userId/movieId, float32 cho rating)
- Trả về pandas DataFrame
- Sample 5000 users cho dev, có thể tăng lên khi cần
```

### Step 1.3: Data Preprocessor
```
Mục tiêu: Clean data, feature engineering, train/val split
File: src/data/preprocessor.py
Thời gian: ~1.5 giờ

Việc cần làm:
1. filter_sparse(min_user_ratings=20, min_item_ratings=10)
2. create_genre_features(): multi-hot encoding cho genres
3. time_split(train_ratio=0.8): split theo timestamp
4. create_surprise_dataset(): convert sang Surprise format
5. get_popular_movies(n=50): top phim phổ biến nhất (cho onboarding)
6. get_movies_by_genre(genre): filter phim theo genre

Lưu ý:
- Cache processed data bằng joblib hoặc pickle
- Log thống kê trước/sau filter
```

---

## Phase 2: Model Training

### Step 2.1: Item-based KNN Model
```
Mục tiêu: Train Item-KNN, evaluate baseline
File: src/models/knn_model.py
Thời gian: ~1.5 giờ

Việc cần làm:
1. Class ItemKNN:
   - __init__(k=30, sim='cosine')
   - train(trainset): fit model
   - predict(user_id, movie_id): single prediction
   - get_neighbors(movie_id, k=10): tìm k phim tương tự nhất
   - recommend(user_id, n=10): top-N recommendations
   - save(path) / load(path): serialize model

2. Dùng surprise.KNNBaseline hoặc KNNWithMeans
3. Lưu similarity matrix để dùng cho explanation
4. Test: train trên sample, in top-10 cho 1 user

Lưu ý:
- user_based=False (Item-based)
- Lưu model bằng joblib vào artifacts/
```

### Step 2.2: SVD Model
```
Mục tiêu: Train SVD, evaluate và so sánh với KNN
File: src/models/svd_model.py
Thời gian: ~1.5 giờ

Việc cần làm:
1. Class SVDModel:
   - __init__(n_factors=100, n_epochs=20, lr=0.005, reg=0.02)
   - train(trainset)
   - predict(user_id, movie_id)
   - recommend(user_id, n=10, candidate_ids=None)
   - get_user_vector(user_id): trả về latent vector
   - get_item_vector(movie_id): trả về latent vector
   - save(path) / load(path)

2. Dùng surprise.SVD
3. Test: train, so sánh RMSE với KNN

Lưu ý:
- Có thể tune hyperparams bằng GridSearchCV của Surprise
- Lưu model vào artifacts/
```

### Step 2.3: Hybrid Model
```
Mục tiêu: Kết hợp KNN + SVD scores
File: src/models/hybrid.py
Thời gian: ~1 giờ

Việc cần làm:
1. Class HybridRecommender:
   - __init__(knn_model, svd_model, alpha=0.5)
   - recommend(user_id, n=10):
     * Lấy candidate movies (user chưa rate)
     * Score = alpha * svd_score + (1-alpha) * knn_score
     * Normalize scores về [0, 1] trước khi combine
     * Return top-N sorted by final score
   - tune_alpha(val_data): tìm alpha tốt nhất trên validation

Lưu ý:
- Handle trường hợp model predict lỗi (unknown user/item)
- Fallback sang single model nếu model kia fail
```

---

## Phase 3: Services

### Step 3.1: Recommender Service
```
Mục tiêu: Service chính kết nối model với UI
File: src/services/recommender.py
Thời gian: ~1 giờ

Việc cần làm:
1. Class RecommenderService:
   - __init__(): load models và data khi khởi tạo
   - recommend_for_new_user(genres, ratings_dict): cold-start
   - recommend_for_user(user_id, n=10): existing user
   - get_movie_details(movie_id): thông tin phim

2. Load artifacts/ models khi init
3. Cache movie metadata trong memory

Lưu ý:
- Singleton pattern (chỉ load model 1 lần)
- Handle errors gracefully
```

### Step 3.2: Explanation Service
```
Mục tiêu: Giải thích tại sao gợi ý phim
File: src/services/explainer.py
Thời gian: ~45 phút

Việc cần làm:
1. Class ExplainService:
   - explain(user_id, movie_id, scores_breakdown):
     * Xác định model nào contribute nhiều nhất
     * Nếu KNN: tìm phim tương tự nhất mà user đã rate cao
     * Nếu SVD: dùng predicted rating
     * Thêm genre match info
     * Return explanation string

2. Templates tiếng Việt + tiếng Anh
```

### Step 3.3: Search Service
```
Mục tiêu: Tìm kiếm và lọc phim
File: src/services/search.py
Thời gian: ~30 phút

Việc cần làm:
1. search_movies(query, genre=None, min_rating=None, limit=20):
   - Tìm theo title (case-insensitive, partial match)
   - Filter theo genre nếu có
   - Filter theo min rating nếu có
   - Sort theo relevance / rating
```

---

## Phase 4: Gradio UI

### Step 4.1: Main App
```
Mục tiêu: Tạo Gradio app với tất cả tabs
File: src/app.py
Thời gian: ~2-3 giờ

Việc cần làm:
1. Tab "Onboarding":
   - gr.CheckboxGroup cho genres
   - gr.Slider hoặc gr.Radio cho rating từng phim
   - Button "Gợi ý phim cho tôi"
   - Output: gr.Dataframe hiển thị recommendations

2. Tab "Gợi ý phim":
   - Dropdown chọn user_id (cho demo với existing users)
   - Slider chọn số lượng N
   - Button "Lấy gợi ý"
   - Output: Dataframe + explanation text

3. Tab "Tìm kiếm":
   - Textbox search
   - Dropdown genre filter
   - Slider min rating
   - Output: Dataframe kết quả

4. Tab "Đánh giá Model" (optional):
   - Hiển thị comparison charts (gr.Plot)
   - Bảng metrics (gr.Dataframe)

Lưu ý:
- Dùng gr.Blocks() cho layout linh hoạt
- Theme: gr.themes.Soft() hoặc gr.themes.Default()
- Chạy: gradio src/app.py hoặc python src/app.py
```

---

## Phase 5: Evaluation

### Step 5.1: Evaluation Pipeline
```
Mục tiêu: Đánh giá và so sánh tất cả models
File: src/evaluation/evaluate.py
Thời gian: ~2 giờ

Việc cần làm:
1. evaluate_model(model, testset): tính RMSE, MAE
2. evaluate_topn(model, testset, n=10): Precision@K, Recall@K, NDCG@K
3. evaluate_coverage(model, all_items): Coverage %
4. evaluate_diversity(recommendations, similarity_matrix): ILD
5. compare_models(models_dict, testset): tạo comparison table
6. plot_comparison(results): tạo bar charts

Output:
- Console: bảng so sánh
- File: artifacts/evaluation_results.json
- Plots: artifacts/plots/ (PNG files)
```

---

## Thứ tự thực hiện (Priority Order)

```
Tuần 1 (Days 1-7):
  ✅ Step 1.1: Project Setup
  ✅ Step 1.2: Data Loader
  ✅ Step 1.3: Data Preprocessor
  ✅ Step 2.1: Item-KNN Model
  ✅ Step 2.2: SVD Model
  ✅ Step 5.1: Evaluation (baseline results)

Tuần 2 (Days 8-14):
  ✅ Step 2.3: Hybrid Model
  ✅ Step 3.1: Recommender Service
  ✅ Step 3.2: Explanation Service
  ✅ Step 3.3: Search Service
  ✅ Step 4.1: Gradio UI (basic)

Tuần 3 (Days 15-21):
  ✅ UI polish & bug fixes
  ✅ Final evaluation with comparison charts
  ✅ Evaluation tab in Gradio
  ✅ Demo preparation
  ✅ Báo cáo & slides
```

---

## Coding Prompts cho Vibe Coding

> Copy paste các prompt này khi bắt đầu code từng phần

### Prompt 1: Data Pipeline
```
Hãy tạo data pipeline cho MovieLens recommender app:
- File src/data/loader.py: load rating.csv và movie.csv, hàm sample 5000 users
- File src/data/preprocessor.py: filter sparse data, time-based train/val split,
  tạo Surprise dataset, lấy popular movies cho onboarding
- Tham khảo docs/10-algorithm-detail.md cho chi tiết
- Dữ liệu ở thư mục data/
```

### Prompt 2: KNN + SVD Models
```
Hãy tạo models cho recommender system:
- File src/models/knn_model.py: Item-based KNN wrapper dùng surprise.KNNBaseline
- File src/models/svd_model.py: SVD wrapper dùng surprise.SVD
- File src/models/hybrid.py: Hybrid kết hợp KNN + SVD với weighted scoring
- Mỗi model cần: train(), predict(), recommend(), save(), load()
- Tham khảo docs/10-algorithm-detail.md cho hyperparameters
```

### Prompt 3: Services
```
Hãy tạo services layer:
- File src/services/recommender.py: RecommenderService load models,
  recommend cho new user (onboarding) và existing user
- File src/services/explainer.py: sinh explanation text cho mỗi recommendation
- File src/services/search.py: tìm kiếm và lọc phim
- Tham khảo docs/11-tech-stack.md cho kiến trúc
```

### Prompt 4: Gradio UI
```
Hãy tạo Gradio app (src/app.py) với 4 tabs:
1. Onboarding: chọn genres + rate phim → nhận gợi ý
2. Recommendations: chọn user → xem top-N gợi ý với explanations
3. Search: tìm phim theo tên, filter genre/rating
4. Evaluation: hiển thị biểu đồ so sánh models
- Dùng gr.Blocks(), theme Soft
- Kết nối với RecommenderService
- Tham khảo docs/11-tech-stack.md cho UI layout
```

### Prompt 5: Evaluation
```
Hãy tạo evaluation pipeline:
- File src/evaluation/metrics.py: RMSE, MAE, Precision@K, Recall@K, NDCG@K, Coverage, Diversity
- File src/evaluation/evaluate.py: chạy đánh giá tất cả models, tạo comparison table và charts
- So sánh: Random, Popularity, Item-KNN, SVD, Hybrid
- Save kết quả vào artifacts/
- Tham khảo docs/10-algorithm-detail.md cho target metrics
```
