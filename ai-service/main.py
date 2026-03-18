from fastapi import FastAPI, HTTPException
import uvicorn
import pandas as pd
import os
import joblib
try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import train_test_split
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    class SVD: pass # Dummy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CineStream AI Service", version="1.0.0")

# --- Global Variables for Data and Models ---
svd_model = None
cosine_sim_matrix = None
movies_df = None
indices = None # Map movie_id to matrix index
movie_id_to_index = {} # For cosine logic

# --- Data Loading & Model Training Functions ---

def _find_file(filename: str) -> str | None:
    """Search common relative paths for a data file and return the first match."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "..", "data", filename),
        os.path.join(base_dir, "data", filename),
        os.path.join(base_dir, "..", "..", "data", filename),
    ]
    for p in candidates:
        norm = os.path.normpath(p)
        if os.path.exists(norm):
            return norm
    return None

def load_data():
    global movies_df, movie_id_to_index, indices

    movies_path = _find_file("movies.csv")

    if not movies_path:
        logger.error("movies.csv not found!")
        # Create dummy data if file missing to prevent crash
        movies_df = pd.DataFrame({
            'movieId': [1, 2, 3],
            'title': ['Toy Story (1995)', 'Jumanji (1995)', 'Grumpier Old Men (1995)'],
            'genres': ['Adventure|Animation|Children|Comedy|Fantasy', 'Adventure|Children|Fantasy', 'Comedy|Romance']
        })
    else:
        logger.info(f"Loading movies from {movies_path}")
        movies_df = pd.read_csv(movies_path)

    # Create mapping for Cosine Similarity
    # Reset index to ensure linear 0..N indexing for matrix
    movies_df = movies_df.reset_index(drop=True)
    indices = pd.Series(movies_df.index, index=movies_df['movieId'])

    # Also create a reverse map if needed
    movie_id_to_index.clear()
    for idx, row in movies_df.iterrows():
        movie_id_to_index[int(row['movieId'])] = idx

def train_svd():
    global svd_model
    if not SURPRISE_AVAILABLE:
        logger.warning("scikit-surprise not available. Skipping SVD training.")
        return

    ratings_path = _find_file("ratings.csv")

    if ratings_path:
        # Load ONLY first 100k rows for speed in MVP/Dev
        logger.info(f"Loading ratings from {ratings_path} (limit 100k)")
        df = pd.read_csv(ratings_path, nrows=100000)
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)
        trainset = data.build_full_trainset()
        svd = SVD()
        svd.fit(trainset)
        svd_model = svd
        logger.info("SVD Model trained successfully")
    else:
        logger.warning("ratings.csv not found. SVD model will be None")

def build_content_filtering():
    global cosine_sim_matrix
    logger.info("Building Content-Based Matrix...")

    if movies_df is None:
        return

    # Use Genres for simple content-based filtering
    # Replace '|' with space to tokenize
    if 'genres' in movies_df.columns:
        movies_df['genres_str'] = movies_df['genres'].fillna('').str.replace('|', ' ')
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movies_df['genres_str'])
        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        logger.info(f"Cosine Matrix built: {cosine_sim_matrix.shape}")

# --- Startup ---
@app.on_event("startup")
def startup_event():
    load_data()
    train_svd()
    build_content_filtering()

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "AI Service Running", "models": "active"}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int):
    """
    Get generic personalized recommendations using SVD.
    Returns list of Movie IDs.
    """
    if svd_model and movies_df is not None and SURPRISE_AVAILABLE:
        try:
            all_movie_ids = movies_df['movieId'].tolist()
            # Predict ratings for all movies and pick the top 10
            predictions = [svd_model.predict(user_id, mid) for mid in all_movie_ids]
            predictions.sort(key=lambda x: x.est, reverse=True)
            top_ids = [int(p.iid) for p in predictions[:10]]
            return top_ids
        except Exception as e:
            logger.error(f"SVD prediction failed: {e}")

    # Fallback: return first 10 movie IDs from the dataset
    if movies_df is not None:
        return movies_df['movieId'].head(10).astype(int).tolist()
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

@app.get("/similar/{movie_id}")
def get_similar_movies(movie_id: int):
    """
    Get similar movies based on content (genres).
    """
    if cosine_sim_matrix is not None and movie_id in movie_id_to_index:
        idx = movie_id_to_index[movie_id]
        sim_scores = list(enumerate(cosine_sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Exclude itself; take top 5
        sim_scores = [s for s in sim_scores if s[0] != idx][:5]
        similar_ids = [int(movies_df.iloc[i[0]]['movieId']) for i in sim_scores]
        return similar_ids

    # Fallback: return next 5 sequential movie IDs
    if movies_df is not None:
        all_ids = movies_df['movieId'].tolist()
        try:
            pos = all_ids.index(movie_id)
            return [int(mid) for mid in all_ids[pos + 1: pos + 6]]
        except ValueError:
            pass
    return [movie_id + 1, movie_id + 2, movie_id + 3, movie_id + 4, movie_id + 5]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

