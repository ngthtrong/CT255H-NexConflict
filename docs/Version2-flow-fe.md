# Luồng Giao Diện (Frontend Flow) - Version 2

*(Phát triển bằng Next.js)*

Tài liệu này mô tả chi tiết luồng màn hình FE dành cho hệ thống gợi ý phim, phân tách rõ ràng giữa phân khúc Người dùng mới và Người dùng đã có lịch sử tương tác.

## 1. Đối với Người dùng mới (Khắc phục "Cold-Start Problem")

Luồng (Onboarding Flow) được thiết kế để thu thập sở thích ban đầu khi người dùng mới tạo tài khoản chưa có dữ liệu đánh giá:

* **Bước 1:** Sau khi đăng nhập/đăng ký thành công, hệ thống yêu cầu người dùng hoàn thành một **Onboarding Quiz**.
* **Bước 2 (Chọn thể loại):** Hiển thị danh sách các thể loại phim (Genres). Người dùng bắt buộc chọn 3-5 thể loại yêu thích nhất.
* **Bước 3 (Chọn phim yêu thích):** Hệ thống hiển thị một grid các "Phim phổ biến nhất" (Top Popular - xếp hạng theo số lượng rating/đánh giá). Người dùng chọn/đánh giá (chấm sao/thả tim) từ 5-10 phim họ đã xem.

=> Kết quả: Cung cấp ngay tập dữ liệu ban đầu cho hệ thống AI để cá nhân hóa Trang chủ.

## 2. Đối với Người dùng cũ (Đã có lịch sử xem/đánh giá)

Thuật toán Lọc cộng tác (Collaborative Filtering - SVD) dự đoán và hiển thị nội dung tùy chỉnh ngay trên Trang chủ khi người dùng truy cập lại ứng dụng. Cụ thể:

## 3. Danh sách các Màn hình (FE - Next.js) cốt lõi

### 3.1. Màn hình Auth (Login/Register)

* Giao diện đăng nhập, đăng ký tài khoản (JWT).

### 3.2. Màn hình Onboarding

* Hiển thị dưới dạng Cửa sổ Pop-up hoặc Wizard các bước (Step 1, Step 2).
* Cho phép chọn Thể loại -> Chọn Phim mẫu như đã mô tả ở phần 1.

### 3.3. Màn hình Trang chủ (Home Page)

* **Nếu là khách (Guest) hoặc chưa Onboarding:** Hiển thị hàng "Top Trending" (Các phim phổ biến nhất mọi thời đại).
* **Nếu đã hoàn thành Onboarding hoặc đã có đánh giá:**
  * **Hàng 1 (#Recommended For You):** "Dành riêng cho bạn" (Sử dụng model SVD/Lọc cộng tác dựa trên thông tin rating). Hệ thống tìm những phim người dùng *chưa xem* nhưng có khả năng sẽ chấm điểm cao.
  * **Hàng 2 (#Top Genres):** Các bộ phim thuộc những thể loại người dùng hay xem/đánh giá cao nhất.
  * **Hàng 3 (#Watch Again):** Các phim người dùng đã xem hoặc đánh giá.

### 3.4. Màn hình Chi tiết phim (Movie Detail)

* Hiển thị thông tin tổng quan phim: Tiêu đề, điểm trung bình, thể loại (genres), cast/crew (nếu có bổ sung).
* **Tính năng gợi ý cốt lõi bắt buộc: "Phim tương tự (More Like This)"**.
  * *Sức mạnh Data:* Sử dụng model Content-Based Filtering, tận dụng bộ `genome-scores.csv` (chấm điểm theo biểu đồ từ khóa cực sâu, ví dụ: 'dark comedy', 'space travel'). Dùng Cosine Similarity tìm các phim đạt điểm cao ở cùng cụm tag này. Đảm bảo phần phim gợi ý ra có độ tương đồng sát với bộ phim gốc theo nghĩa nội dung sâu sắc chứ không chỉ theo thể loại.

### 3.5. Màn hình Tìm kiếm (Search & Filter)

* Thanh tìm kiếm Tên phim.
* Bộ lọc (Filter) nâng cao gồm: Lọc theo đánh giá sao, thể loại, hoặc các Tag.
