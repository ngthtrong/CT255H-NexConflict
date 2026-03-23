# Thuật toán Gợi ý (Recommendation Algorithms) - Version 2

Ứng dụng sử dụng hệ thống gợi ý lai (**Hybrid Recommender System**) kết hợp giữa Collaborative Filtering và Content-Based Filtering nhằm tối ưu hóa kết quả dựa trên ngữ cảnh người dùng.

## 1. Lọc cộng tác (Collaborative Filtering - CF)
Thuật toán này được đặt ở màn hình Trang chủ (Home Page) cho những User đã thu thập đủ lượng dữ liệu đánh giá/thích phim.
- **Mô hình định hướng:** SVD (Singular Value Decomposition).
- **Thư viện:** `Surprise` (Python).
- **Cách thức hoạt động:** Phân tích ma trận User-Item từ tệp `ratings.csv`. SVD sẽ học các "đặc trưng ẩn" (latent features) của người dùng và phim để dự đoán số sao mà một người dùng có thể đánh giá cho bộ phim họ chưa từng xem.
- **Mục đích:** Gợi ý các phim mang tính "cá nhân hóa" (#Recommended For You).

## 2. Lọc theo nội dung (Content-Based Filtering)
Thuật toán này được đặt ở Trang chi tiết phim (Movie Detail).
- **Mô hình định hướng:** Cosine Similarity.
- **Thư viện:** `scikit-learn` & `pandas`.
- **Cách thức hoạt động:** Xây dựng Vector biểu diễn phim dựa trên `genome-scores.csv` (điểm số mức độ liên quan của hàng ngàn thẻ tag) và thể loại (genres) trong `movies.csv`. Sử dụng Cosine Similarity để tính điểm tương đồng giữa vector phim hiện tại và các vector phim khác trong dữ liệu.
- **Mục đích:** Gợi ý tập hợp "Phim tương tự" (More Like This) theo chiều sâu nội dung.

## 3. Giải quyết "Cold-Start" (Cho người dùng mới)
- **Thuật toán khởi tạo (Popularity-Based):** Tính toán và sắp xếp điểm rating trung bình có trọng số (weighted rating) kết hợp với số lượng đánh giá để tạo danh sách điểm chuẩn Top Trending.
- **Sử dụng để:** Khởi tạo dữ liệu người dùng trên màn hình Onboarding (chọn phim/thể loại) và đề xuất bộ khung chuẩn ở Trang chủ cho người mới.
