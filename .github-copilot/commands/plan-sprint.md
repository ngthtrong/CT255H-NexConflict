# /plan-sprint

## Mô tả
Agent PM đọc tất cả REQ đã được phê duyệt, phân rã thành chuỗi task TDD (unit-test → implementation → e2e-test), và commit vào `develop` trước khi bất kỳ code nào được viết.

## Cú pháp
```
/plan-sprint
```

## Điều kiện tiên quyết
- Có ít nhất 1 file `REQ-*.md` (không phải `DRAFT-REQ-*`) trong `.github-copilot/workspace/requirements/`

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: Branch Guard
```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ]; then
  git checkout develop
fi
```

### Bước 2: Kiểm tra REQ đã phê duyệt
```bash
REQ_FILES=$(ls .github-copilot/workspace/requirements/REQ-*.md 2>/dev/null | grep -v DRAFT)
if [ -z "$REQ_FILES" ]; then
  echo "❌ Không có REQ nào được phê duyệt!"
  echo "   Hãy đổi tên DRAFT-REQ-*.md → REQ-*.md để phê duyệt"
  exit 1
fi
```

### Bước 3: Lấy Task ID tiếp theo
```bash
LAST_ID=$(ls .github-copilot/workspace/tasks/TASK-*.yaml 2>/dev/null | \
  sed 's/.*TASK-//' | sed 's/.yaml//' | sort -n | tail -1)
NEXT_ID=$((${LAST_ID:-0} + 1))
```

### Bước 4: Tạo chuỗi 3 Task cho mỗi Feature

Với mỗi Functional Requirement trong mỗi REQ file:

| Task | Type | Mục đích |
|------|------|----------|
| TASK-{N} | unit-test | Viết failing tests (TDD Red) |
| TASK-{N+1} | implementation | Implement cho tests pass (TDD Green) |
| TASK-{N+2} | e2e-test | Viết E2E tests từ acceptance criteria |

### Bước 5: Tạo Sprint Plan
Tạo `.github-copilot/workspace/sprints/SPRINT-{date}.md` với danh sách task và dependencies.

### Bước 6: Commit Planning Artifacts
```bash
git add .github-copilot/workspace/tasks/ .github-copilot/workspace/sprints/
git commit -m "plan: sprint {date} — {N} tasks từ {REQ-IDs}"
git push origin develop
```

## Output
```
📋 Sprint Plan đã được tạo!

Tasks:
| ID | Type | Feature | Depends On |
|----|------|---------|------------|
| TASK-00001 | unit-test | {feature} | — |
| TASK-00002 | implementation | {feature} | TASK-00001 |
| TASK-00003 | e2e-test | {feature} | TASK-00002 |

Bước tiếp theo:
  /write-unit-tests TASK-00001    → Bắt đầu TDD Red Phase
```

## Human Checkpoint
Không bắt buộc — nhưng PO có thể review Sprint Plan trước khi team bắt đầu.

## Agent sử dụng
**Agent PM**
