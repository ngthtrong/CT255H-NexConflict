"""
train.py - Script train model riêng biệt
Chạy: python train.py
Output: Lưu model SVD và Cosine Similarity Matrix vào thư mục models/
"""

import pandas as pd
import numpy as np
import os
import joblib
import logging
import time

try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import cross_validate
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    print("WARNING: scikit-surprise not installed. Run: pip install scikit-surprise")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Cấu hình ---
# Đường dẫn tới thư mục data
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
# Thư mục lưu model
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

# === Tham số SVD (Collaborative Filtering) ===
SVD_PARAMS = {
    'n_factors': 100,      # Số lượng latent factors (chiều không gian ẩn)
    'n_epochs': 20,        # Số vòng lặp training (gradient descent)
    'lr_all': 0.005,       # Learning rate cho tất cả parameters
    'reg_all': 0.02,       # Regularization factor (chống overfitting)
    'random_state': 42,    # Seed cho reproducibility
}

# === Tham số Content-Based Filtering ===
CONTENT_PARAMS = {
    'max_movies': 5000,    # Số phim tối đa để tính cosine similarity matrix
}

# Số dòng ratings tối đa để train (None = dùng toàn bộ)
MAX_RATINGS_ROWS = 200000


def find_data_file(filename):
    """Tìm file data trong các đường dẫn có thể."""
    possible_paths = [
        os.path.join(DATA_DIR, filename),
        os.path.join('..', 'data', filename),
        os.path.join('data', filename),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None


def train_svd_model():
    """
    Train model SVD (Singular Value Decomposition) cho Collaborative Filtering.
    
    SVD phân rã ma trận ratings (User x Movie) thành 3 ma trận:
        R ≈ U × Σ × V^T
    Trong đó:
        - U: ma trận user latent factors (mỗi user = 1 vector n_factors chiều)
        - Σ: ma trận diagonal chứa singular values
        - V: ma trận item latent factors (mỗi phim = 1 vector n_factors chiều)
    
    Dự đoán rating: r̂(u,i) = μ + b_u + b_i + q_i^T × p_u
    Trong đó:
        - μ: rating trung bình toàn hệ thống
        - b_u: bias của user u
        - b_i: bias của item i
        - q_i: latent factor vector của item i
        - p_u: latent factor vector của user u
    """
    if not SURPRISE_AVAILABLE:
        logger.error("scikit-surprise chưa được cài đặt!")
        return None

    ratings_path = find_data_file('ratings.csv')
    if not ratings_path:
        logger.error("Không tìm thấy ratings.csv!")
        return None

    logger.info(f"Đọc ratings từ: {ratings_path}")
    
    if MAX_RATINGS_ROWS:
        ratings_df = pd.read_csv(ratings_path, nrows=MAX_RATINGS_ROWS)
        logger.info(f"Đã load {len(ratings_df)} ratings (giới hạn {MAX_RATINGS_ROWS} dòng)")
    else:
        ratings_df = pd.read_csv(ratings_path)
        logger.info(f"Đã load toàn bộ {len(ratings_df)} ratings")

    # Thống kê
    n_users = ratings_df['userId'].nunique()
    n_movies = ratings_df['movieId'].nunique()
    logger.info(f"Số users: {n_users}, Số movies: {n_movies}")
    logger.info(f"Rating trung bình: {ratings_df['rating'].mean():.2f}")
    logger.info(f"Sparsity: {1 - len(ratings_df) / (n_users * n_movies):.4%}")

    # Chuẩn bị data cho Surprise
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)

    # Cross-validation để đánh giá model
    logger.info("Đang cross-validate SVD model...")
    logger.info(f"Tham số SVD: {SVD_PARAMS}")
    
    svd = SVD(**SVD_PARAMS)
    
    cv_results = cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=3, verbose=True)
    logger.info(f"RMSE trung bình: {cv_results['test_rmse'].mean():.4f}")
    logger.info(f"MAE trung bình: {cv_results['test_mae'].mean():.4f}")

    # Train trên toàn bộ data
    logger.info("Đang train SVD trên toàn bộ dữ liệu...")
    start_time = time.time()
    
    trainset = data.build_full_trainset()
    svd_final = SVD(**SVD_PARAMS)
    svd_final.fit(trainset)
    
    train_time = time.time() - start_time
    logger.info(f"Train xong trong {train_time:.2f} giây")

    return svd_final, ratings_df


def build_content_model():
    """
    Build Content-Based Filtering model dùng GENOME-SCORES + Cosine Similarity.

    Thuật toán:
    1. Genome Scores (MovieLens):
       - Mỗi phim có 1,128 tags với relevance score (0-1)
       - Các tags sâu như: 'dark comedy', 'space travel', 'twist ending'
       - Điểm relevance càng cao = tag càng phù hợp với phim

    2. Cosine Similarity:
       - Đo độ tương đồng giữa 2 vector genome scores
       - cos(A,B) = (A·B) / (||A|| × ||B||)
       - Giá trị từ 0 (khác hoàn toàn) đến 1 (giống hoàn toàn)
       - Kết quả: ma trận NxN (N = số phim), mỗi ô = độ tương đồng giữa 2 phim

    So với TF-IDF genres:
       - Genres: chỉ có ~20 categories (Action, Comedy, Drama...)
       - Genome: có 1,128 tags chi tiết → tìm phim tương tự CHÍNH XÁC hơn
    """
    movies_path = find_data_file('movies.csv')
    if not movies_path:
        logger.error("Không tìm thấy movies.csv!")
        return None, None, None, None

    logger.info(f"Đọc movies từ: {movies_path}")
    movies_df = pd.read_csv(movies_path)
    movies_df = movies_df.reset_index(drop=True)
    logger.info(f"Đã load {len(movies_df)} phim")

    # === Load Genome Scores ===
    genome_path = find_data_file('genome-scores.csv')
    genome_tags_path = find_data_file('genome-tags.csv')

    if genome_path and genome_tags_path:
        logger.info("=" * 50)
        logger.info("Đang load GENOME SCORES cho Content-Based Filtering...")
        logger.info(f"File: {genome_path}")

        # Load genome scores (có thể lớn, load theo chunks)
        logger.info("Đang đọc genome-scores.csv (có thể mất vài phút)...")
        genome_scores = pd.read_csv(genome_path)
        logger.info(f"Đã load {len(genome_scores)} genome scores")

        # Load genome tags để biết tên tag
        genome_tags = pd.read_csv(genome_tags_path)
        logger.info(f"Số tags: {len(genome_tags)} (VD: {', '.join(genome_tags['tag'].head(5).tolist())})")

        # Pivot: mỗi hàng = 1 phim, mỗi cột = 1 tag, giá trị = relevance
        logger.info("Đang pivot genome scores thành movie-tag matrix...")
        genome_matrix = genome_scores.pivot(
            index='movieId',
            columns='tagId',
            values='relevance'
        ).fillna(0)

        logger.info(f"Genome matrix shape: {genome_matrix.shape}")
        logger.info(f"Số phim có genome data: {len(genome_matrix)}")

        # Lọc chỉ giữ những phim có trong cả movies.csv và genome-scores
        common_movie_ids = list(set(movies_df['movieId'].values) & set(genome_matrix.index))
        logger.info(f"Số phim có cả info và genome: {len(common_movie_ids)}")

        # Filter movies_df để chỉ giữ phim có genome data
        movies_df = movies_df[movies_df['movieId'].isin(common_movie_ids)].reset_index(drop=True)

        # Tạo mappings mới dựa trên movies_df đã filter
        movie_id_to_index = {}
        index_to_movie_id = {}
        for idx, row in movies_df.iterrows():
            movie_id_to_index[row['movieId']] = idx
            index_to_movie_id[idx] = row['movieId']

        # Sắp xếp genome_matrix theo thứ tự movies_df
        genome_matrix = genome_matrix.loc[movies_df['movieId'].values]
        genome_array = genome_matrix.values

        logger.info(f"Final genome array shape: {genome_array.shape}")

        # Tính Cosine Similarity
        max_movies = min(CONTENT_PARAMS['max_movies'], genome_array.shape[0])
        logger.info(f"Đang tính Cosine Similarity matrix ({max_movies}x{max_movies})...")
        logger.info("(Sử dụng 1,128 genome tags - ĐỘ CHÍNH XÁC CAO)")

        start_time = time.time()
        cosine_sim = cosine_similarity(genome_array[:max_movies], genome_array[:max_movies])
        build_time = time.time() - start_time

        logger.info(f"Cosine matrix shape: {cosine_sim.shape}")
        logger.info(f"Build xong trong {build_time:.2f} giây")
        logger.info("=" * 50)

        return cosine_sim, movies_df, movie_id_to_index, index_to_movie_id

    # === Fallback: dùng TF-IDF genres nếu không có genome ===
    logger.warning("Không tìm thấy genome-scores.csv, fallback sang TF-IDF genres...")

    # Tạo mappings
    movie_id_to_index = {}
    index_to_movie_id = {}
    for idx, row in movies_df.iterrows():
        movie_id_to_index[row['movieId']] = idx
        index_to_movie_id[idx] = row['movieId']

    # TF-IDF trên genres
    if 'genres' not in movies_df.columns:
        logger.error("Không tìm thấy cột 'genres' trong movies.csv!")
        return None, None, None, None

    movies_df['genres_str'] = movies_df['genres'].fillna('').str.replace('|', ' ', regex=False)

    logger.info("Đang tính TF-IDF matrix (fallback - chỉ dùng genres)...")
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['genres_str'])
    logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    logger.info(f"Số features (genres): {len(tfidf.get_feature_names_out())}")

    # Cosine similarity matrix
    max_movies = min(CONTENT_PARAMS['max_movies'], tfidf_matrix.shape[0])
    logger.info(f"Đang tính Cosine Similarity matrix ({max_movies}x{max_movies})...")

    start_time = time.time()
    cosine_sim = cosine_similarity(tfidf_matrix[:max_movies], tfidf_matrix[:max_movies])
    build_time = time.time() - start_time

    logger.info(f"Cosine matrix shape: {cosine_sim.shape}")
    logger.info(f"Build xong trong {build_time:.2f} giây")

    return cosine_sim, movies_df, movie_id_to_index, index_to_movie_id


def save_models(svd_model, ratings_df, cosine_sim, movies_df, movie_id_to_index, index_to_movie_id):
    """Lưu tất cả models và data vào thư mục models/"""
    os.makedirs(MODEL_DIR, exist_ok=True)

    if svd_model is not None:
        svd_path = os.path.join(MODEL_DIR, 'svd_model.pkl')
        joblib.dump(svd_model, svd_path)
        logger.info(f"Đã lưu SVD model: {svd_path}")

    if ratings_df is not None:
        ratings_path = os.path.join(MODEL_DIR, 'ratings_df.pkl')
        joblib.dump(ratings_df, ratings_path)
        logger.info(f"Đã lưu ratings DataFrame: {ratings_path}")

    if cosine_sim is not None:
        cosine_path = os.path.join(MODEL_DIR, 'cosine_sim_matrix.pkl')
        joblib.dump(cosine_sim, cosine_path)
        logger.info(f"Đã lưu Cosine Similarity matrix: {cosine_path}")

    if movies_df is not None:
        movies_path = os.path.join(MODEL_DIR, 'movies_df.pkl')
        joblib.dump(movies_df, movies_path)
        logger.info(f"Đã lưu movies DataFrame: {movies_path}")

    if movie_id_to_index:
        mapping_path = os.path.join(MODEL_DIR, 'mappings.pkl')
        joblib.dump({
            'movie_id_to_index': movie_id_to_index,
            'index_to_movie_id': index_to_movie_id
        }, mapping_path)
        logger.info(f"Đã lưu mappings: {mapping_path}")

    logger.info(f"\n✅ Tất cả models đã được lưu vào: {os.path.abspath(MODEL_DIR)}")


def main():
    logger.info("=" * 60)
    logger.info("   CINESTREAM AI - TRAIN MODELS")
    logger.info("=" * 60)

    # 1. Train SVD
    svd_result = train_svd_model()
    svd_model = None
    ratings_df = None
    if svd_result:
        svd_model, ratings_df = svd_result

    # 2. Build Content-Based model
    cosine_sim, movies_df, movie_id_to_index, index_to_movie_id = build_content_model()

    # 3. Lưu models
    save_models(svd_model, ratings_df, cosine_sim, movies_df, movie_id_to_index, index_to_movie_id)

    logger.info("\n🎬 Training hoàn tất!")
    logger.info("Chạy server: python main.py")


if __name__ == "__main__":
    main()
