# AGENT 1: Data Pipeline
# Vai trò: Xây dựng toàn bộ data loading và preprocessing

## BỐI CẢNH DỰ ÁN
Đây là ứng dụng Web gợi ý phim (Movie Recommendation) sử dụng MovieLens 20M Dataset.
- Tech: Python 3.10+, pandas, numpy, scikit-surprise
- Kiến trúc: xem docs/ARCHITECTURE.md
- Thuật toán: xem docs/10-algorithm-detail.md

## NHIỆM VỤ
Tạo 2 file trong `src/data/`:
1. `src/data/__init__.py`
2. `src/data/loader.py` — Load raw CSV data, sampling
3. `src/data/preprocessor.py` — Clean, split, feature engineering

## RÀNG BUỘC
- Dữ liệu CSV nằm ở `data/` (cùng cấp với `src/`)
- Chỉ sử dụng 2 file chính: `rating.csv` và `movie.csv` (các file khác optional)
- Dùng dtype tối ưu: int32 cho userId/movieId, float32 cho rating
- Sample mặc định 5000 users cho development
- Phải dùng `pathlib.Path` cho file paths
- Dùng `logging` module, KHÔNG dùng print
- Type hints cho tất cả public functions

## FILE 1: src/data/loader.py

### Functions cần tạo:

```python
def get_data_dir() -> Path:
    """Trả về đường dẫn đến thư mục data/"""

def load_ratings(data_dir: Path = None) -> pd.DataFrame:
    """
    Load rating.csv
    - Columns: userId(int32), movieId(int32), rating(float32), timestamp(int64)
    - Parse từ CSV, cast dtypes
    - Log số dòng loaded
    Returns: pd.DataFrame
    """

def load_movies(data_dir: Path = None) -> pd.DataFrame:
    """
    Load movie.csv
    - Columns: movieId(int32), title(str), genres(str)
    - genres format: "Action|Comedy|Drama" (pipe-separated)
    Returns: pd.DataFrame
    """

def sample_data(ratings: pd.DataFrame, n_users: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Lấy mẫu ngẫu nhiên n_users users và tất cả ratings của họ
    - Random sample userId
    - Giữ tất cả ratings của sampled users
    - Log số users, ratings trước/sau sample
    Returns: pd.DataFrame (sampled ratings)
    """

def get_stats(ratings: pd.DataFrame, movies: pd.DataFrame) -> dict:
    """
    Thống kê cơ bản:
    - n_users, n_items, n_ratings
    - sparsity = 1 - n_ratings / (n_users * n_items)
    - avg_ratings_per_user, avg_ratings_per_item
    - rating_distribution (counts per rating value)
    Returns: dict với các key trên
    """
```

## FILE 2: src/data/preprocessor.py

### Functions cần tạo:

```python
def filter_sparse(
    ratings: pd.DataFrame,
    min_user_ratings: int = 20,
    min_item_ratings: int = 10
) -> pd.DataFrame:
    """
    Lọc bỏ users có ít hơn min_user_ratings ratings
    Lọc bỏ items có ít hơn min_item_ratings ratings
    Lặp lại cho đến khi stable (iterative filtering)
    Log số users/items trước/sau filter
    """

def extract_year(title: str) -> int | None:
    """
    Trích xuất năm từ title. VD: "Toy Story (1995)" → 1995
    Dùng regex. Return None nếu không tìm thấy.
    """

def parse_genres(genres_str: str) -> list[str]:
    """
    Parse "Action|Comedy|Drama" → ["Action", "Comedy", "Drama"]
    Handle "(no genres listed)" → []
    """

def enrich_movies(movies: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm các cột vào movies DataFrame:
    - year: extracted từ title
    - genres_list: list[str] parsed từ genres
    - avg_rating: trung bình rating
    - num_ratings: số lượng ratings
    Returns: enriched movies DataFrame
    """

def time_split(ratings: pd.DataFrame, train_ratio: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split theo timestamp:
    - Sort by timestamp
    - 80% cũ nhất → train
    - 20% mới nhất → test
    Returns: (train_df, test_df)
    """

def create_surprise_dataset(ratings_df: pd.DataFrame) -> tuple:
    """
    Convert pandas DataFrame → Surprise Dataset
    - Reader(rating_scale=(0.5, 5.0))
    - Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)
    - Build trainset
    Returns: (trainset, testset_as_list)
    """

def get_popular_movies(movies: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    """
    Top-N phim phổ biến nhất (nhiều ratings VÀ rating cao)
    - Filter: num_ratings >= 100
    - Sort by: avg_rating * log(num_ratings) (weighted)
    Returns: DataFrame [movieId, title, genres, avg_rating, num_ratings]
    """

def get_movies_by_genre(movies: pd.DataFrame, genre: str) -> pd.DataFrame:
    """Filter phim theo genre (case-insensitive, partial match trên genres column)"""

def get_all_genres(movies: pd.DataFrame) -> list[str]:
    """Trả về danh sách tất cả genres unique trong dataset, sorted alphabetically"""
```

## FILE 3: src/data/__init__.py

```python
from .loader import load_ratings, load_movies, sample_data, get_stats
from .preprocessor import (
    filter_sparse, enrich_movies, time_split,
    create_surprise_dataset, get_popular_movies,
    get_movies_by_genre, get_all_genres
)
```

## DATASET FORMAT (để reference)
```
rating.csv: userId,movieId,rating,timestamp
movie.csv:  movieId,title,genres
```
- rating values: 0.5 to 5.0 (bước 0.5)
- genres: pipe-separated, e.g. "Action|Adventure|Sci-Fi"
- title format: "Movie Name (Year)", e.g. "Toy Story (1995)"

## TEST PLAN
Sau khi code xong, tạo script test đơn giản:
```python
# Ở cuối mỗi file, thêm:
if __name__ == "__main__":
    # Test basic functionality
    # Load → Sample → Filter → Split → Create Surprise Dataset
    # Print stats at each step
```

## DELIVERABLES
1. `src/data/__init__.py`
2. `src/data/loader.py` — hoàn chỉnh, có type hints, docstrings, logging
3. `src/data/preprocessor.py` — hoàn chỉnh, có type hints, docstrings, logging
