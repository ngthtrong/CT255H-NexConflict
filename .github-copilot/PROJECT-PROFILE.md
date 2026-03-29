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

> **Tổng số**: 17 zones (6 HIGH, 6 MEDIUM, 5 LOW)  
> **Chi tiết đầy đủ**: [04-fragile-zones.md](workspace/analysis/04-fragile-zones.md)

| Zone ID | File/Area | Risk | Lý do | Effort |
|---------|-----------|------|-------|--------|
| **FZ-H01** | backend/security/* (duplicate classes) | 🔴 HIGH | Duplicate JWT security classes causing confusion | 2h |
| **FZ-H02** | backend/application.properties (line 24) | 🔴 HIGH | Hardcoded JWT secret in properties file | 1h |
| **FZ-H03** | backend/application.properties (line 40) | 🔴 HIGH | Hardcoded TMDB API key exposed | 30m |
| **FZ-H04** | backend/application.properties | 🔴 HIGH | No database connection pooling configured | 1h |
| **FZ-H05** | backend/RecommendationService.java | 🔴 HIGH | AI service single point of failure (no circuit breaker) | 4h |
| **FZ-H06** | backend/OnboardingController.java | 🔴 HIGH | Missing rating validation (accepts out-of-range values) | 1h |
| **FZ-M01** | ai-service/main.py (lines 100-350) | 🟡 MEDIUM | God function with 250+ lines of logic | 3h |
| **FZ-M02** | ai-service/train.py (single file) | 🟡 MEDIUM | No modularization of training logic | 6h |
| **FZ-M03** | backend/ (no migrations folder) | 🟡 MEDIUM | No database migration tooling (Flyway/Liquibase) | 4h |
| **FZ-M04** | backend/GenreRepository.java | 🟡 MEDIUM | N+1 query pattern on genre tags | 2h |
| **FZ-M05** | backend/RecommendationService.java | 🟡 MEDIUM | No RestTemplate timeout configuration | 30m |
| **FZ-M06** | frontend/app/onboarding/page.tsx | 🟡 MEDIUM | Onboarding ratings not integrated with backend | 2h |

**Total Remediation Effort**: 27 hours (HIGH priority only: 9.5h)

## Tech Debt Register

> **Chi tiết đầy đủ**: [00-SUMMARY.md](workspace/analysis/00-SUMMARY.md)

| ID | Mô tả | Ảnh hưởng | Priority | Effort |
|----|-------|-----------|----------|--------|
| **TD-001** | Hardcoded JWT secret & TMDB API key | Security vulnerability, potential breach | P1 | 1.5h |
| **TD-002** | Test coverage only 2% (1 smoke test) | High regression risk on changes | P1 | 26h |
| **TD-003** | Duplicate JWT security classes | Code maintenance confusion | P1 | 2h |
| **TD-004** | No database migrations (Flyway/Liquibase) | Schema changes require manual SQL | P2 | 4h |
| **TD-005** | AI service has no circuit breaker | Backend fails when AI service is down | P2 | 4h |
| **TD-006** | No API documentation (Swagger/OpenAPI) | Developer onboarding difficulty | P2 | 3h |
| **TD-007** | Missing input validation (ratings, genres) | Data integrity issues | P2 | 2h |
| **TD-008** | No connection pooling configured | Performance degradation under load | P2 | 1h |
| **TD-009** | God function in AI service (250+ lines) | Hard to test and maintain | P3 | 3h |
| **TD-010** | No logging framework (only System.out) | Production debugging difficulty | P3 | 2h |
| **TD-011** | Frontend has no error boundaries | Poor UX on component errors | P3 | 2h |
| **TD-012** | No caching for recommendations | Repeated AI calls for same request | P3 | 4h |

**Total Tech Debt**: 54.5 hours remediation effort  
**P1 Critical**: 29.5 hours  
**P2 Important**: 14 hours  
**P3 Nice-to-have**: 11 hours

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
