# /write-unit-tests [TASK-ID]

## Mô tả
Agent Developer viết failing unit tests (TDD Red Phase) cho task được chỉ định. Tests phải fail trước khi có implementation.

## Cú pháp
```
/write-unit-tests TASK-00001
```

## Điều kiện tiên quyết
- TASK-{ID}.yaml phải tồn tại trong git (đã được commit bởi `/plan-sprint`)

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Verify Task trong Git
```bash
git show develop:.github-copilot/workspace/tasks/TASK-{ID}.yaml > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ TASK-{ID}.yaml chưa có trong git!"
  echo "   Chạy /plan-sprint trước để tạo task."
  exit 1
fi
```

### Bước 2: Đọc Acceptance Criteria
```bash
cat .github-copilot/workspace/tasks/TASK-{ID}.yaml
# Đọc Given/When/Then từ acceptance_criteria
```

### Bước 3: Tạo Branch
```bash
git checkout develop && git pull origin develop
git checkout -b test/TASK-{ID}-unit-tests
```

### Bước 4: Viết Failing Tests

Với mỗi acceptance criterion trong task:
- Tạo test case với naming convention: `test_{component}_should_{behavior}_when_{condition}`
- Test phải FAIL khi chạy (chưa có implementation)
- Không mock business logic chính
- Cover edge cases từ spec

### Bước 5: Xác nhận Tests Đang Đỏ
```bash
# Chạy test command từ PROJECT-PROFILE.md
{test_command}
# Expect: ALL NEW TESTS FAIL
```

### Bước 6: Commit và Push
```bash
git add .
git commit -m "test(TASK-{ID}): viết failing unit tests cho {feature}

- {N} test cases từ acceptance criteria
- Tất cả tests đang fail (TDD Red Phase)
- Covers: {list behaviors}"
git push origin test/TASK-{ID}-unit-tests
```

## Output
```
🔴 TDD Red Phase Complete — TASK-{ID}

Branch: test/TASK-{ID}-unit-tests
Tests Written: {N}
Status: ALL FAILING (expected)

Test cases:
1. ❌ test_{name_1} — {description}
2. ❌ test_{name_2} — {description}

Bước tiếp theo:
  /implement-task TASK-{ID+1}    → Viết code để tests pass
```

## Human Checkpoint
Không bắt buộc — PM/Tech Lead có thể review test cases nếu cần.

## Agent sử dụng
**Agent Developer**
