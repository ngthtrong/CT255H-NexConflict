# Kiến trúc Hệ thống (System Architecture) - Version 2

Dự án áp dụng mô hình phân tán **Microservices cơ bản**, tách biệt rõ ràng trách nhiệm giữa Frontend, Backend Core (Nghiệp vụ), và hệ thống AI/ML. Cách tiếp cận này giúp dễ bảo trì ngôn ngữ chuyên biệt của từng mảng (NodeJS, Java, Python).

## 1. Sơ đồ Kiến trúc Cốt lõi
- **Frontend (Client):** Render UI giao tiếp qua REST API (JWT Authenticated).
- **Backend Core (Gateway / Proxy):** Quản lý trạng thái hệ thống, Data người dùng, nghiệp vụ đăng nhập và làm cầu nối Data.
- **AI Service (Worker):** Chuyên cung cấp sức mạnh tính toán ML, lấy cấu hình đầu vào và trả array dữ liệu tính toán.

## 2. Trách nhiệm của các khối Components

### A. Frontend Service (Next.js - Cổng tương tác)
- Xây dựng layout/components giao diện người dùng.
- Client-side data fetching cho các sự kiện chọn, tìm kiếm phim.
- Chỉ giao tiếp thuần túy với Java Backend, hoàn toàn ẩn hệ thống AI.

### B. Backend Core Service (Spring Boot - Trái tim hệ thống)
- **Auth & Security:** Quản trị đăng nhập, JWT creation và validation.
- **Business Core:** Lưu trữ quan hệ User - Movie (Phim yêu thích, Onboarding process). 
- **Internal Orchestrator:** Nhận yêu cầu *Gợi ý phim* từ Frontend -> Call internal API (HTTP) sang Python AI Service với thông số `user_id` hoặc `movie_id` -> Nhận List `movieId` từ AI -> Query Database lấy chi tiết (Title, Image/Poster, Rating) -> Response về Frontend.

### C. Backend AI Service (FastAPI - Khối não logic ML)
- Server khởi động sẽ load trước các mô hình đã lưu (.pkl) hoặc tính trước vector tĩnh lên RAM.
- Cung cấp ít nhất 2 API endpoint độc lập:
  1. `GET /ai-service/recommendations/{user_id}`: Request SVD engine, trả về top 10 MovieID.
  2. `GET /ai-service/similar/{movie_id}`: Request Cosine Similarity engine, trả về top 10 MovieID.

### D. Cơ sở Dữ liệu
- **RDBMS (PostgreSQL/MySQL):** Lưu dữ liệu quản trị (User Info, Accounts) và Movie Metadata.
- Dữ liệu Dataset (CSV) được load trực tiếp cho môi trường AI.
