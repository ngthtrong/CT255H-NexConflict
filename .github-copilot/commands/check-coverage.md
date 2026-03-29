# /check-coverage [TASK-ID]

## Mô tả
Chạy test coverage report và kiểm tra xem có đạt ngưỡng 80% không. Hiển thị breakdown chi tiết các file chưa được cover tốt.

## Cú pháp
```
/check-coverage TASK-00002
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Đọc Coverage Command từ PROJECT-PROFILE
```bash
COVERAGE_CMD=$(yq '.Commands.coverage' .github-copilot/PROJECT-PROFILE.md)
```

### Bước 2: Chạy Coverage Report
```bash
$COVERAGE_CMD
# Output: coverage report
```

### Bước 3: Parse Results
```bash
# Ví dụ cho Jest:
# Statements: 85.23%, Branches: 78.45%, Functions: 90.12%, Lines: 84.67%

# Ví dụ cho Go:
# coverage: 82.3% of statements
```

### Bước 4: Identify Uncovered Files
```bash
# Liệt kê files có coverage < 50%
# Liệt kê files mới trong task này
```

### Bước 5: Generate Report

```markdown
## Coverage Report — TASK-{ID}

**Gate**: 80%
**Current**: {X}%
**Status**: {✅ PASS / ❌ FAIL}

### Summary
| Metric | Value | Gate |
|--------|-------|------|
| Statements | {X}% | 80% |
| Branches | {Y}% | 80% |
| Functions | {Z}% | 80% |
| Lines | {W}% | 80% |

### Files Changed in This Task
| File | Coverage | Status |
|------|----------|--------|
| {file1} | {X}% | ✅ / ⚠️ / ❌ |
| {file2} | {Y}% | ✅ / ⚠️ / ❌ |

### Uncovered Lines (Top 10)
{List các lines chưa được cover}
```

### Bước 6: Update Task YAML
```bash
yq -i '.coverage_pct = {X}' .github-copilot/workspace/tasks/TASK-{ID}.yaml
```

## Output
```
📊 Coverage Report — TASK-{ID}

Overall: {X}% {✅ PASS / ❌ FAIL} (Gate: 80%)

{If PASS}
✅ Coverage gate passed!
Bước tiếp theo:
  /create-pr TASK-{ID}

{If FAIL}
❌ Coverage below 80%

Uncovered areas:
1. {file}:{line} — {function/branch}
2. {file}:{line} — {function/branch}

Actions:
- Thêm tests cho các areas trên, hoặc
- Ghi Tech Debt note với lý do cụ thể
```

## Human Checkpoint
Không bắt buộc — nhưng Tech Lead có thể review nếu coverage thấp.

## Agent sử dụng
**Agent Developer**
