"""
Evaluation pipeline for NexConflict recommendation system.
Compares Random, Popularity, KNN, SVD, and Hybrid models.
"""

import json
import logging
import random
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .metrics import (
    rmse,
    mae,
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    coverage,
    intra_list_diversity,
)

logger = logging.getLogger(__name__)


class RandomModel:
    """Baseline recommender that returns random recommendations."""

    def __init__(self, all_movie_ids: list[int], rating_range: tuple = (0.5, 5.0)):
        self.all_movie_ids = all_movie_ids
        self.rating_range = rating_range

    def predict(self, user_id: int, movie_id: int) -> float:
        """Return a random predicted rating."""
        return random.uniform(*self.rating_range)

    def recommend(
        self, user_id: int, n: int = 10, exclude: set = None
    ) -> list[tuple[int, float]]:
        """Return n random movies not in exclude set."""
        candidates = [m for m in self.all_movie_ids if m not in (exclude or set())]
        selected = random.sample(candidates, min(n, len(candidates)))
        return [(mid, self.predict(user_id, mid)) for mid in selected]


class PopularityModel:
    """Baseline recommender based on popularity (avg_rating × log(num_ratings))."""

    def __init__(self, movies_info: pd.DataFrame):
        df = movies_info.copy()
        df["pop_score"] = df["avg_rating"] * np.log1p(df["num_ratings"])
        self.popularity = df.sort_values("pop_score", ascending=False).reset_index(drop=True)

    def predict(self, user_id: int, movie_id: int) -> float:
        """Return avg_rating of the movie as popularity score."""
        row = self.popularity[self.popularity["movieId"] == movie_id]
        return float(row["avg_rating"].values[0]) if len(row) > 0 else 3.0

    def recommend(
        self, user_id: int, n: int = 10, exclude: set = None
    ) -> list[tuple[int, float]]:
        """Return top-n popular movies not in exclude set."""
        candidates = self.popularity[~self.popularity["movieId"].isin(exclude or set())]
        top_n = candidates.head(n)
        return list(zip(top_n["movieId"].astype(int), top_n["pop_score"]))


class EvaluationPipeline:
    """Orchestrates full evaluation of recommendation models."""

    def __init__(self, trainset, testset: list, movies_info: pd.DataFrame):
        """
        Args:
            trainset: Surprise Trainset.
            testset: List of (userId, movieId, rating) tuples.
            movies_info: DataFrame with movie metadata.
        """
        self.trainset = trainset
        self.testset = testset
        self.movies_info = movies_info
        self.total_items = len(movies_info)

    def evaluate_rating_prediction(self, model, testset: list) -> dict:
        """
        Compute RMSE and MAE for rating prediction.

        Args:
            model: Model with predict(user_id, movie_id) method.
            testset: List of (userId, movieId, actual_rating) tuples.

        Returns:
            dict with keys 'rmse' and 'mae'.
        """
        pairs = []
        for uid, iid, actual in testset:
            predicted = model.predict(int(uid), int(iid))
            if predicted is not None:
                pairs.append((float(actual), float(predicted)))
        return {"rmse": rmse(pairs), "mae": mae(pairs)}

    def evaluate_topn(
        self, model, testset: list, n: int = 10, threshold: float = 3.5
    ) -> dict:
        """
        Compute Precision@N, Recall@N, NDCG@N averaged across users.

        Args:
            model: Model with recommend(user_id, n) method.
            testset: List of (userId, movieId, rating) tuples.
            n: Top-N cutoff.
            threshold: Rating threshold for relevance.

        Returns:
            dict with 'precision@N', 'recall@N', 'ndcg@N'.
        """
        user_relevant: dict[int, dict[int, float]] = defaultdict(dict)
        for uid, iid, rating in testset:
            user_relevant[int(uid)][int(iid)] = float(rating)

        precisions, recalls, ndcgs = [], [], []
        for user_id, item_ratings in user_relevant.items():
            relevant_set = {mid for mid, r in item_ratings.items() if r >= threshold}
            try:
                recs = model.recommend(user_id, n=n)
            except Exception:
                continue
            if not recs:
                continue
            # Handle both list[tuple] and list[dict] formats
            if isinstance(recs[0], dict):
                rec_ids = [r["movieId"] for r in recs]
            else:
                rec_ids = [r[0] for r in recs]

            precisions.append(precision_at_k(rec_ids, relevant_set, k=n))
            recalls.append(recall_at_k(rec_ids, relevant_set, k=n))
            ndcgs.append(ndcg_at_k(rec_ids, item_ratings, k=n))

        return {
            f"precision@{n}": float(np.mean(precisions)) if precisions else 0.0,
            f"recall@{n}": float(np.mean(recalls)) if recalls else 0.0,
            f"ndcg@{n}": float(np.mean(ndcgs)) if ndcgs else 0.0,
        }

    def evaluate_coverage_diversity(
        self, model, test_users: list[int], n: int = 10
    ) -> dict:
        """
        Compute catalog coverage and average intra-list diversity.

        Args:
            model: Model with recommend(user_id, n) method.
            test_users: List of user IDs to evaluate.
            n: Number of recommendations per user.

        Returns:
            dict with 'coverage' and 'diversity'.
        """
        all_recs = []
        diversities = []
        for user_id in test_users:
            try:
                recs = model.recommend(user_id, n=n)
            except Exception:
                continue
            if not recs:
                continue
            if isinstance(recs[0], dict):
                rec_ids = [r["movieId"] for r in recs]
            else:
                rec_ids = [r[0] for r in recs]
            all_recs.append(rec_ids)
            div = intra_list_diversity(rec_ids, movies_info=self.movies_info)
            diversities.append(div)

        cov = coverage(all_recs, self.total_items) if all_recs else 0.0
        div_avg = float(np.mean(diversities)) if diversities else 0.0
        return {"coverage": cov, "diversity": div_avg}

    def compare_all_models(self, models: dict, n: int = 10) -> pd.DataFrame:
        """
        Run full evaluation for all provided models.

        Args:
            models: Dict mapping model name to model object.
            n: Top-N cutoff.

        Returns:
            DataFrame with columns: Model, RMSE, MAE, Precision@N, Recall@N, NDCG@N,
            Coverage, Diversity.
        """
        test_users = list({int(uid) for uid, _, _ in self.testset})
        rows = []
        for name, model in models.items():
            logger.info(f"Evaluating {name}...")
            rating_metrics = self.evaluate_rating_prediction(model, self.testset)
            topn_metrics = self.evaluate_topn(model, self.testset, n=n)
            cov_div = self.evaluate_coverage_diversity(model, test_users, n=n)
            row = {
                "Model": name,
                "RMSE": round(rating_metrics["rmse"], 4),
                "MAE": round(rating_metrics["mae"], 4),
                f"Precision@{n}": round(topn_metrics.get(f"precision@{n}", 0.0), 4),
                f"Recall@{n}": round(topn_metrics.get(f"recall@{n}", 0.0), 4),
                f"NDCG@{n}": round(topn_metrics.get(f"ndcg@{n}", 0.0), 4),
                "Coverage": round(cov_div["coverage"], 4),
                "Diversity": round(cov_div["diversity"], 4),
            }
            rows.append(row)
            logger.info(f"{name}: {row}")
        return pd.DataFrame(rows)

    def plot_comparison(
        self, results_df: pd.DataFrame, save_dir: str = "artifacts/plots"
    ) -> dict:
        """
        Create and save bar chart comparisons for RMSE, Precision, and NDCG.

        Args:
            results_df: DataFrame from compare_all_models().
            save_dir: Directory to save PNG plots.

        Returns:
            Dict of matplotlib Figure objects.
        """
        sns.set_style("whitegrid")
        palette = sns.color_palette("Set2")
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        model_names = results_df["Model"].tolist()
        figures = {}

        # RMSE comparison
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        rmse_vals = results_df["RMSE"].tolist()
        bars = ax1.bar(model_names, rmse_vals, color=palette[: len(model_names)])
        ax1.set_title("So sánh RMSE giữa các Model")
        ax1.set_ylabel("RMSE (thấp hơn = tốt hơn)")
        ax1.set_xlabel("Model")
        for bar, val in zip(bars, rmse_vals):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.3f}",
                ha="center",
                va="bottom",
            )
        fig1.tight_layout()
        fig1.savefig(save_path / "rmse_comparison.png")
        figures["rmse"] = fig1
        plt.close(fig1)

        # Precision@10 comparison
        prec_col = [c for c in results_df.columns if c.startswith("Precision")]
        if prec_col:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            prec_vals = results_df[prec_col[0]].tolist()
            bars2 = ax2.bar(model_names, prec_vals, color=palette[: len(model_names)])
            ax2.set_title(f"So sánh {prec_col[0]} giữa các Model")
            ax2.set_ylabel(f"{prec_col[0]} (cao hơn = tốt hơn)")
            ax2.set_xlabel("Model")
            for bar, val in zip(bars2, prec_vals):
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f"{val:.3f}",
                    ha="center",
                    va="bottom",
                )
            fig2.tight_layout()
            fig2.savefig(save_path / "precision_comparison.png")
            figures["precision"] = fig2
            plt.close(fig2)

        # NDCG@10 comparison
        ndcg_col = [c for c in results_df.columns if c.startswith("NDCG")]
        if ndcg_col:
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            ndcg_vals = results_df[ndcg_col[0]].tolist()
            bars3 = ax3.bar(model_names, ndcg_vals, color=palette[: len(model_names)])
            ax3.set_title(f"So sánh {ndcg_col[0]} giữa các Model")
            ax3.set_ylabel(f"{ndcg_col[0]} (cao hơn = tốt hơn)")
            ax3.set_xlabel("Model")
            for bar, val in zip(bars3, ndcg_vals):
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.001,
                    f"{val:.3f}",
                    ha="center",
                    va="bottom",
                )
            fig3.tight_layout()
            fig3.savefig(save_path / "ndcg_comparison.png")
            figures["ndcg"] = fig3
            plt.close(fig3)

        # Overview grouped bar chart
        metric_cols = [c for c in results_df.columns if c != "Model"]
        norm_df = results_df[metric_cols].copy()
        # Normalize to [0,1] per column for display
        for col in metric_cols:
            col_max = norm_df[col].max()
            if col_max > 0:
                norm_df[col] = norm_df[col] / col_max
        norm_df.insert(0, "Model", model_names)

        fig4, ax4 = plt.subplots(figsize=(14, 7))
        x = np.arange(len(model_names))
        width = 0.1
        for idx, col in enumerate(metric_cols):
            offset = (idx - len(metric_cols) / 2) * width
            ax4.bar(x + offset, norm_df[col], width, label=col, color=palette[idx % len(palette)])
        ax4.set_xticks(x)
        ax4.set_xticklabels(model_names)
        ax4.set_title("Tổng quan so sánh các Metrics (chuẩn hóa)")
        ax4.set_ylabel("Normalized Score")
        ax4.legend(loc="upper right", fontsize=8)
        fig4.tight_layout()
        fig4.savefig(save_path / "overview_comparison.png")
        figures["overview"] = fig4
        plt.close(fig4)

        return figures

    def save_results(
        self,
        results_df: pd.DataFrame,
        path: str = "artifacts/evaluation_results.json",
    ) -> None:
        """Save evaluation results to a JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        records = results_df.to_dict(orient="records")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        logger.info(f"Evaluation results saved to {path}")

    def run_full_evaluation(self, models: dict) -> tuple[pd.DataFrame, dict]:
        """
        Run full evaluation pipeline: compare all models and generate plots.

        Args:
            models: Dict of model name → model instance.

        Returns:
            (results_df, plot_figures_dict) tuple.
        """
        results_df = self.compare_all_models(models)
        plots = self.plot_comparison(results_df)
        return results_df, plots
