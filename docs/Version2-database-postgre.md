# Thiết kế Cơ sở dữ liệu Web (PostgreSQL) - Version 2

Tài liệu này mô tả chi tiết sơ đồ thiết kế các bảng (Tables) cho hệ quản trị cơ sở dữ liệu PostgreSQL. Database này do Spring Boot nắm quyền quản lý, chủ yếu để lưu trữ **Dữ liệu động** phía Web.

> *Lưu ý: Các thuật toán AI của Python sẽ dựa trên **Dữ liệu tĩnh** (như `ratings.csv`, `genome-scores.csv`) load trên RAM chứ không đọc từ PostgreSQL lúc dự đoán, nhằm đảm bảo hiệu năng.*

Dưới đây là các bảng (Entities) cốt lõi thiết kế theo chuẩn ORM của Spring Boot:

## 1. Nhóm Bảng Xác thực & Người dùng (Core Web)

### Bảng `users` (Danh sách người dùng / tài khoản)
Dùng để thiết lập JWT Security và thông tin cá nhân.
- `id`: BIGINT (Primary Key, Auto Increment)
- `email`: VARCHAR (Unique, Not Null) - Tên đăng nhập.
- `password`: VARCHAR (Not Null) - Lưu trữ chuỗi đã mã hoá BCrypt.
- `full_name`: VARCHAR - Tên hiển thị người dùng (Ví dụ hiển thị: Hi, John).
- `role`: VARCHAR (Default: 'ROLE_USER') - Thêm 'ROLE_ADMIN' nếu sau này mở rộng luồng.
- `created_at`: TIMESTAMP (Default: Current Time).

## 2. Nhóm Bảng Onboarding (Xử lý Cold-Start)

### Bảng `user_preferences` (Sở thích Thể loại)
Lưu lại bước 1 của chu trình Onboarding: Khảo sát thể loại yêu thích.
- `id`: BIGINT (Primary Key, Auto Increment)
- `user_id`: BIGINT (Foreign Key trỏ đến bảng `users`)
- `genre_name`: VARCHAR - Tên thể loại (Ví dụ: "Action", "Romance", "Sci-Fi").

### Bảng `user_onboarding_ratings` (Kênh đánh giá phim mới)
Lưu lại bước 2 của chu trình Onboarding: Khảo sát mồi các phim phổ biến. (Spring Boot sẽ thu thập bảng này, sau này có thể dùng làm Data mở rộng feed thêm cho Python AI).
- `id`: BIGINT (Primary Key, Auto Increment)
- `user_id`: BIGINT (Foreign Key trỏ đến bảng `users`)
- `movie_id`: BIGINT (Mã phim BẮT BUỘC khớp chính xác với cột movieId trong lõi data cục bộ `movies.csv` của AI).
- `rating`: FLOAT - Mức điểm đánh giá (0.5 -> 5.0).
- `rated_at`: TIMESTAMP - Thời gian đánh giá.

## 3. Nhóm Bảng Cache Phim cơ bản 

### Bảng `movies` (Danh mục Phim Trích Tuyển)
Mặc dù AI giữ toàn bộ 20 triệu file CSV ở Python, nhưng để frontend truy xuất list tìm kiếm phim nhanh chóng, ta nên đổ trước data cơ bản của file `movies.csv` vào một bảng Cache SQL này.
- `id`: BIGINT (Primary Key) => ID do hệ thống MovieLens Data cung cấp, KHÔNG ĐỂ TỰ ĐỘNG SINH. Nó chính là "cầu nối" ID map giữa Web và Model AI.
- `title`: VARCHAR (Not Null) - Tên phim + Năm phát hành.
- `genres`: VARCHAR - Chuỗi phân tách bằng ký tự pipe (VD: "Action|Sci-Fi").
- `poster_url`: VARCHAR (Null) - *[Mở rộng]* Trường thiết kế thêm để phục vụ giao diện UI Web sau này nếu gọi API ngoài lấy ảnh Poster.

### Bảng `watch_history` (Lịch Sử Tương Tác)
Ghi chép lại các phim người dùng đã nhấp vào xem chi tiết để đưa vào mục "Xem lại / Watch Again".
- `id`: BIGINT (Primary Key, Auto Increment)
- `user_id`: BIGINT (Foreign Key -> bảng `users`)
- `movie_id`: BIGINT (Foreign Key -> bảng `movies` cache ID)
- `viewed_at`: TIMESTAMP - Thời điểm click mở xem.
