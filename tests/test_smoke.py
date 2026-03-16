"""
Smoke tests for NexConflict Movie Recommender.

These tests verify that all modules import correctly and basic functionality
works without requiring the full MovieLens dataset (they use synthetic data).

Usage:
    python -m pytest tests/test_smoke.py -v
"""

import pandas as pd
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers to create synthetic data
# ---------------------------------------------------------------------------

def _make_synthetic_ratings(n_users: int = 50, n_movies: int = 100, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    user_ids = rng.integers(1, n_users + 1, size=n_users * 20)
    movie_ids = rng.integers(1, n_movies + 1, size=n_users * 20)
    ratings = rng.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], size=n_users * 20)
    timestamps = rng.integers(1_000_000, 2_000_000, size=n_users * 20)
    df = pd.DataFrame({
        "userId": user_ids.astype("int32"),
        "movieId": movie_ids.astype("int32"),
        "rating": ratings.astype("float32"),
        "timestamp": timestamps.astype("int64"),
    }).drop_duplicates(subset=["userId", "movieId"])
    return df


def _make_synthetic_movies(n_movies: int = 100) -> pd.DataFrame:
    genres_pool = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"]
    titles = [f"Movie {i} ({1990 + i % 30})" for i in range(1, n_movies + 1)]
    genres = ["|".join(np.random.choice(genres_pool, size=2, replace=False)) for _ in range(n_movies)]
    return pd.DataFrame({
        "movieId": np.arange(1, n_movies + 1, dtype="int32"),
        "title": titles,
        "genres": genres,
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_preprocessor():
    """Test preprocessing pipeline on synthetic data."""
    from src.data.preprocessor import (
        filter_sparse, enrich_movies, time_split,
        create_surprise_dataset, get_popular_movies, get_all_genres,
    )

    ratings = _make_synthetic_ratings()
    movies = _make_synthetic_movies()

    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    assert len(ratings) > 0

    movies = enrich_movies(movies, ratings)
    assert "avg_rating" in movies.columns
    assert "num_ratings" in movies.columns
    assert "year" in movies.columns
    assert "genres_list" in movies.columns

    train, test = time_split(ratings)
    assert len(train) > len(test)

    trainset, testset = create_surprise_dataset(train)
    assert trainset is not None

    popular = get_popular_movies(movies, n=10)
    assert len(popular) <= 10

    genres = get_all_genres(movies)
    assert len(genres) > 0


def test_knn_model():
    """Test ItemKNN trains and produces recommendations on synthetic data."""
    from src.data.preprocessor import filter_sparse, time_split, create_surprise_dataset
    from src.models import ItemKNN

    ratings = _make_synthetic_ratings()
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    train, _ = time_split(ratings)
    trainset, _ = create_surprise_dataset(train)

    knn = ItemKNN(k=5)
    knn.train(trainset)

    uid = trainset.to_raw_uid(0)
    recs = knn.recommend(int(uid), n=5)
    assert isinstance(recs, list)


def test_svd_model():
    """Test SVDModel trains and produces recommendations on synthetic data."""
    from src.data.preprocessor import filter_sparse, time_split, create_surprise_dataset
    from src.models import SVDModel

    ratings = _make_synthetic_ratings()
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    train, _ = time_split(ratings)
    trainset, _ = create_surprise_dataset(train)

    svd = SVDModel(n_factors=10, n_epochs=3)
    svd.train(trainset)

    uid = trainset.to_raw_uid(0)
    recs = svd.recommend(int(uid), n=5)
    assert isinstance(recs, list)


def test_hybrid_model():
    """Test HybridRecommender on synthetic data."""
    from src.data.preprocessor import filter_sparse, time_split, create_surprise_dataset
    from src.models import ItemKNN, SVDModel, HybridRecommender

    ratings = _make_synthetic_ratings()
    ratings = filter_sparse(ratings, min_user_ratings=5, min_item_ratings=3)
    train, _ = time_split(ratings)
    trainset, _ = create_surprise_dataset(train)

    knn = ItemKNN(k=5)
    knn.train(trainset)
    svd = SVDModel(n_factors=5, n_epochs=2)
    svd.train(trainset)

    hybrid = HybridRecommender(knn, svd, alpha=0.5)
    uid = int(trainset.to_raw_uid(0))
    recs = hybrid.recommend(uid, n=5)
    assert isinstance(recs, list)


def test_metrics():
    """Test metric calculations."""
    from src.evaluation.metrics import rmse, mae, precision_at_k, recall_at_k, ndcg_at_k

    preds = [(4.0, 3.5), (3.0, 3.2), (5.0, 4.5)]
    assert rmse(preds) > 0
    assert mae(preds) > 0

    rec = [1, 2, 3, 4, 5]
    rel = {1, 3, 7}
    assert 0 <= precision_at_k(rec, rel, k=5) <= 1
    assert 0 <= recall_at_k(rec, rel, k=5) <= 1

    relevant_dict = {1: 5.0, 3: 4.0}
    assert 0 <= ndcg_at_k(rec, relevant_dict, k=5) <= 1


def test_search():
    """Test SearchService with synthetic movie data."""
    from src.data.preprocessor import enrich_movies
    from src.services.search import SearchService

    movies = _make_synthetic_movies()
    ratings = _make_synthetic_ratings()
    movies = enrich_movies(movies, ratings)

    search = SearchService(movies)
    results = search.search_movies("Movie 1", limit=5)
    assert isinstance(results, pd.DataFrame)
    assert len(results) >= 0

    genre_opts = search.get_genre_options()
    assert "Tất cả" in genre_opts
    assert len(genre_opts) > 1


def test_get_movies_by_genre():
    """Test get_movies_by_genre returns correctly filtered results."""
    from src.data.preprocessor import get_movies_by_genre

    movies = _make_synthetic_movies()
    result = get_movies_by_genre(movies, "Action")
    assert isinstance(result, pd.DataFrame)
    # All returned movies should contain "Action" in their genres
    for _, row in result.iterrows():
        assert "action" in str(row["genres"]).lower()


def test_imports():
    """Verify that all public modules can be imported."""
    from src.data import (  # noqa: F401
        load_ratings, load_movies, sample_data, get_stats,
        filter_sparse, enrich_movies, time_split,
        create_surprise_dataset, get_popular_movies,
        get_movies_by_genre, get_all_genres,
    )
    from src.models import ItemKNN, SVDModel, HybridRecommender  # noqa: F401
    from src.services import RecommenderService, ExplainService, SearchService  # noqa: F401
    from src.evaluation import (  # noqa: F401
        EvaluationPipeline, RandomModel, PopularityModel,
        rmse, mae, precision_at_k, recall_at_k, ndcg_at_k,
        coverage, intra_list_diversity,
    )
