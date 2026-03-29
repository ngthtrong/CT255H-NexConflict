# /check-coverage [TASK-ID]

## Mô tả
Chạy test coverage report và kiểm tra xem có đạt ngưỡng 80% không. Hiển thị breakdown chi tiết các file chưa được cover tốt.

## Cú pháp
```
/check-coverage TASK-00002
/check-coverage        ← Kiểm tra toàn bộ codebase
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Chạy Coverage
```bash
# Dùng command từ PROJECT-PROFILE.md
{coverage_command}
```

### Bước 2: Phân tích Kết quả
```bash
# Lấy danh sách files có coverage thấp
# (logic phụ thuộc vào tool: nyc, pytest-cov, go cover...)
```

### Bước 3: Báo cáo
```
📊 Coverage Report — {date}

Overall: {X}%  (Gate: 80% — {PASS ✅ / FAIL ❌})

Files cần chú ý (coverage < 80%):
  src/services/payment.ts   → 45%  ⚠️
  src/utils/validator.go    → 62%  ⚠️

Files tốt:
  src/handlers/user.ts      → 91%  ✅
  src/models/order.go       → 88%  ✅

Hành động khuyến nghị:
  - Thêm test cho payment.ts: error handling branches chưa được cover
  - Thêm test cho validator.go: edge cases với invalid input
```

## Agent sử dụng
**Agent Developer**
