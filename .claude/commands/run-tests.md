# /run-tests [TASK-ID]

## Mô tả
Agent Tester viết và chạy E2E tests dựa trên acceptance criteria của task. Đây là bước sau khi implementation đã complete.

## Cú pháp
```
/run-tests TASK-00003
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Đọc Acceptance Criteria
Lấy Given/When/Then từ REQ spec liên quan đến task.

### Bước 2: Viết E2E Test Plan
Với mỗi Given/When/Then viết 1 test scenario:
```markdown
### Scenario: {tên từ acceptance criteria}
- Given: {điều kiện}
- When: {hành động}
- Then: {kết quả mong đợi}
- Implementation: {code test}
```

### Bước 3: Chạy E2E Tests
```bash
{e2e_test_command từ PROJECT-PROFILE.md}
```

### Bước 4: Commit E2E Tests
```bash
git add tests/e2e/
git commit -m "test(TASK-{ID}): E2E tests cho {feature} — {N} scenarios"
```

### Bước 5: Báo cáo
```
🧪 E2E Tests — TASK-{ID}

Scenarios: {N}
Pass: {X} ✅
Fail: {Y} ❌

{Nếu có fail}: Chi tiết lỗi được ghi vào bug report
→ Tạo bug: /report-bug
```

## Ghi chú
- E2E tests dùng môi trường development với test data, không phải live
- Smoke test (/smoke-test) mới dùng môi trường live thực tế

## Agent sử dụng
**Agent Tester**
