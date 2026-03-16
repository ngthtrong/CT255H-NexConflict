# AGENT 3: Services Layer + Gradio UI
# Vai trò: Kết nối models với UI, tạo giao diện Gradio

## BỐI CẢNH DỰ ÁN
Ứng dụng gợi ý phim chạy local, giao diện Gradio 4 tabs.
- Kiến trúc: docs/ARCHITECTURE.md
- UI Layout: docs/11-tech-stack.md (Section 4)
- Thuật toán: docs/10-algorithm-detail.md (Section 5 - Explainability)

## PHỤ THUỘC
- **Agent 1**: `src/data/` — loader.py, preprocessor.py
- **Agent 2**: `src/models/` — ItemKNN, SVDModel, HybridRecommender
- Models đã train và save tại `artifacts/`

## NHIỆM VỤ
Tạo 5 file:
1. `src/services/__init__.py`
2. `src/services/recommender.py` — Main recommendation orchestrator
3. `src/services/explainer.py` — Explanation generation
4. `src/services/search.py` — Movie search & filter
5. `src/app.py` — Gradio UI entry point

## RÀNG BUỘC
- Gradio gọi trực tiếp Python functions (KHÔNG qua HTTP)
- RecommenderService là singleton (load models 1 lần khi init)
- UI tiếng Việt (labels, explanations)
- Dùng `gr.Blocks()` cho layout, theme `gr.themes.Soft()`
- Logging, type hints, docstrings

---

## FILE 1: src/services/recommender.py

### Class RecommenderService:

```python
class RecommenderService:
    """
    Main service kết nối data layer và model layer.
    Singleton: load models 1 lần duy nhất.
    """

    _instance = None  # Singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Nếu chưa initialized:
        1. Load processed data (movies_info, genre_list, popular_movies)
        2. Load trained models từ artifacts/ (knn, svd, hybrid)
        3. Load trainset reference (cần cho predict)
        """

    def recommend_for_new_user(self, genres: list[str], ratings: dict[int, float],
                                n: int = 10) -> list[dict]:
        """
        Gợi ý cho user mới từ onboarding quiz.

        Args:
            genres: list genres đã chọn, e.g. ["Action", "Sci-Fi"]
            ratings: {movieId: rating_value}, e.g. {1: 4.5, 2: 3.0}
            n: số phim gợi ý

        Flow:
        1. Nếu len(ratings) >= 5 → dùng hybrid.recommend_for_new_user()
        2. Nếu < 5 → fallback popularity trong genres đã chọn
        3. Kèm explanation cho mỗi phim

        Returns: [
            {
                "rank": 1,
                "title": "Interstellar (2014)",
                "genres": "Sci-Fi, Adventure",
                "predicted_rating": 4.5,
                "explanation": "Vì bạn thích...",
            },
            ...
        ]
        """

    def recommend_for_user(self, user_id: int, n: int = 10) -> list[dict]:
        """
        Gợi ý cho existing user (có trong dataset).
        - Dùng HybridRecommender.recommend()
        - Enrich kết quả với movie info + explanation
        Returns: same format as above
        """

    def get_movie_details(self, movie_id: int) -> dict | None:
        """Trả về thông tin phim: title, genres, year, avg_rating, num_ratings"""

    def get_genres(self) -> list[str]:
        """Trả về list tất cả genres"""

    def get_popular_movies_for_onboarding(self, genres: list[str] = None, n: int = 15) -> pd.DataFrame:
        """
        Lấy phim phổ biến cho onboarding quiz.
        Nếu genres specified → filter theo genres trước
        Returns: DataFrame [movieId, title, genres, avg_rating]
        """

    def get_user_ids(self, limit: int = 100) -> list[int]:
        """Trả về list user_ids có trong trainset (cho dropdown trong UI)"""
```

## FILE 2: src/services/explainer.py

### Class ExplainService:

```python
# Templates
TEMPLATES = {
    'knn': "Vì bạn thích '{liked_movie}', phim này có pattern đánh giá tương tự (similarity: {sim:.0%})",
    'svd': "Dựa trên sở thích của bạn, model dự đoán bạn sẽ đánh giá phim này {rating:.1f}/5",
    'genre': "Phù hợp với thể loại yêu thích của bạn: {genres}",
    'popular': "Phim được đánh giá cao bởi {count} người dùng (avg: {avg:.1f}/5)",
}

class ExplainService:
    """Sinh giải thích cho mỗi recommendation."""

    def __init__(self, knn_model, movies_info: pd.DataFrame):
        """
        Args:
            knn_model: Trained ItemKNN (cần get_neighbors)
            movies_info: DataFrame với movie metadata
        """

    def explain(self, user_id: int, movie_id: int,
                svd_score: float, knn_score: float,
                user_rated_movies: dict[int, float] = None,
                user_genres: list[str] = None) -> str:
        """
        Sinh explanation text cho 1 recommendation.

        Logic:
        1. So sánh svd_score vs knn_score → model nào contribute nhiều hơn
        2. Nếu KNN contribute nhiều:
           - Tìm phim tương tự nhất mà user đã rate cao (>= 3.5)
           - Dùng template 'knn'
        3. Nếu SVD contribute nhiều:
           - Dùng template 'svd' với predicted rating
        4. Bonus: nếu genres match user preferences → append template 'genre'

        Returns: explanation string (tiếng Việt)
        """

    def explain_popular(self, movie_id: int) -> str:
        """Explanation cho popularity-based recommendation"""
```

## FILE 3: src/services/search.py

### Class SearchService:

```python
class SearchService:
    """Tìm kiếm và lọc phim."""

    def __init__(self, movies_info: pd.DataFrame):
        """
        Args:
            movies_info: DataFrame [movieId, title, genres, year, avg_rating, num_ratings]
        """

    def search_movies(self, query: str = "", genre: str = None,
                      min_rating: float = None, limit: int = 20) -> pd.DataFrame:
        """
        Tìm phim theo nhiều tiêu chí.

        Args:
            query: Tên phim (partial match, case-insensitive). "" = tất cả
            genre: Filter theo genre cụ thể. None = tất cả genres
            min_rating: Chỉ lấy phim có avg_rating >= min_rating
            limit: Số kết quả tối đa

        Returns: DataFrame [title, year, genres, avg_rating, num_ratings]
                 sorted by avg_rating desc
        """

    def get_genre_options(self) -> list[str]:
        """List genres cho dropdown, bao gồm "Tất cả" ở đầu"""
```

## FILE 4: src/services/__init__.py

```python
from .recommender import RecommenderService
from .explainer import ExplainService
from .search import SearchService
```

---

## FILE 5: src/app.py — GRADIO UI

### Cấu trúc tổng thể:

```python
import gradio as gr
from src.services import RecommenderService, SearchService

# Init services (singleton)
service = RecommenderService()
search_service = SearchService(service.movies_info)

def create_app() -> gr.Blocks:
    with gr.Blocks(
        title="NexConflict - Movie Recommender",
        theme=gr.themes.Soft()
    ) as app:

        gr.Markdown("# 🎬 NexConflict - Hệ thống Gợi ý Phim")

        with gr.Tabs():
            # Tab 1: Onboarding
            _build_onboarding_tab()

            # Tab 2: Recommendations (existing users)
            _build_recommend_tab()

            # Tab 3: Search
            _build_search_tab()

            # Tab 4: Model Evaluation
            _build_eval_tab()

    return app
```

### Tab 1: Onboarding (Chi tiết)

```python
def _build_onboarding_tab():
    with gr.Tab("🎯 Bắt đầu"):
        gr.Markdown("### Hãy cho chúng tôi biết sở thích phim của bạn!")

        # Step 1: Chọn genres
        genre_selector = gr.CheckboxGroup(
            choices=service.get_genres(),
            label="Chọn thể loại yêu thích (2-5 thể loại)",
        )

        # Step 2: Button load phim phổ biến theo genres
        load_movies_btn = gr.Button("Hiển thị phim để đánh giá")

        # Step 3: Hiển thị phim + rating sliders
        # Dùng gr.Dataframe hoặc dynamic components
        # Mỗi phim: title + Slider(1, 5, step=0.5, value=3)
        # Tối đa 15 phim

        movie_ratings = gr.Dataframe(
            headers=["movieId", "Tên phim", "Thể loại", "Đánh giá (1-5)"],
            datatype=["number", "str", "str", "number"],
            interactive=True,  # User có thể sửa cột "Đánh giá"
            label="Đánh giá các phim sau (sửa cột 'Đánh giá')"
        )

        # Step 4: Button gợi ý
        recommend_btn = gr.Button("💡 Gợi ý phim cho tôi", variant="primary")

        # Output
        results = gr.Dataframe(
            headers=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"],
            label="Phim gợi ý cho bạn"
        )

        # Event handlers
        load_movies_btn.click(
            fn=on_load_movies,  # Load popular movies based on selected genres
            inputs=[genre_selector],
            outputs=[movie_ratings]
        )

        recommend_btn.click(
            fn=on_recommend_new_user,
            inputs=[genre_selector, movie_ratings],
            outputs=[results]
        )
```

### Tab 2: Recommendations

```python
def _build_recommend_tab():
    with gr.Tab("📋 Gợi ý phim"):
        gr.Markdown("### Xem gợi ý cho người dùng có trong hệ thống")

        with gr.Row():
            user_dropdown = gr.Dropdown(
                choices=service.get_user_ids(),
                label="Chọn User ID",
                interactive=True,
            )
            n_slider = gr.Slider(
                minimum=5, maximum=20, value=10, step=1,
                label="Số lượng phim gợi ý"
            )

        recommend_btn = gr.Button("🎬 Lấy gợi ý", variant="primary")

        results = gr.Dataframe(
            headers=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"],
            label="Top phim gợi ý"
        )

        recommend_btn.click(
            fn=on_recommend_existing,
            inputs=[user_dropdown, n_slider],
            outputs=[results]
        )
```

### Tab 3: Search

```python
def _build_search_tab():
    with gr.Tab("🔍 Tìm kiếm"):
        gr.Markdown("### Tìm kiếm phim trong cơ sở dữ liệu")

        with gr.Row():
            search_box = gr.Textbox(label="Tên phim", placeholder="Nhập tên phim...")
            genre_filter = gr.Dropdown(
                choices=["Tất cả"] + service.get_genres(),
                value="Tất cả",
                label="Thể loại"
            )
            min_rating = gr.Slider(
                minimum=0.5, maximum=5.0, value=0.5, step=0.5,
                label="Rating tối thiểu"
            )

        search_btn = gr.Button("Tìm kiếm")

        results = gr.Dataframe(
            headers=["Tên phim", "Năm", "Thể loại", "Rating TB", "Số lượt đánh giá"],
            label="Kết quả tìm kiếm"
        )

        search_btn.click(
            fn=on_search,
            inputs=[search_box, genre_filter, min_rating],
            outputs=[results]
        )
```

### Tab 4: Evaluation

```python
def _build_eval_tab():
    with gr.Tab("📊 Đánh giá Model"):
        gr.Markdown("### So sánh hiệu suất các thuật toán")

        eval_btn = gr.Button("Tải kết quả đánh giá")

        with gr.Row():
            rmse_plot = gr.Plot(label="So sánh RMSE")
            precision_plot = gr.Plot(label="So sánh Precision@10")

        metrics_table = gr.Dataframe(
            headers=["Model", "RMSE", "MAE", "Precision@10", "Recall@10", "NDCG@10", "Coverage", "Diversity"],
            label="Bảng tổng hợp Metrics"
        )

        eval_btn.click(
            fn=on_load_evaluation,
            outputs=[rmse_plot, precision_plot, metrics_table]
        )
```

### Event Handler Functions

```python
def on_load_movies(genres: list[str]) -> pd.DataFrame:
    """Load phim phổ biến theo genres đã chọn cho onboarding"""
    if not genres:
        return pd.DataFrame()
    movies = service.get_popular_movies_for_onboarding(genres, n=15)
    # Thêm cột "Đánh giá" mặc định = 3.0
    movies["Đánh giá (1-5)"] = 3.0
    return movies[["movieId", "title", "genres", "Đánh giá (1-5)"]]

def on_recommend_new_user(genres: list[str], ratings_df: pd.DataFrame) -> pd.DataFrame:
    """Xử lý onboarding: parse ratings từ dataframe → gọi service"""
    # Parse ratings_df → dict {movieId: rating}
    ratings = dict(zip(ratings_df["movieId"].astype(int), ratings_df["Đánh giá (1-5)"].astype(float)))
    results = service.recommend_for_new_user(genres, ratings, n=10)
    return pd.DataFrame(results)

def on_recommend_existing(user_id: int, n: int) -> pd.DataFrame:
    """Gợi ý cho existing user"""
    results = service.recommend_for_user(int(user_id), int(n))
    return pd.DataFrame(results)

def on_search(query: str, genre: str, min_rating: float) -> pd.DataFrame:
    """Tìm kiếm phim"""
    g = None if genre == "Tất cả" else genre
    return search_service.search_movies(query, genre=g, min_rating=min_rating)

def on_load_evaluation():
    """Load evaluation results từ artifacts/"""
    # Load artifacts/evaluation_results.json
    # Tạo matplotlib figures cho plots
    # Return (fig1, fig2, metrics_df)
```

### App Entry Point

```python
if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Local only
    )
```

## LƯU Ý QUAN TRỌNG

### Gradio Dataframe interactive
- Khi dùng dataframe interactive, user có thể chỉnh sửa cells
- Dùng cái này cho onboarding ratings (user sửa cột "Đánh giá")

### Error handling trong UI
- Bọc mỗi event handler trong try/except
- Hiển thị error message bằng gr.Warning() hoặc gr.Info()
- KHÔNG để app crash khi có lỗi

### State management
- Gradio handles state per-session tự động
- Không cần global mutable state ngoài singleton service

## DELIVERABLES
1. `src/services/__init__.py`
2. `src/services/recommender.py`
3. `src/services/explainer.py`
4. `src/services/search.py`
5. `src/app.py` — Gradio UI hoàn chỉnh với 4 tabs
