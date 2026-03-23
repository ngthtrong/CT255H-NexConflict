# Chi tiết Vận hành và Stack Công nghệ (Tech Stack) - Version 2

Mô hình 3 lớp phân tách yêu cầu hệ sinh thái công nghệ rõ ràng để phối hợp nhịp nhàng, tối đa hoá hiệu suất từng phần việc.

## 1. Lớp Tương Tác - Frontend (FE)
*   **Công nghệ lõi:** Next.js (Dựa trên React 18).
*   **Giao diện/Design:** Tailwind CSS.
*   **Mục đích chọn lựa:** 
    *   Next.js cho phép Routing nhẹ nhàng.
    *   Việc làm trang Gợi ý phim thường đòi hỏi hiển thị nhiều Thumbnail kết hợp với Client-side render, Next.js kiểm soát hydration state cực tốt. Cung cấp UX mượt mà qua Skeleton Loaders cho các API AI đang tính toán.

## 2. Trái tim Web - Backend REST API (BE)
*   **Công nghệ lõi:** Java (JDK 17 hoặc 21), Framework **Spring Boot 3.x**.
*   **Database Tooling:** Spring Data JPA / Hibernate.
*   **Security:** Spring Security cấu hình bảo vệ Stateless kèm thư viện JWT (`io.jsonwebtoken`).
*   **Mục đích chọn lựa:** 
    *   Sự ổn định và logic vững vàng của Java Spring phù hợp cho việc phân tải xử lý Authentication (Đăng ký/Đăng nhập), điều phối Data từ PostgreSQL.

## 3. Khối Não Phân Tích - AI Service
*   **Công nghệ Khung:** Python 3.9+ với **FastAPI**.
*   **Máy chủ ASGI:** Uvicorn.
*   **Data/ML Libs:** `pandas`, `numpy`, `scikit-learn`, `scikit-surprise`.
*   **Mục đích chọn lựa:** FastAPI được thiết kế dựa trên Asynchronous, cực nhẹ và cực nhanh. Tốc độ route của nó đủ sức đáp ứng request liên tục từ Spring Boot Gateway gọi sang khi cần ML List Movies, đồng thời tự động xuất docs API (Swagger UI).

## 4. Hệ CSDL và Cơ chế lưu trữ 
*   **RDBMS Core Database:** PostgreSQL (Hoặc MySQL) chuyên lưu trữ dữ liệu Web (Bảng `User`, Bảng `Onboarding_Pref`, Bảng ánh xạ `Movie_Meta`).
*   **In-Memory Models (RAM):** Backend AI Python không dùng DB truyền thống cho lúc gợi ý mà sẽ load các tệp `.pkl` (Pickle models) và ma trận CSV lên thẳng RAM bằng Pandas lúc khởi động Web server.

## 5. Deployment / Local Runtime Flow
Khi chạy Local dev, quy trình khởi động yêu cầu mở 3 Terminals:
1. `npm run dev` (Frontend port: 3000)
2. `./mvnw spring-boot:run` (Backend core port: 8080)
3. `uvicorn main:app --reload --port 8000` (FastAPI AI port: 8000)
