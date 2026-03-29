# Dataset và Library Support (AI Data Core) - Version 2

Hệ thống tận dụng nền tảng là Data Source **MovieLens 20M** và thư viện lõi **Surprise**.

## 1. Thành phần dữ liệu cần dùng từ MovieLens 20M

*   **`movies.csv`**:
    *   *Columns:* `movieId`, `title`, `genres`.
    *   *Mục đích:* Ánh xạ MovieID thành tên phim thực tế trả về cho người dùng và xử lý Content-based bề mặt (Genre).
*   **`ratings.csv`**:
    *   *Columns:* `userId`, `movieId`, `rating`, `timestamp`.
    *   *Mục đích:* Đây là nhiên liệu động cơ khổng lồ cho ML. Áp dụng cho **Thuật toán SVD**, tạo ma trận đánh giá cho phép ứng dụng học thói quen người dùng với hơn 20 triệu bản ghi.
*   **`genome-scores.csv` & `genome-tags.csv`**:
    *   *Columns:* `movieId`, `tagId`, `relevance` (Genome-scores) | `tagId`, `tag` (Genome-tags).
    *   *Mục đích:* Vũ khí bí mật cho **Content-Based Filtering**. Các tags cụ thể định nghĩa cái "chất" nội dung của phim (VD: "time-travel", "zombies", "dark comedy"). Giúp thuật toán đo độ tương đồng Cosine Similarity đạt hiệu quả sắc nét.

## 2. Các thư viện ML thiết yếu
*   **`scikit-surprise` (Surprise Library):** 
    *   Một library Python đỉnh cao thiết kế riêng rẽ để xây dựng và đánh giá hệ thống Recommender. Nó cung cấp hàm dựng sẵn `SVD`, `Dataset.load_from_df()`, và Reader API rất phù hợp cho dataset rating như MovieLens.
*   **`scikit-learn`**:
    *   Sử dụng module con `sklearn.metrics.pairwise.cosine_similarity` nhằm tính toán khoảng cách nội dung (vectors space) giữa hàng ngàn bộ phim trong nhánh làm Model 2 (Similar Movies).
*   **`pandas` & `numpy`**:
    *   Dùng để đọc Data CSV gốc, filter loại bỏ outliers, biến đổi bảng, merge bảng Tag thay SQL và chuẩn bị raw data đẩy vào Model training.
