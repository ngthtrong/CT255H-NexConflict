# PROJECT-PROFILE.md

> File này được điền tự động bởi `/detect-stack` và `/discover-codebase`, hoặc có thể điền thủ công.
> Các agent khác (Developer, Tester, Doc Sync) sẽ đọc file này để biết cách chạy tests, coverage, và smoke test.

## Stack

- **Language**: <!-- Go / TypeScript / Python / Java / ... -->
- **Framework**: <!-- Gin / Express / FastAPI / Spring Boot / ... -->
- **Database**: <!-- PostgreSQL / MongoDB / MySQL / ... -->
- **Test runner**: <!-- Jest / pytest / go test / JUnit / ... -->
- **Coverage tool**: <!-- nyc / coverage.py / go tool cover / ... -->
- **Linter**: <!-- ESLint / golangci-lint / pylint / ... -->

## Commands

```yaml
start: ""           # ví dụ: docker-compose up / npm run dev
stop: ""            # ví dụ: docker-compose down / pkill node
test: ""            # ví dụ: npm test / go test ./... / pytest
coverage: ""        # ví dụ: npm run coverage / pytest --cov
lint: ""            # ví dụ: npm run lint / golangci-lint run
health_check_url: "" # ví dụ: http://localhost:8080/health
```

## Smoke Test Scenarios (≤ 10)

<!-- Liệt kê các critical user flow cần test trên live environment -->

1. <!-- Happy path chính: ví dụ "User có thể đăng ký tài khoản mới" -->
2. <!-- Authentication: ví dụ "User có thể đăng nhập và nhận token" -->
3. <!-- Core feature 1 -->
4. <!-- Core feature 2 -->
5. <!-- Error handling quan trọng -->

## Fragile Zones Summary

| Zone | File | Risk | Lý do |
|------|------|------|-------|
| <!-- tên zone --> | <!-- đường dẫn file --> | 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW | <!-- giải thích --> |

## Tech Debt Register

| ID | Mô tả | Ảnh hưởng | Priority |
|----|-------|-----------|----------|
| TD-001 | <!-- mô tả tech debt --> | <!-- ảnh hưởng đến vùng nào --> | P1 / P2 / P3 |

## External Dependencies

- **Third-party APIs**: <!-- list các external APIs được sử dụng -->
- **Secrets management**: <!-- .env / Vault / AWS Secrets Manager -->
- **Background jobs**: <!-- cron, scheduler, queue worker -->

---
*File này được tạo bởi `/setup-project` và cập nhật bởi `/detect-stack`, `/discover-codebase`*
