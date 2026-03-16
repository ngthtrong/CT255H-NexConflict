"""
Evaluation metrics for the NexConflict recommendation system.
"""

import math

import numpy as np


def rmse(predictions: list[tuple[float, float]]) -> float:
    """
    Root Mean Square Error.

    Args:
        predictions: List of (actual_rating, predicted_rating) tuples.

    Returns:
        RMSE value (lower is better).
    """
    if not predictions:
        return 0.0
    errors = [(a - p) ** 2 for a, p in predictions]
    return float(math.sqrt(np.mean(errors)))


def mae(predictions: list[tuple[float, float]]) -> float:
    """
    Mean Absolute Error.

    Args:
        predictions: List of (actual_rating, predicted_rating) tuples.

    Returns:
        MAE value (lower is better).
    """
    if not predictions:
        return 0.0
    errors = [abs(a - p) for a, p in predictions]
    return float(np.mean(errors))


def precision_at_k(recommended: list[int], relevant: set[int], k: int = 10) -> float:
    """
    Precision@K: fraction of top-K recommended items that are relevant.

    Args:
        recommended: Ordered list of recommended movie IDs.
        relevant: Set of movie IDs the user actually likes.
        k: Top-K cutoff.

    Returns:
        Precision score in [0, 1].
    """
    if k <= 0:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for mid in top_k if mid in relevant)
    return hits / k


def recall_at_k(recommended: list[int], relevant: set[int], k: int = 10) -> float:
    """
    Recall@K: fraction of relevant items found in top-K.

    Args:
        recommended: Ordered list of recommended movie IDs.
        relevant: Set of movie IDs the user actually likes.
        k: Top-K cutoff.

    Returns:
        Recall score in [0, 1].
    """
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for mid in top_k if mid in relevant)
    return hits / len(relevant)


def ndcg_at_k(recommended: list[int], relevant: dict[int, float], k: int = 10) -> float:
    """
    Normalized Discounted Cumulative Gain @K.

    Args:
        recommended: Ordered list of recommended movie IDs.
        relevant: Dict mapping movieId to actual rating (ground truth).
        k: Top-K cutoff.

    Returns:
        NDCG score in [0, 1].
    """
    def dcg(items: list[int], ratings: dict[int, float]) -> float:
        score = 0.0
        for i, mid in enumerate(items, start=1):
            rel = ratings.get(mid, 0.0)
            score += (2 ** rel - 1) / math.log2(i + 1)
        return score

    top_k = recommended[:k]
    dcg_val = dcg(top_k, relevant)

    ideal_items = sorted(relevant.keys(), key=lambda m: relevant[m], reverse=True)[:k]
    idcg_val = dcg(ideal_items, relevant)

    if idcg_val == 0.0:
        return 0.0
    return dcg_val / idcg_val


def coverage(all_recommendations: list[list[int]], total_items: int) -> float:
    """
    Catalog coverage: fraction of all items that appear in recommendations.

    Args:
        all_recommendations: List of recommendation lists (one per user).
        total_items: Total number of items in the catalog.

    Returns:
        Coverage score in [0, 1].
    """
    if total_items <= 0:
        return 0.0
    unique = set()
    for recs in all_recommendations:
        unique.update(recs)
    return len(unique) / total_items


def genre_jaccard_similarity(genres_a: set[str], genres_b: set[str]) -> float:
    """
    Jaccard similarity between two genre sets.

    Args:
        genres_a: Set of genres for movie A.
        genres_b: Set of genres for movie B.

    Returns:
        Jaccard similarity in [0, 1].
    """
    if not genres_a or not genres_b:
        return 0.0
    intersection = genres_a & genres_b
    union = genres_a | genres_b
    return len(intersection) / len(union)


def intra_list_diversity(
    recommended_ids: list[int],
    similarity_matrix: dict | None = None,
    movies_info=None,
) -> float:
    """
    Average pairwise dissimilarity (1 - similarity) within a recommendation list.

    Args:
        recommended_ids: List of movie IDs in one recommendation.
        similarity_matrix: Optional dict {(id1, id2): similarity}.
                           If None, genre-based Jaccard similarity is used.
        movies_info: DataFrame with 'movieId' and 'genres_list' columns.
                     Required when similarity_matrix is None.

    Returns:
        ILD score in [0, 1] (higher = more diverse).
    """
    n = len(recommended_ids)
    if n < 2:
        return 0.0

    diversities = []
    for i in range(n):
        for j in range(i + 1, n):
            id_a = recommended_ids[i]
            id_b = recommended_ids[j]
            if similarity_matrix is not None:
                sim = similarity_matrix.get((id_a, id_b),
                                            similarity_matrix.get((id_b, id_a), 0.0))
            elif movies_info is not None:
                row_a = movies_info[movies_info["movieId"] == id_a]
                row_b = movies_info[movies_info["movieId"] == id_b]
                if row_a.empty or row_b.empty:
                    sim = 0.0
                else:
                    genres_a = set(row_a.iloc[0].get("genres_list", []))
                    genres_b = set(row_b.iloc[0].get("genres_list", []))
                    sim = genre_jaccard_similarity(genres_a, genres_b)
            else:
                sim = 0.0
            diversities.append(1.0 - sim)

    return float(np.mean(diversities)) if diversities else 0.0
