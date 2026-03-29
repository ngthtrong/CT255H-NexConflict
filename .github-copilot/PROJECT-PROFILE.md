# PROJECT-PROFILE.md

> File này được điền tự động bởi `/detect-stack` và `/discover-codebase`, hoặc có thể điền thủ công.
> Các agent khác (Developer, Tester, Doc Sync) sẽ đọc file này để biết cách chạy tests, coverage, và smoke test.

## Stack

> **Architecture**: Microservices (Frontend + Backend + AI Service)

### Frontend (Next.js)
- **Language**: TypeScript
- **Framework**: Next.js 16.1.7 + React 19.2.3
- **Test runner**: ❌ Not configured (recommend Jest/Vitest)
- **Coverage tool**: ❌ Not configured
- **Linter**: ESLint 9 (eslint-config-next)

### Backend (Spring Boot)
- **Language**: Java 21
- **Framework**: Spring Boot 3.4.4
- **Database**: PostgreSQL 16 (+ H2 for testing)
- **Test runner**: JUnit (Spring Boot Test)
- **Coverage tool**: Maven JaCoCo (recommended)
- **Linter**: ❌ Not configured (recommend Checkstyle)

### AI Service (FastAPI)
- **Language**: Python 3.x
- **Framework**: FastAPI 0.109.1 + Uvicorn 0.27.0
- **ML**: scikit-surprise, scikit-learn, pandas, numpy
- **Test runner**: ❌ Not configured (recommend pytest)
- **Coverage tool**: ❌ Not configured (recommend pytest-cov)
- **Linter**: ❌ Not configured (recommend Black/Ruff)

## Commands

### Full Stack (Docker Compose)
```yaml
start: "docker-compose up -d"
stop: "docker-compose down"
test: "(run per-service tests below)"
health_check_url: "http://localhost:3000"  # Frontend
```

### Frontend (./frontend)
```yaml
start: "cd frontend && npm run dev"
build: "cd frontend && npm run build"
test: "(not configured - TODO: add Jest/Vitest)"
lint: "cd frontend && npm run lint"
health_check_url: "http://localhost:3000"
```

### Backend (./backend)
```yaml
start: "cd backend && ./mvnw spring-boot:run"
stop: "Stop-Process -Id <PID>"  # Use specific PID
test: "cd backend && ./mvnw test"
coverage: "cd backend && ./mvnw test jacoco:report"
lint: "(not configured - TODO: add Checkstyle)"
health_check_url: "http://localhost:8080/actuator/health"
```

### AI Service (./ai-service)
```yaml
start: "cd ai-service && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
stop: "Stop-Process -Id <PID>"  # Use specific PID
test: "(not configured - TODO: add pytest)"
lint: "(not configured - TODO: add Black/Ruff)"
health_check_url: "http://localhost:8000/docs"
```

## Smoke Test Scenarios (≤ 10)

> **Dựa trên MovieLens Recommendation System**

1. **User Registration**: User có thể đăng ký tài khoản mới thành công
2. **User Authentication**: User có thể đăng nhập và nhận JWT token
3. **Movie Recommendation (KNN)**: User có thể nhận gợi ý phim bằng Item-based KNN
4. **Movie Recommendation (SVD)**: User có thể nhận gợi ý phim bằng SVD (Matrix Factorization)
5. **Movie Recommendation (Hybrid)**: User có thể nhận gợi ý phim bằng Hybrid algorithm
6. **Database Connection**: Backend kết nối thành công với PostgreSQL
7. **AI Service Health**: AI Service trả về 200 OK tại /docs endpoint
8. **CORS Configuration**: Frontend có thể gọi API Backend/AI Service thành công
9. **Model Loading**: AI Service load model (KNN/SVD) thành công khi khởi động
10. **Error Handling**: System trả về error message rõ ràng khi input invalid

## Fragile Zones Summary

| Zone | File | Risk | Lý do |
|------|------|------|-------|
| <!-- tên zone --> | <!-- đường dẫn file --> | 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW | <!-- giải thích --> |

## Tech Debt Register

| ID | Mô tả | Ảnh hưởng | Priority |
|----|-------|-----------|----------|
| TD-001 | <!-- mô tả tech debt --> | <!-- ảnh hưởng đến vùng nào --> | P1 / P2 / P3 |

## External Dependencies

- **Database**: PostgreSQL 16 (Docker container)
- **Dataset**: MovieLens 20M (external download required)
- **ML Libraries**: scikit-surprise, scikit-learn
- **Third-party APIs**: None detected
- **External Services**: None detected (fully self-hosted)
- **Secrets management**: <!-- .env / Vault / AWS Secrets Manager -->
- **Background jobs**: <!-- cron, scheduler, queue worker -->

---
*File này được tạo bởi `/setup-project` và cập nhật bởi `/detect-stack`, `/discover-codebase`*
