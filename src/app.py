"""
NexConflict Movie Recommender — Gradio UI entry point.

Usage:
    python -m src.app
"""

import json
import logging
from pathlib import Path

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Service initialisation
# ---------------------------------------------------------------------------

try:
    from src.services import RecommenderService, SearchService

    service = RecommenderService()
    search_service = SearchService(service.movies_info)
    _service_ok = True
except Exception as exc:
    logger.error(f"Could not initialise services: {exc}")
    service = None  # type: ignore[assignment]
    search_service = None  # type: ignore[assignment]
    _service_ok = False


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------


def on_load_movies(genres: list[str]) -> pd.DataFrame:
    """Load popular movies filtered by selected genres for the onboarding quiz."""
    try:
        if not genres or service is None:
            return pd.DataFrame(columns=["movieId", "Tên phim", "Thể loại", "Đánh giá (1-5)"])
        movies = service.get_popular_movies_for_onboarding(genres, n=15)
        movies = movies.rename(columns={"title": "Tên phim", "genres": "Thể loại"})
        movies["Đánh giá (1-5)"] = 3.0
        cols = [c for c in ["movieId", "Tên phim", "Thể loại", "Đánh giá (1-5)"] if c in movies.columns]
        return movies[cols]
    except Exception as e:
        logger.error(f"on_load_movies error: {e}")
        return pd.DataFrame(columns=["movieId", "Tên phim", "Thể loại", "Đánh giá (1-5)"])


def on_recommend_new_user(
    genres: list[str], ratings_df: pd.DataFrame
) -> pd.DataFrame:
    """Parse onboarding ratings and call RecommenderService."""
    try:
        if service is None or ratings_df is None or ratings_df.empty:
            return pd.DataFrame(columns=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"])

        # Accept either column name variants
        id_col = "movieId" if "movieId" in ratings_df.columns else ratings_df.columns[0]
        rating_col = "Đánh giá (1-5)" if "Đánh giá (1-5)" in ratings_df.columns else ratings_df.columns[-1]

        ratings: dict[int, float] = {}
        for _, row in ratings_df.iterrows():
            try:
                ratings[int(row[id_col])] = float(row[rating_col])
            except (ValueError, KeyError):
                continue

        results = service.recommend_for_new_user(genres or [], ratings, n=10)
        df = pd.DataFrame(results)
        if df.empty:
            return df
        return df.rename(columns={
            "rank": "#",
            "title": "Tên phim",
            "genres": "Thể loại",
            "predicted_rating": "Điểm dự đoán",
            "explanation": "Giải thích",
        })[["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"]]
    except Exception as e:
        logger.error(f"on_recommend_new_user error: {e}")
        gr.Warning(f"Lỗi: {e}")
        return pd.DataFrame(columns=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"])


def on_recommend_existing(user_id, n: int) -> pd.DataFrame:
    """Recommend movies for an existing user."""
    try:
        if service is None or user_id is None:
            return pd.DataFrame(columns=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"])
        results = service.recommend_for_user(int(user_id), int(n))
        df = pd.DataFrame(results)
        if df.empty:
            return df
        return df.rename(columns={
            "rank": "#",
            "title": "Tên phim",
            "genres": "Thể loại",
            "predicted_rating": "Điểm dự đoán",
            "explanation": "Giải thích",
        })[["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"]]
    except Exception as e:
        logger.error(f"on_recommend_existing error: {e}")
        gr.Warning(f"Lỗi: {e}")
        return pd.DataFrame(columns=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"])


def on_search(query: str, genre: str, min_rating: float) -> pd.DataFrame:
    """Search for movies."""
    try:
        if search_service is None:
            return pd.DataFrame()
        g = None if genre == "Tất cả" else genre
        return search_service.search_movies(query, genre=g, min_rating=min_rating)
    except Exception as e:
        logger.error(f"on_search error: {e}")
        gr.Warning(f"Lỗi tìm kiếm: {e}")
        return pd.DataFrame()


def on_load_evaluation():
    """Load evaluation results from artifacts/ and build plots."""
    results_path = Path("artifacts/evaluation_results.json")
    if not results_path.exists():
        empty_fig = plt.figure()
        empty_df = pd.DataFrame(
            columns=["Model", "RMSE", "MAE", "Precision@10", "Recall@10", "NDCG@10", "Coverage", "Diversity"]
        )
        return empty_fig, empty_fig, empty_df

    try:
        import matplotlib
        matplotlib.use("Agg")
        import seaborn as sns

        with open(results_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        df = pd.DataFrame(records)

        palette = sns.color_palette("Set2")
        model_names = df["Model"].tolist()

        # RMSE plot
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        rmse_col = "RMSE" if "RMSE" in df.columns else df.columns[1]
        ax1.bar(model_names, df[rmse_col], color=palette[: len(model_names)])
        ax1.set_title("So sánh RMSE")
        ax1.set_ylabel("RMSE (thấp hơn = tốt hơn)")

        # Precision plot
        prec_col = next((c for c in df.columns if "Precision" in c), None)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        if prec_col:
            ax2.bar(model_names, df[prec_col], color=palette[: len(model_names)])
            ax2.set_title(f"So sánh {prec_col}")
            ax2.set_ylabel(f"{prec_col} (cao hơn = tốt hơn)")

        return fig1, fig2, df
    except Exception as e:
        logger.error(f"on_load_evaluation error: {e}")
        empty_fig = plt.figure()
        return empty_fig, empty_fig, pd.DataFrame()


# ---------------------------------------------------------------------------
# UI builder
# ---------------------------------------------------------------------------


def _get_genres() -> list[str]:
    if service is not None:
        return service.get_genres()
    return []


def _get_user_ids() -> list:
    if service is not None:
        return service.get_user_ids(limit=200)
    return []


def create_app() -> gr.Blocks:
    genres = _get_genres()
    user_ids = _get_user_ids()
    genre_options = ["Tất cả"] + genres

    with gr.Blocks(
        title="NexConflict - Movie Recommender",
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown("# 🎬 NexConflict - Hệ thống Gợi ý Phim")

        with gr.Tabs():

            # ----------------------------------------------------------------
            # Tab 1: Onboarding
            # ----------------------------------------------------------------
            with gr.Tab("🎯 Bắt đầu"):
                gr.Markdown("### Hãy cho chúng tôi biết sở thích phim của bạn!")

                genre_selector = gr.CheckboxGroup(
                    choices=genres,
                    label="Chọn thể loại yêu thích (2-5 thể loại)",
                )

                load_movies_btn = gr.Button("Hiển thị phim để đánh giá")

                movie_ratings = gr.Dataframe(
                    headers=["movieId", "Tên phim", "Thể loại", "Đánh giá (1-5)"],
                    datatype=["number", "str", "str", "number"],
                    interactive=True,
                    label="Đánh giá các phim sau (sửa cột 'Đánh giá (1-5)')",
                )

                recommend_btn = gr.Button("💡 Gợi ý phim cho tôi", variant="primary")

                onboarding_results = gr.Dataframe(
                    headers=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"],
                    label="Phim gợi ý cho bạn",
                )

                load_movies_btn.click(
                    fn=on_load_movies,
                    inputs=[genre_selector],
                    outputs=[movie_ratings],
                )

                recommend_btn.click(
                    fn=on_recommend_new_user,
                    inputs=[genre_selector, movie_ratings],
                    outputs=[onboarding_results],
                )

            # ----------------------------------------------------------------
            # Tab 2: Existing user recommendations
            # ----------------------------------------------------------------
            with gr.Tab("📋 Gợi ý phim"):
                gr.Markdown("### Xem gợi ý cho người dùng có trong hệ thống")

                with gr.Row():
                    user_dropdown = gr.Dropdown(
                        choices=user_ids,
                        label="Chọn User ID",
                        interactive=True,
                    )
                    n_slider = gr.Slider(
                        minimum=5,
                        maximum=20,
                        value=10,
                        step=1,
                        label="Số lượng phim gợi ý",
                    )

                rec_btn = gr.Button("🎬 Lấy gợi ý", variant="primary")

                rec_results = gr.Dataframe(
                    headers=["#", "Tên phim", "Thể loại", "Điểm dự đoán", "Giải thích"],
                    label="Top phim gợi ý",
                )

                rec_btn.click(
                    fn=on_recommend_existing,
                    inputs=[user_dropdown, n_slider],
                    outputs=[rec_results],
                )

            # ----------------------------------------------------------------
            # Tab 3: Search
            # ----------------------------------------------------------------
            with gr.Tab("🔍 Tìm kiếm"):
                gr.Markdown("### Tìm kiếm phim trong cơ sở dữ liệu")

                with gr.Row():
                    search_box = gr.Textbox(
                        label="Tên phim",
                        placeholder="Nhập tên phim...",
                    )
                    genre_filter = gr.Dropdown(
                        choices=genre_options,
                        value="Tất cả",
                        label="Thể loại",
                    )
                    min_rating_slider = gr.Slider(
                        minimum=0.5,
                        maximum=5.0,
                        value=0.5,
                        step=0.5,
                        label="Rating tối thiểu",
                    )

                search_btn = gr.Button("Tìm kiếm")

                search_results = gr.Dataframe(
                    headers=["Tên phim", "Năm", "Thể loại", "Rating TB", "Số lượt đánh giá"],
                    label="Kết quả tìm kiếm",
                )

                search_btn.click(
                    fn=on_search,
                    inputs=[search_box, genre_filter, min_rating_slider],
                    outputs=[search_results],
                )

            # ----------------------------------------------------------------
            # Tab 4: Model Evaluation
            # ----------------------------------------------------------------
            with gr.Tab("📊 Đánh giá Model"):
                gr.Markdown("### So sánh hiệu suất các thuật toán")

                eval_btn = gr.Button("Tải kết quả đánh giá")

                with gr.Row():
                    rmse_plot = gr.Plot(label="So sánh RMSE")
                    precision_plot = gr.Plot(label="So sánh Precision@10")

                metrics_table = gr.Dataframe(
                    headers=[
                        "Model", "RMSE", "MAE",
                        "Precision@10", "Recall@10", "NDCG@10",
                        "Coverage", "Diversity",
                    ],
                    label="Bảng tổng hợp Metrics",
                )

                eval_btn.click(
                    fn=on_load_evaluation,
                    outputs=[rmse_plot, precision_plot, metrics_table],
                )

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
