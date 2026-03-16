"""
Training script for NexConflict Movie Recommender.

Trains KNN, SVD, and Hybrid models and saves artifacts.

Usage:
    python -m src.scripts.train [--n-users 5000] [--tune]
"""

import argparse
import logging
import time
from pathlib import Path

import joblib

from src.data import load_ratings, load_movies, sample_data
from src.data import filter_sparse, enrich_movies, time_split, create_surprise_dataset, get_popular_movies
from src.models import ItemKNN, SVDModel, HybridRecommender
from src.evaluation import EvaluationPipeline, RandomModel, PopularityModel

ARTIFACTS_DIR = Path("artifacts")
PLOTS_DIR = ARTIFACTS_DIR / "plots"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train NexConflict recommendation models")
    parser.add_argument(
        "--n-users", type=int, default=5000,
        help="Number of users to sample from the full dataset (default: 5000)"
    )
    parser.add_argument(
        "--tune", action="store_true",
        help="Tune Hybrid alpha on validation data"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Load & Sample
    # ------------------------------------------------------------------
    logger.info("Loading data…")
    ratings = load_ratings()
    movies = load_movies()
    ratings = sample_data(ratings, n_users=args.n_users)

    # ------------------------------------------------------------------
    # Step 2: Preprocess
    # ------------------------------------------------------------------
    logger.info("Preprocessing…")
    ratings = filter_sparse(ratings)
    movies = enrich_movies(movies, ratings)
    train_df, test_df = time_split(ratings)
    trainset, testset = create_surprise_dataset(train_df)
    popular = get_popular_movies(movies)

    # Save processed data artifacts used by the app
    movies.to_pickle(ARTIFACTS_DIR / "movies_info.pkl")
    popular.to_pickle(ARTIFACTS_DIR / "popular_movies.pkl")
    joblib.dump(trainset, ARTIFACTS_DIR / "trainset.pkl")
    joblib.dump(testset, ARTIFACTS_DIR / "testset.pkl")
    logger.info("Saved processed data artifacts.")

    # ------------------------------------------------------------------
    # Step 3: Train KNN
    # ------------------------------------------------------------------
    logger.info("Training Item-KNN…")
    t0 = time.time()
    knn = ItemKNN(k=30, sim_name="cosine")
    knn.train(trainset)
    knn.save(str(ARTIFACTS_DIR / "knn_model.pkl"))
    logger.info(f"KNN trained in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------
    # Step 4: Train SVD
    # ------------------------------------------------------------------
    logger.info("Training SVD…")
    t0 = time.time()
    svd = SVDModel(n_factors=100, n_epochs=20)
    svd.train(trainset)
    svd.save(str(ARTIFACTS_DIR / "svd_model.pkl"))
    logger.info(f"SVD trained in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------
    # Step 5: Create Hybrid
    # ------------------------------------------------------------------
    logger.info("Creating Hybrid model…")
    hybrid = HybridRecommender(knn, svd, alpha=0.5)
    if args.tune:
        logger.info("Tuning alpha on test set…")
        best_alpha = hybrid.tune_alpha(testset)
        logger.info(f"Best alpha: {best_alpha}")
    hybrid.save(str(ARTIFACTS_DIR / "hybrid_model.pkl"))

    # ------------------------------------------------------------------
    # Step 6: Evaluate
    # ------------------------------------------------------------------
    logger.info("Running evaluation…")
    evaluator = EvaluationPipeline(trainset, testset, movies)
    models = {
        "Random": RandomModel(movies["movieId"].tolist()),
        "Popularity": PopularityModel(movies),
        "Item-KNN": knn,
        "SVD": svd,
        "Hybrid": hybrid,
    }
    results_df, _plots = evaluator.run_full_evaluation(models)
    evaluator.save_results(results_df)

    logger.info("Training complete!")
    logger.info(f"\n{results_df.to_string()}")


if __name__ == "__main__":
    main()
