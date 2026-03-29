# /plan-sprint

## Mô tả
Agent PM đọc tất cả REQ đã được phê duyệt, phân rã thành chuỗi task TDD (unit-test → implementation → e2e-test), và commit vào `develop` trước khi bất kỳ code nào được viết.

## Khi nào dùng
Sau khi PO đã phê duyệt ít nhất một spec (đổi tên DRAFT-REQ → REQ).

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: Branch Guard
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ]; then
  git checkout develop
fi
```

### Bước 2: Kiểm tra REQ đã phê duyệt
```bash
REQ_FILES=$(ls .claude/workspace/requirements/REQ-*.md 2>/dev/null)
if [ -z "$REQ_FILES" ]; then
  echo "❌ Không có REQ nào được phê duyệt."
  echo "   PO phải đổi tên DRAFT-REQ-*.md → REQ-*.md trước."
  exit 1
fi
```

### Bước 3: Kiểm tra Untracked Files trước khi commit
```bash
# Chạy scan để tránh commit nhầm
/scan-untracked
```

### Bước 4: PM tạo Task Sequence
Với mỗi Feature trong REQ, tạo 3 tasks theo `agents/pm.md`:
- **TASK-{N}**: Unit Tests (type: unit-test, depends: none)
- **TASK-{N+1}**: Implementation (type: implementation, depends: TASK-{N})
- **TASK-{N+2}**: E2E Tests (type: e2e-test, depends: TASK-{N+1})

Dùng template tại `.claude/templates/TASK-template.yaml`

### Bước 5: Tạo Sprint Plan File
Tạo `.claude/workspace/sprints/SPRINT-{YYYY-MM-DD}.md`

### Bước 6: Commit TẤT CẢ vào develop (BẮT BUỘC)
```bash
git add .claude/workspace/tasks/ .claude/workspace/sprints/
git commit -m "plan: sprint {date} — {N} tasks từ {REQ-IDs}"
git push origin develop
echo "✅ Planning artifacts đã được commit vào develop"
```

### Bước 7: Tóm tắt Sprint
```
📅 Sprint Plan — {date}

Tasks đã tạo:
  TASK-00001 [unit-test]       → Viết failing tests cho {feature}
  TASK-00002 [implementation]  → Implement {feature} (depends: TASK-00001)
  TASK-00003 [e2e-test]        → E2E tests cho {feature} (depends: TASK-00002)

Trình tự thực hiện:
  /write-unit-tests TASK-00001
  /implement-task TASK-00002
  /run-tests TASK-00003
  /create-pr TASK-00002
  /techlead-review TASK-00002
  /merge-pr TASK-00002
```

## Human Checkpoint ⚠️
Không bắt buộc dừng, nhưng PO nên review sprint plan trước khi team bắt đầu implement.

## Agent sử dụng
**Agent PM** (Project Manager)
