# NexConflict - Movie Recommendation System

Hệ thống gợi ý phim sử dụng Collaborative Filtering trên MovieLens 20M Dataset.

## Thuật toán
- Item-based KNN (Cosine Similarity)
- SVD (Matrix Factorization)
- Hybrid (Weighted KNN + SVD)

## Tech Stack
- **Frontend**: Gradio
- **ML**: scikit-surprise, scikit-learn
- **Data**: pandas, numpy
- **Visualization**: matplotlib, seaborn

## Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/ngthtrong/CT255H-NexConflict.git
cd CT255H-NexConflict
```

### 2. Tạo virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate     # Windows
```

### 3. Cài dependencies
```bash
pip install -r requirements.txt
```

### 4. Download data
Download MovieLens 20M dataset và đặt các file CSV vào thư mục `data/`:
- rating.csv
- movie.csv

### 5. Train models
```bash
python -m src.scripts.train
```

### 6. Chạy app
```bash
python -m src.app
```

Truy cập: http://localhost:7860

## Cấu trúc thư mục
Xem [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) để biết chi tiết kiến trúc hệ thống.

## Thành viên
- (Tên sinh viên 1)
- (Tên sinh viên 2)

## Môn học
CT255H - Ứng dụng và Máy học