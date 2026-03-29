from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import numpy as np
import os
import joblib

try:
    from surprise import Dataset, Reader, SVD
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    class SVD: pass  # Dummy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineStream AI Service", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Variables for Data and Models ---
svd_model = None
cosine_sim_matrix = None
movies_df = None
ratings_df = None
movie_id_to_index = {}
index_to_movie_id = {}

# --- Paths ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

# --- Helper Functions ---
def find_file(filename):
    possible_paths = [
        f"../data/{filename}",
        f"data/{filename}",
        f"../../data/{filename}",
        f"D:/CT255H - BI/Project/CT255H-NexConflict/data/{filename}"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

# --- Model Loading Functions (load từ file đã train sẵn) ---
def load_models():
    """Load pre-trained models từ thư mục models/"""
    global svd_model, cosine_sim_matrix, movies_df, ratings_df
    global movie_id_to_index, index_to_movie_id

    if not os.path.exists(MODEL_DIR):
        logger.warning(f"Thư mục models/ không tồn tại: {MODEL_DIR}")
        logger.warning("Hãy chạy 'python train.py' trước để train model!")
        return False

    loaded = False

    # Load SVD model
    svd_path = os.path.join(MODEL_DIR, 'svd_model.pkl')
    if os.path.exists(svd_path):
        try:
            svd_model = joblib.load(svd_path)
            logger.info(f"✅ Đã load SVD model từ {svd_path}")
            loaded = True
        except ModuleNotFoundError as e:
            # Compatible fallback when pre-trained SVD was saved with surprise
            # but current environment does not have surprise installed.
            logger.warning(f"Không thể load SVD model do thiếu module: {e}")
            svd_model = None
        except Exception as e:
            logger.warning(f"Không thể load SVD model: {e}")
            svd_model = None
    else:
        logger.warning("SVD model không tìm thấy")

    # Load ratings DataFrame
    ratings_path = os.path.join(MODEL_DIR, 'ratings_df.pkl')
    if os.path.exists(ratings_path):
        ratings_df = joblib.load(ratings_path)
        logger.info(f"✅ Đã load ratings DataFrame ({len(ratings_df)} rows)")

    # Load cosine similarity matrix
    cosine_path = os.path.join(MODEL_DIR, 'cosine_sim_matrix.pkl')
    if os.path.exists(cosine_path):
        cosine_sim_matrix = joblib.load(cosine_path)
        logger.info(f"✅ Đã load Cosine Similarity matrix: {cosine_sim_matrix.shape}")
        loaded = True

    # Load movies DataFrame
    movies_pkl_path = os.path.join(MODEL_DIR, 'movies_df.pkl')
    if os.path.exists(movies_pkl_path):
        movies_df = joblib.load(movies_pkl_path)
        logger.info(f"✅ Đã load movies DataFrame ({len(movies_df)} phim)")

    # Load mappings
    mapping_path = os.path.join(MODEL_DIR, 'mappings.pkl')
    if os.path.exists(mapping_path):
        mappings = joblib.load(mapping_path)
        movie_id_to_index = mappings['movie_id_to_index']
        index_to_movie_id = mappings['index_to_movie_id']
        logger.info(f"✅ Đã load mappings ({len(movie_id_to_index)} phim)")

    return loaded

def fallback_train():
    """Fallback: train trực tiếp nếu không có model file (giống logic cũ)."""
    global svd_model, cosine_sim_matrix, movies_df, ratings_df
    global movie_id_to_index, index_to_movie_id

    logger.info("⚠️ Không tìm thấy model đã train. Đang train trực tiếp...")

    # Load movies
    movies_path = find_file("movies.csv")
    if not movies_path:
        logger.error("movies.csv not found!")
        movies_df = pd.DataFrame({
            'movieId': [1, 2, 3],
            'title': ['Toy Story (1995)', 'Jumanji (1995)', 'Grumpier Old Men (1995)'],
            'genres': ['Adventure|Animation|Children|Comedy|Fantasy',
                       'Adventure|Children|Fantasy', 'Comedy|Romance']
        })
    else:
        movies_df = pd.read_csv(movies_path)

    movies_df = movies_df.reset_index(drop=True)
    for idx, row in movies_df.iterrows():
        movie_id_to_index[row['movieId']] = idx
        index_to_movie_id[idx] = row['movieId']

    # Train SVD
    if SURPRISE_AVAILABLE:
        ratings_path = find_file("ratings.csv")
        if ratings_path:
            try:
                ratings_df = pd.read_csv(ratings_path, nrows=200000)
                reader = Reader(rating_scale=(0.5, 5.0))
                data = Dataset.load_from_df(
                    ratings_df[['userId', 'movieId', 'rating']], reader)
                trainset = data.build_full_trainset()
                svd = SVD(n_factors=100, n_epochs=20, random_state=42)
                svd.fit(trainset)
                svd_model = svd
                logger.info("SVD trained (fallback)")
            except Exception as e:
                logger.error(f"SVD training failed: {e}")

    # Build content filtering
    if 'genres' in movies_df.columns:
        try:
            movies_df['genres_str'] = movies_df['genres'].fillna('').str.replace(
                '|', ' ', regex=False)
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(movies_df['genres_str'])
            max_movies = min(5000, tfidf_matrix.shape[0])
            cosine_sim_matrix = cosine_similarity(
                tfidf_matrix[:max_movies], tfidf_matrix[:max_movies])
            logger.info(f"Cosine matrix built (fallback): {cosine_sim_matrix.shape}")
        except Exception as e:
            logger.error(f"Content filtering failed: {e}")

# --- Startup ---
@app.on_event("startup")
def startup_event():
    # Ưu tiên load model đã train sẵn
    success = load_models()
    if not success:
        # Fallback: train trực tiếp (như logic cũ)
        fallback_train()
    logger.info("AI Service ready!")

# --- API Endpoints ---
@app.get("/")
def read_root():
    models_status = {
        "svd": svd_model is not None,
        "content_based": cosine_sim_matrix is not None,
        "movies_loaded": len(movies_df) if movies_df is not None else 0
    }
    return {"status": "AI Service Running", "models": models_status}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, limit: int = 10):
    """
    Get personalized recommendations using SVD or content-based filtering.
    Returns list of Movie IDs.
    """
    if movies_df is None:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10][:limit]

    try:
        # If SVD model available, use collaborative filtering
        if svd_model is not None and ratings_df is not None:
            all_movie_ids = movies_df['movieId'].unique()

            # Get movies the user has already rated
            user_ratings = ratings_df[ratings_df['userId'] == user_id]
            rated_movies = set(user_ratings['movieId'].values)

            # Predict ratings for unrated movies
            predictions = []
            for movie_id in all_movie_ids[:1000]:  # Limit to first 1000 for speed
                if movie_id not in rated_movies:
                    try:
                        pred = svd_model.predict(user_id, movie_id)
                        predictions.append((int(movie_id), pred.est))
                    except:
                        pass

            if predictions:
                predictions.sort(key=lambda x: x[1], reverse=True)
                return [p[0] for p in predictions[:limit]]

        # Fallback: Use content-based - recommend diverse genres
        # Get movies with highest variety of genres (proxy for popularity)
        movie_ids = [int(x) for x in movies_df['movieId'].head(limit * 3).values]
        # Shuffle to add variety
        import random
        random.seed(user_id)  # Consistent for same user
        random.shuffle(movie_ids)
        return movie_ids[:limit]

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return [int(x) for x in movies_df['movieId'].head(limit).values]

@app.get("/similar/{movie_id}")
def get_similar_movies(movie_id: int, limit: int = 5):
    """
    Get similar movies based on content (genres) using cosine similarity.
    """
    if cosine_sim_matrix is None or movies_df is None:
        # Fallback: return nearby movie IDs
        return [movie_id + i for i in range(1, limit + 1)]

    try:
        # Get index of the movie
        if movie_id not in movie_id_to_index:
            # Movie not found, return nearby IDs
            return [movie_id + i for i in range(1, limit + 1)]

        idx = movie_id_to_index[movie_id]

        # Check if index is within our computed matrix
        if idx >= cosine_sim_matrix.shape[0]:
            return [movie_id + i for i in range(1, limit + 1)]

        # Get similarity scores for this movie
        sim_scores = list(enumerate(cosine_sim_matrix[idx]))

        # Sort by similarity (descending), excluding the movie itself
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get top similar movies (skip first one which is the movie itself)
        similar_indices = [i[0] for i in sim_scores[1:limit + 1]]

        # Convert indices back to movie IDs
        similar_movie_ids = [int(index_to_movie_id[i]) for i in similar_indices if i in index_to_movie_id]

        return similar_movie_ids if similar_movie_ids else [movie_id + i for i in range(1, limit + 1)]

    except Exception as e:
        logger.error(f"Error getting similar movies: {e}")
        return [movie_id + i for i in range(1, limit + 1)]

@app.post("/recommendations/based-on-movies")
def get_recommendations_based_on_movies(movie_ids: list[int], limit: int = 10):
    """
    Get recommendations based on a list of movie IDs (e.g., from user's watchlist).
    Uses content-based filtering to find similar movies.
    """
    if movies_df is None or cosine_sim_matrix is None:
        # Fallback
        return [int(x) for x in movies_df['movieId'].head(limit).values] if movies_df is not None else []

    try:
        # Collect similarity scores for all watchlist movies
        all_similar = {}
        input_movie_set = set(movie_ids)

        for movie_id in movie_ids:
            if movie_id not in movie_id_to_index:
                continue

            idx = movie_id_to_index[movie_id]

            # Check if index is within our computed matrix
            if idx >= cosine_sim_matrix.shape[0]:
                continue

            # Get similarity scores for this movie
            sim_scores = cosine_sim_matrix[idx]

            for i, score in enumerate(sim_scores):
                if i in index_to_movie_id:
                    similar_movie_id = index_to_movie_id[i]
                    # Don't recommend movies already in watchlist
                    if similar_movie_id not in input_movie_set:
                        if similar_movie_id in all_similar:
                            all_similar[similar_movie_id] = max(all_similar[similar_movie_id], score)
                        else:
                            all_similar[similar_movie_id] = score

        if all_similar:
            # Sort by similarity score and return top recommendations
            sorted_movies = sorted(all_similar.items(), key=lambda x: x[1], reverse=True)
            result = [int(movie_id) for movie_id, score in sorted_movies[:limit]]
            logger.info(f"Recommendations based on {len(movie_ids)} watchlist movies: {result}")
            return result

        # Fallback if no similar movies found
        return [int(x) for x in movies_df['movieId'].head(limit).values]

    except Exception as e:
        logger.error(f"Error getting watchlist-based recommendations: {e}")
        return [int(x) for x in movies_df['movieId'].head(limit).values]


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "svd_model": svd_model is not None,
        "content_model": cosine_sim_matrix is not None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
