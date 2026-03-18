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

def load_data():
    global movies_df, movie_id_to_index
    
    # Paths - Update these to point to your actual data location
    # Assuming ai-service is at root, and data is in ../data/ or ./data
    # Trying absolute or relative paths
    possible_paths = [
        "../data/movies.csv", 
        "data/movies.csv",
        "../../data/movies.csv",
        r"D:\CT255H - BI\Project\CT255H-NexConflict\data\movies.csv"
    ]
    
    movies_path = None
    for p in possible_paths:
        if os.path.exists(p):
            movies_path = p
            break
            
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
    for idx, row in movies_df.iterrows():
        movie_id_to_index[row['movieId']] = idx

def train_svd():
    global svd_model
    logger.info("Training SVD Model (Mock/Light)...")
    
    # In a real scenario, load ratings.csv. 
    # For this MVP startup, we will train on a tiny subset or dummy if file too big/missing
    # to allow fast server start.
    
    # Try finding ratings.csv
    possible_paths = [
        "../data/ratings.csv", 
        "data/ratings.csv",
        "../../data/ratings.csv",
        r"D:\CT255H - BI\Project\CT255H-NexConflict\data\ratings.csv"
    ]
    ratings_path = None
    for p in possible_paths:
        if os.path.exists(p):
            ratings_path = p
            break
            
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
        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix) # Might be heavy on memory for 20M
        logger.info(f"Cosine Matrix built: {cosine_sim_matrix.shape}")

# --- Startup ---
@app.on_event("startup")
def startup_event():
    load_data()
    # Uncomment lines below to enable real training (takes time)
    # train_svd()
    # build_content_filtering() 
    
    # Mocking for fast response if models not loaded
    pass

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
    if svd_model:
        # Predict logic here
        pass
    
    # Mock return for visual validation
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

@app.get("/similar/{movie_id}")
def get_similar_movies(movie_id: int):
    """
    Get similar movies based on content (genres).
    """
    # Simple Mock: Return next 5 movies sequentially
    return [movie_id + 1, movie_id + 2, movie_id + 3, movie_id + 4, movie_id + 5]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
