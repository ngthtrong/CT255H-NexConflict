# BÁO CÁO DỰ ÁN NEXCONFLICT

## Trọng tâm: Huấn luyện mô hình gợi ý phim

## 1. Giới thiệu đề tài

Dự án NexConflict xây dựng hệ thống gợi ý phim phục vụ học phần CT255H (Business Intelligence), mục tiêu là cá nhân hóa nội dung phim cho người dùng dựa trên dữ liệu đánh giá và đặc trưng nội dung phim.

Bài toán cốt lõi gồm:

- Gợi ý cá nhân hóa cho người dùng đã có lịch sử đánh giá (Collaborative Filtering).
- Gợi ý phim tương tự theo nội dung tại trang chi tiết phim (Content-Based Filtering).
- Hỗ trợ người dùng mới khi dữ liệu tương tác còn ít (Cold Start bằng danh sách phổ biến/trending và luồng onboarding).

Dự án triển khai theo kiến trúc tách lớp:

- Frontend: Next.js.
- Backend Core: Spring Boot.
- AI Service: FastAPI + pipeline học máy.

## 2. Giới thiệu lý thuyết mô hình

Hệ thống áp dụng mô hình Hybrid Recommender với hai nhánh chính.

### 2.1. Collaborative Filtering với SVD / Matrix Factorization

Ý tưởng: phân rã ma trận User-Item để học vector ẩn của người dùng và phim.

Công thức dự đoán rating:

$$
\hat{r}_{ui} = \mu + b_u + b_i + p_u^T q_i
$$

Trong đó:

- $\mu$: điểm trung bình toàn cục.
- $b_u$: độ lệch người dùng.
- $b_i$: độ lệch phim.
- $p_u, q_i$: vector latent factors.

Hai cách triển khai trong dự án:

- Pipeline 1 (production script): dùng thư viện Surprise (SVD) trong ai-service/train.py.
- Pipeline 2 (GPU notebook): dùng PyTorch Matrix Factorization để tăng tốc bằng CUDA trong notebook GPU.

### 2.2. Content-Based Filtering với Cosine Similarity

Mỗi phim được biểu diễn thành vector đặc trưng, sau đó tính độ tương đồng cosine:

$$
\text{cosine}(A,B) = \frac{A \cdot B}{\|A\|\|B\|}
$$

Nguồn đặc trưng:

- Ưu tiên genome-scores.csv (độ chi tiết cao, theo tag relevance).
- Fallback TF-IDF trên genres khi không có genome data.

## 3. Giới thiệu dataset

Dự án sử dụng bộ MovieLens, các file chính:

- ratings.csv: lịch sử chấm điểm user-movie.
- movies.csv: metadata phim (title, genres).
- genome-scores.csv + genome-tags.csv: vector liên quan nội dung (nếu có).

Đặc điểm dữ liệu trong pipeline hiện tại:

- train.py đang đặt MAX_RATINGS_ROWS = 200000 để kiểm soát thời gian train.
- Notebook GPU hỗ trợ chạy full hoặc sample tùy cấu hình.
- Dữ liệu có tính sparse cao do mỗi user chỉ đánh giá một phần rất nhỏ tổng số phim.

## 4. Trình bày quá trình training

Phần này mô tả theo đúng mã nguồn hiện tại.

### 4.1. Quy trình train Collaborative Filtering (ai-service/train.py)

1. Đọc ratings.csv, thống kê số user, số movie, sparsity.
2. Chuyển dữ liệu sang định dạng Surprise Dataset.
3. Khởi tạo SVD với cấu hình:
   - n_factors = 100
   - n_epochs = 20
   - lr_all = 0.005
   - reg_all = 0.02
   - random_state = 42
4. Cross-validation 3-fold với metrics RMSE và MAE.
5. Train model cuối trên toàn bộ tập trainset.
6. Lưu artifact:
   - svd_model.pkl
   - ratings_df.pkl

### 4.2. Quy trình train Content-Based (ai-service/train.py)

1. Đọc movies.csv.
2. Nếu có genome-scores.csv:
   - Pivot thành ma trận movie-tag.
   - Đồng bộ danh sách movieId giữa metadata và genome.
3. Nếu không có genome thì fallback TF-IDF genres.
4. Tính cosine similarity matrix với ngưỡng max_movies = 5000.
5. Lưu artifact:
   - cosine_sim_matrix.pkl
   - movies_df.pkl
   - mappings.pkl

### 4.3. Quy trình train GPU (notebook PyTorch)

1. Kiểm tra CUDA, cấu hình device.
2. Map userId/movieId sang index liên tục.
3. Chia train/test (80/20).
4. Huấn luyện Matrix Factorization bằng PyTorch với batch lớn (4096) để tận dụng GPU.
5. Theo dõi train loss, RMSE, MAE qua từng epoch.
6. Lưu model và mapping:
   - mf_model_gpu.pt
   - mappings_gpu.pkl
   - biểu đồ training_history_gpu.png, error_analysis_gpu.png

## 5. Kết quả training và đánh giá

### 5.1. Chỉ số đánh giá chính

Hai chỉ số được dùng xuyên suốt:

- RMSE: nhạy hơn với lỗi lớn.
- MAE: trực quan về sai số trung bình tuyệt đối.

### 5.2. Kết quả thực nghiệm ghi nhận

Theo notebook GPU của dự án:

- Best RMSE được ghi nhận ở khoảng 0.85 - 0.87.
- MAE đạt mức thấp tương ứng và hội tụ ổn định sau nhiều epoch.

Với pipeline Surprise trong train.py:

- Có bước cross-validation 3-fold để kiểm tra tính ổn định trước khi train full data.
- Kết quả RMSE/MAE được log theo từng lần chạy, phù hợp để so sánh các bộ siêu tham số.

### 5.3. Nhận xét

- Mô hình lai giải quyết tốt cả hai ngữ cảnh: cá nhân hóa theo user và gợi ý phim tương tự theo nội dung.
- SVD/MF cho chất lượng dự đoán tốt khi user đã có lịch sử.
- Content-based giúp cải thiện trải nghiệm tại trang chi tiết phim và hỗ trợ trường hợp dữ liệu user còn hạn chế.

## 6. Giới thiệu ứng dụng demo: sơ lược kiến trúc

Kiến trúc demo theo luồng 3 dịch vụ:

- Frontend (Next.js): hiển thị UI, gọi API backend.
- Backend (Spring Boot): xác thực JWT, xử lý nghiệp vụ, điều phối dữ liệu.
- AI Service (FastAPI): tải model đã train, trả danh sách movieId đề xuất.

Luồng nghiệp vụ gợi ý:

1. Người dùng đăng nhập và tương tác trên frontend.
2. Frontend gọi backend để lấy danh sách đề xuất.
3. Backend gọi AI service (recommendations/similar).
4. AI service trả về danh sách movieId.
5. Backend ghép metadata phim và trả kết quả hoàn chỉnh cho frontend.

## 7. Demo kết quả thực tế

### 7.1. Các endpoint AI đã triển khai

- GET /recommendations/{user_id}: gợi ý cá nhân hóa.
- GET /similar/{movie_id}: gợi ý phim tương tự theo nội dung.
- GET /: kiểm tra trạng thái model đang nạp (SVD/MF/content-based).

### 7.2. Kịch bản demo đề xuất

1. Khởi chạy backend, frontend, ai-service.
2. Đăng nhập tài khoản đã có rating history.
3. Mở trang Home để xem danh sách Recommended for You.
4. Chọn một phim bất kỳ, vào trang chi tiết.
5. Quan sát khối More Like This (kết quả content-based).
6. So sánh sự khác nhau giữa user mới và user có lịch sử đánh giá.

### 7.3. Kết luận demo

- Hệ thống trả về gợi ý theo thời gian phản hồi phù hợp cho web app học thuật.
- Kiến trúc tách AI service giúp dễ nâng cấp mô hình (đổi SVD sang MF/NCF) mà ít ảnh hưởng backend/frontend.
- Kết quả cho thấy hướng hybrid là phù hợp với bài toán gợi ý phim trong phạm vi dự án CT255H.

## 8. Hạn chế và hướng phát triển

Hạn chế hiện tại:

- Chưa đánh giá online bằng A/B test hoặc chỉ số tương tác thực người dùng.
- Chất lượng phụ thuộc dữ liệu rating và độ phủ movie features.
- Một số cấu hình train đang cân bằng theo thời gian chạy hơn là tối ưu tuyệt đối.

Hướng phát triển:

- Thử Neural Collaborative Filtering hoặc Two-Tower retrieval.
- Bổ sung ranking stage sau candidate generation.
- Tự động hóa pipeline train/evaluate/deploy theo lịch.
- Bổ sung dashboard theo dõi drift mô hình và hiệu năng dự đoán theo thời gian.

---

Tài liệu này tập trung cho phần mô hình và huấn luyện, có thể dùng trực tiếp làm nền cho báo cáo môn học hoặc slide demo kỹ thuật.
