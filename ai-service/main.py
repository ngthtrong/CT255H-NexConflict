from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
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

# PyTorch support for MF model (GPU-trained)
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

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

# --- PyTorch Matrix Factorization Model ---
if TORCH_AVAILABLE:
    class MatrixFactorization(nn.Module):
        """PyTorch MF model - phải match với architecture đã train trong notebook"""
        def __init__(self, n_users, n_movies, n_factors=100, global_mean=3.5):
            super(MatrixFactorization, self).__init__()
            
            self.global_mean = global_mean
            
            # User embeddings: latent factors + bias
            self.user_factors = nn.Embedding(n_users, n_factors)
            self.user_bias = nn.Embedding(n_users, 1)
            
            # Item embeddings: latent factors + bias
            self.movie_factors = nn.Embedding(n_movies, n_factors)
            self.movie_bias = nn.Embedding(n_movies, 1)
            
        def forward(self, user_idx, movie_idx):
            # Get embeddings
            user_emb = self.user_factors(user_idx)
            movie_emb = self.movie_factors(movie_idx)
            user_b = self.user_bias(user_idx).squeeze()
            movie_b = self.movie_bias(movie_idx).squeeze()
            
            # Dot product of user and movie factors
            dot_product = (user_emb * movie_emb).sum(dim=1)
            
            # Final prediction
            prediction = self.global_mean + user_b + movie_b + dot_product
            return prediction
        
        def predict(self, user_idx, movie_idx):
            """Predict with clipping to valid rating range [0.5, 5.0]."""
            with torch.no_grad():
                pred = self.forward(user_idx, movie_idx)
                pred = torch.clamp(pred, 0.5, 5.0)
            return pred

# --- Global Variables for Data and Models ---
svd_model = None           # Surprise SVD model
mf_model = None            # PyTorch MF model
mf_config = None           # PyTorch model config
mf_mappings = None         # PyTorch model mappings (user_to_idx, movie_to_idx)
mf_global_mean = 0.0       # Global mean rating for MF model
cosine_sim_matrix = None
movies_df = None
ratings_df = None
movie_id_to_index = {}
index_to_movie_id = {}
active_cf_model = None     # 'svd', 'mf', or None

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
    global svd_model, mf_model, mf_config, mf_mappings, mf_global_mean
    global cosine_sim_matrix, movies_df, ratings_df
    global movie_id_to_index, index_to_movie_id, active_cf_model

    if not os.path.exists(MODEL_DIR):
        logger.warning(f"Thư mục models/ không tồn tại: {MODEL_DIR}")
        logger.warning("Hãy chạy 'python train.py' trước để train model!")
        return False

    loaded = False

    # === COLLABORATIVE FILTERING MODELS ===
    
    # Option 1: Load SVD model (Surprise) - ưu tiên nếu có
    svd_path = os.path.join(MODEL_DIR, 'svd_model.pkl')
    if os.path.exists(svd_path):
        try:
            svd_model = joblib.load(svd_path)
            active_cf_model = 'svd'
            logger.info(f"✅ Đã load SVD model từ {svd_path}")
            loaded = True
        except ModuleNotFoundError as e:
            logger.warning(f"Không thể load SVD model do thiếu module: {e}")
            svd_model = None
        except Exception as e:
            logger.warning(f"Không thể load SVD model: {e}")
            svd_model = None
    
    # Option 2: Load PyTorch MF model (GPU-trained) - fallback nếu không có SVD
    if svd_model is None and TORCH_AVAILABLE:
        mf_path = os.path.join(MODEL_DIR, 'mf_model_gpu.pt')
        mf_mappings_path = os.path.join(MODEL_DIR, 'mappings_gpu.pkl')
        
        if os.path.exists(mf_path) and os.path.exists(mf_mappings_path):
            try:
                # Load mappings first
                mf_mappings = joblib.load(mf_mappings_path)
                
                # Load model checkpoint
                checkpoint = torch.load(mf_path, map_location='cpu', weights_only=False)
                mf_config = checkpoint.get('config', {})
                n_users = checkpoint.get('n_users', len(mf_mappings['user_to_idx']))
                n_movies = checkpoint.get('n_movies', len(mf_mappings['movie_to_idx']))
                n_factors = mf_config.get('n_factors', 100)
                mf_global_mean = checkpoint.get('global_mean', 3.5)
                
                # Recreate model and load weights (pass global_mean to constructor)
                mf_model = MatrixFactorization(n_users, n_movies, n_factors, mf_global_mean)
                mf_model.load_state_dict(checkpoint['model_state_dict'])
                mf_model.eval()  # Set to evaluation mode
                
                active_cf_model = 'mf'
                logger.info(f"✅ Đã load PyTorch MF model: {n_users} users, {n_movies} movies, {n_factors} factors")
                logger.info(f"   Best RMSE: {checkpoint.get('best_rmse', 'N/A')}")
                loaded = True
            except Exception as e:
                logger.warning(f"Không thể load PyTorch MF model: {e}")
                mf_model = None

    # Load ratings DataFrame
    ratings_path = os.path.join(MODEL_DIR, 'ratings_df.pkl')
    if os.path.exists(ratings_path):
        ratings_df = joblib.load(ratings_path)
        logger.info(f"✅ Đã load ratings DataFrame ({len(ratings_df)} rows)")

    # === CONTENT-BASED MODEL ===
    
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

    # Load mappings (content_mappings.pkl từ notebook)
    mapping_path = os.path.join(MODEL_DIR, 'content_mappings.pkl')
    if os.path.exists(mapping_path):
        mappings = joblib.load(mapping_path)
        movie_id_to_index = mappings['movie_id_to_index']
        index_to_movie_id = mappings['index_to_movie_id']
        logger.info(f"✅ Đã load content mappings ({len(movie_id_to_index)} phim)")

    return loaded


def predict_rating_mf(user_id: int, movie_id: int) -> float:
    """Predict rating using PyTorch MF model"""
    if mf_model is None or mf_mappings is None:
        return None
    
    user_to_idx = mf_mappings['user_to_idx']
    movie_to_idx = mf_mappings['movie_to_idx']
    
    # Check if user and movie exist in training data
    if user_id not in user_to_idx or movie_id not in movie_to_idx:
        return None
    
    user_idx = user_to_idx[user_id]
    movie_idx = movie_to_idx[movie_id]
    
    with torch.no_grad():
        user_tensor = torch.LongTensor([user_idx])
        movie_tensor = torch.LongTensor([movie_idx])
        pred = mf_model(user_tensor, movie_tensor)
        return float(pred.item() + mf_global_mean)

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
        "collaborative_filtering": active_cf_model,  # 'svd', 'mf', or None
        "svd": svd_model is not None,
        "pytorch_mf": mf_model is not None,
        "content_based": cosine_sim_matrix is not None,
        "movies_loaded": len(movies_df) if movies_df is not None else 0
    }
    return {"status": "AI Service Running", "models": models_status}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, limit: int = 10):
    """
    Get personalized recommendations using collaborative filtering (SVD or MF) 
    or content-based filtering as fallback.
    Returns list of Movie IDs.
    """
    if movies_df is None:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10][:limit]

    try:
        # === Option 1: Use Surprise SVD model ===
        if active_cf_model == 'svd' and svd_model is not None and ratings_df is not None:
            all_movie_ids = movies_df['movieId'].unique()
            user_ratings = ratings_df[ratings_df['userId'] == user_id]
            rated_movies = set(user_ratings['movieId'].values)

            predictions = []
            for movie_id in all_movie_ids[:1000]:
                if movie_id not in rated_movies:
                    try:
                        pred = svd_model.predict(user_id, movie_id)
                        predictions.append((int(movie_id), pred.est))
                    except:
                        pass

            if predictions:
                predictions.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"[SVD] Recommendations for user {user_id}: {[p[0] for p in predictions[:limit]]}")
                return [p[0] for p in predictions[:limit]]

        # === Option 2: Use PyTorch MF model ===
        if active_cf_model == 'mf' and mf_model is not None and mf_mappings is not None:
            movie_to_idx = mf_mappings['movie_to_idx']
            idx_to_movie = mf_mappings['idx_to_movie']
            user_to_idx = mf_mappings['user_to_idx']
            
            # Check if user exists in training data
            if user_id in user_to_idx:
                user_idx = user_to_idx[user_id]
                
                # Get movies user has rated
                rated_movies = set()
                if ratings_df is not None:
                    user_ratings = ratings_df[ratings_df['userId'] == user_id]
                    rated_movies = set(user_ratings['movieId'].values)
                
                # Predict ratings for all movies (batch prediction for speed)
                predictions = []
                unrated_movies = [(mid, midx) for mid, midx in movie_to_idx.items() 
                                  if mid not in rated_movies]
                
                # Use model's predict method (includes clipping)
                with torch.no_grad():
                    for movie_id, movie_idx in unrated_movies:
                        user_tensor = torch.LongTensor([user_idx])
                        movie_tensor = torch.LongTensor([movie_idx])
                        pred = mf_model.predict(user_tensor, movie_tensor)
                        rating = float(pred.item())
                        predictions.append((int(movie_id), rating))
                
                if predictions:
                    predictions.sort(key=lambda x: x[1], reverse=True)
                    result = [p[0] for p in predictions[:limit]]
                    logger.info(f"[MF-PyTorch] Recommendations for user {user_id}: {result}")
                    return result

        # === Fallback: Content-based / Random ===
        movie_ids = [int(x) for x in movies_df['movieId'].head(limit * 3).values]
        import random
        random.seed(user_id)
        random.shuffle(movie_ids)
        logger.info(f"[Fallback] Recommendations for user {user_id}: {movie_ids[:limit]}")
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
def get_recommendations_based_on_movies(movie_ids: list[int], limit: int = 10, refresh: bool = False):
    """
    Get recommendations based on a list of movie IDs (e.g., from user's watchlist).
    Uses content-based filtering to find similar movies.
    """
    if movies_df is None or cosine_sim_matrix is None:
        # Fallback
        return [int(x) for x in movies_df['movieId'].head(limit).values] if movies_df is not None else []

    try:
        import random
        import time
        
        # Seed random - use different seed when refresh is True
        if refresh:
            random.seed(int(time.time() * 1000))
        else:
            random.seed(sum(movie_ids))  # Consistent results based on watchlist
        
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
            # Sort by similarity score
            sorted_movies = sorted(all_similar.items(), key=lambda x: x[1], reverse=True)
            
            # Add randomization: shuffle movies with similar scores when refreshing
            if refresh:
                # Group by similar scores (within 0.05 threshold) and shuffle within groups
                result_pool = sorted_movies[:limit * 3]  # Get more candidates
                random.shuffle(result_pool)
                # Re-sort with some randomness
                result_pool.sort(key=lambda x: x[1] + random.uniform(-0.1, 0.1), reverse=True)
                result = [int(movie_id) for movie_id, score in result_pool[:limit]]
            else:
                result = [int(movie_id) for movie_id, score in sorted_movies[:limit]]
            
            logger.info(f"Recommendations based on {len(movie_ids)} watchlist movies (refresh={refresh}): {result}")
            return result

        # Fallback if no similar movies found
        return [int(x) for x in movies_df['movieId'].head(limit).values]

    except Exception as e:
        logger.error(f"Error getting watchlist-based recommendations: {e}")
        return [int(x) for x in movies_df['movieId'].head(limit).values]


# --- Pydantic models for personalized recommendations ---
class RatedMovie(BaseModel):
    movieId: int
    rating: float

class PersonalizedRequest(BaseModel):
    preferredGenres: List[str]
    ratedMovies: Optional[List[RatedMovie]] = []
    limit: int = 10
    userId: Optional[int] = None  # Added for user-specific randomization
    refresh: Optional[bool] = False  # When True, generate different results


@app.post("/recommendations/personalized")
def get_personalized_recommendations(request: PersonalizedRequest):
    """
    Get personalized recommendations based on user's preferred genres and rated movies.
    This endpoint is designed for NEW users who are not in the pre-trained collaborative filtering models.
    Uses content-based filtering with genre preferences.
    """
    if movies_df is None:
        logger.warning("Movies data not loaded")
        return []

    try:
        preferred_genres = set(g.lower() for g in request.preferredGenres)
        rated_movie_ids = set(rm.movieId for rm in request.ratedMovies) if request.ratedMovies else set()
        
        logger.info(f"[Personalized] User: {request.userId}, Genres: {preferred_genres}, Rated movies: {len(rated_movie_ids)}, Refresh: {request.refresh}")
        
        # Seed random - use different seed when refresh is True
        import random
        import time
        if request.refresh:
            # Use timestamp for random results when refreshing
            random.seed(int(time.time() * 1000))
        elif request.userId:
            random.seed(request.userId)
        else:
            # Fallback: use hash of preferences for some variation
            seed_value = hash(frozenset(preferred_genres)) + len(rated_movie_ids)
            random.seed(seed_value)
        
        # Strategy 1: If user has rated movies with high ratings, find similar movies
        if request.ratedMovies and cosine_sim_matrix is not None:
            high_rated_movies = [rm.movieId for rm in request.ratedMovies if rm.rating >= 3.5]
            
            if high_rated_movies:
                all_similar = {}
                
                for movie_id in high_rated_movies:
                    if movie_id not in movie_id_to_index:
                        continue
                    
                    idx = movie_id_to_index[movie_id]
                    if idx >= cosine_sim_matrix.shape[0]:
                        continue
                    
                    sim_scores = cosine_sim_matrix[idx]
                    
                    for i, score in enumerate(sim_scores):
                        if i in index_to_movie_id:
                            similar_movie_id = index_to_movie_id[i]
                            # Don't recommend movies user already rated
                            if similar_movie_id not in rated_movie_ids:
                                if similar_movie_id in all_similar:
                                    all_similar[similar_movie_id] = max(all_similar[similar_movie_id], score)
                                else:
                                    all_similar[similar_movie_id] = score
                
                if all_similar:
                    # Boost scores for movies matching preferred genres
                    for movie_id in list(all_similar.keys()):
                        movie_row = movies_df[movies_df['movieId'] == movie_id]
                        if not movie_row.empty:
                            genres_str = str(movie_row.iloc[0].get('genres', '')).lower()
                            genre_matches = sum(1 for g in preferred_genres if g in genres_str)
                            if genre_matches > 0:
                                all_similar[movie_id] *= (1 + 0.2 * genre_matches)
                    
                    sorted_movies = sorted(all_similar.items(), key=lambda x: x[1], reverse=True)
                    result = [int(movie_id) for movie_id, score in sorted_movies[:request.limit]]
                    logger.info(f"[Personalized-Similarity] Recommendations: {result}")
                    return result
        
        # Strategy 2: Genre-based filtering - find movies matching user's preferred genres
        if preferred_genres:
            genre_scores = []
            
            for idx, row in movies_df.iterrows():
                movie_id = row['movieId']
                
                # Skip already rated movies
                if movie_id in rated_movie_ids:
                    continue
                
                genres_str = str(row.get('genres', '')).lower()
                movie_genres = set(genres_str.split('|'))
                
                # Count matching genres
                match_count = len(preferred_genres & movie_genres)
                
                if match_count > 0:
                    # Score based on number of matching genres
                    genre_scores.append((int(movie_id), match_count))
            
            if genre_scores:
                # Sort by match count, then shuffle within same score for variety
                # Random is already seeded above with userId
                random.shuffle(genre_scores)
                genre_scores.sort(key=lambda x: x[1], reverse=True)
                
                result = [movie_id for movie_id, score in genre_scores[:request.limit]]
                logger.info(f"[Personalized-Genre] Recommendations: {result}")
                return result
        
        # Fallback: Return diverse movies
        logger.info("[Personalized-Fallback] Using random diverse movies")
        all_movie_ids = [int(x) for x in movies_df['movieId'].values]
        # Random is already seeded above with userId
        random.shuffle(all_movie_ids)
        return all_movie_ids[:request.limit]
    
    except Exception as e:
        logger.error(f"Error in personalized recommendations: {e}")
        import traceback
        traceback.print_exc()
        return []


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "collaborative_filtering": active_cf_model,
        "svd_model": svd_model is not None,
        "pytorch_mf_model": mf_model is not None,
        "content_model": cosine_sim_matrix is not None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
