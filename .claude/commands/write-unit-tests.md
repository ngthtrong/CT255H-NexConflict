# /write-unit-tests [TASK-ID]

## Mô tả
Agent Developer viết failing unit tests (TDD Red Phase) cho task được chỉ định. Tests phải fail trước khi có implementation.

## Cú pháp
```
/write-unit-tests TASK-00001
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Verify Task trong Git (BẮT BUỘC)
```bash
git show develop:.claude/workspace/tasks/TASK-{ID}.yaml > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ TASK-{ID}.yaml chưa được commit vào develop!"
  echo "   Chạy /plan-sprint trước để PM tạo và commit task."
  exit 1
fi
```

### Bước 2: Đọc Task và Acceptance Criteria
- Đọc `TASK-{ID}.yaml` để hiểu feature cần test
- Đọc REQ spec liên quan để lấy Given/When/Then

### Bước 3: Tạo Test Branch
```bash
git checkout develop && git pull origin develop
git checkout -b test/TASK-{ID}-unit-tests
```

### Bước 4: Viết Failing Tests
Theo quy tắc trong `agents/developer.md`:
- Test name: `test_{component}_should_{behavior}_when_{condition}`
- Mỗi acceptance criteria → ít nhất 1 test
- Cover happy path + edge cases từ spec
- Test phải FAIL khi chạy (chưa có implementation)

### Bước 5: Xác nhận Tests đang đỏ
```bash
{test_command từ PROJECT-PROFILE.md}
# Output phải show: X tests FAILED
```

### Bước 6: Commit
```bash
git add .
git commit -m "test(TASK-{ID}): viết failing unit tests — {X} tests cho {feature}"
git push origin test/TASK-{ID}-unit-tests
```

## Output
```
🔴 TDD Red Phase Complete — TASK-{ID}

Tests viết: {N}
Trạng thái: Tất cả FAILING (expected)
Branch: test/TASK-{ID}-unit-tests

Bước tiếp theo:
  /implement-task TASK-{N+1}  → Developer implement để tests xanh
```

## Agent sử dụng
**Agent Developer**
