# /run-tests [TASK-ID]

## Mô tả
Agent Tester viết và chạy E2E tests dựa trên acceptance criteria của task. Đây là bước sau khi implementation đã complete.

## Cú pháp
```
/run-tests TASK-00003
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Đọc Task và Acceptance Criteria
```bash
cat .github-copilot/workspace/tasks/TASK-{ID}.yaml
# Lấy acceptance_criteria với Given/When/Then
```

### Bước 2: Đọc REQ Spec liên quan
```bash
REQ_REF=$(yq '.req_ref' .github-copilot/workspace/tasks/TASK-{ID}.yaml)
cat .github-copilot/workspace/requirements/$REQ_REF.md
```

### Bước 3: Tạo E2E Test Plan
```markdown
## E2E Test Plan — TASK-{ID}

### Scenario 1: {Từ Given/When/Then}
- **Given**: {precondition}
- **When**: {action}
- **Then**: {expected result}
- **Test file**: `tests/e2e/TASK-{ID}/{scenario}.test.{ext}`

### Scenario 2: {Từ Given/When/Then}
...
```

### Bước 4: Implement E2E Tests
Viết tests theo framework trong PROJECT-PROFILE.md (Playwright, Cypress, Selenium, etc.)

### Bước 5: Chạy Tests
```bash
{e2e_test_command}
# Ghi lại kết quả PASS/FAIL cho từng scenario
```

### Bước 6: Tạo Report
```markdown
## E2E Test Report — TASK-{ID}

**Ngày**: {date}
**Tester**: Agent Tester

| # | Scenario | Result | Duration |
|---|----------|--------|----------|
| 1 | {name} | ✅ PASS / ❌ FAIL | {ms} |
| 2 | {name} | ✅ PASS / ❌ FAIL | {ms} |

**Tổng**: {pass}/{total} PASS
```

### Bước 7: Commit Tests
```bash
git add tests/
git commit -m "test(TASK-{ID}): add E2E tests

- {N} scenarios from acceptance criteria
- Result: {X}/{N} passing"
git push origin {current_branch}
```

## Output
```
🧪 E2E Tests Complete — TASK-{ID}

Result: {PASS / FAIL}
- Scenarios: {pass}/{total}
- Duration: {total_time}

{If PASS}
Bước tiếp theo:
  /create-pr TASK-{ID}    → Tạo PR

{If FAIL}
❌ Failing scenarios:
1. {scenario}: {error}
2. {scenario}: {error}

Developer cần fix implementation trước khi tiếp tục.
```

## Human Checkpoint
Không bắt buộc — automated testing.

## Agent sử dụng
**Agent Tester**
