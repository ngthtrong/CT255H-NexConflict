# /branch-status

## Mô tả
Hiển thị toàn bộ branches, trạng thái của chúng, và task nào đang nằm trên branch nào.

## Cú pháp
```
/branch-status
```

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: List All Branches
```bash
git fetch --all
git branch -a --format='%(refname:short)|%(upstream:short)|%(committerdate:relative)'
```

### Bước 2: Categorize Branches
```bash
# Protected branches
echo "main, develop"

# Feature branches
git branch -a | grep "feature/TASK"

# Test branches
git branch -a | grep "test/TASK"

# Fix branches
git branch -a | grep "fix/BUG"

# Stale branches (no commits > 7 days)
```

### Bước 3: Map Tasks to Branches
```bash
for task in .github-copilot/workspace/tasks/TASK-*.yaml; do
  ID=$(yq '.id' $task)
  BRANCH=$(yq '.branch' $task)
  STATUS=$(yq '.status' $task)
  echo "$ID|$BRANCH|$STATUS"
done
```

### Bước 4: Generate Report

```markdown
## Branch Status Dashboard

### Protected Branches
| Branch | Last Commit | Status |
|--------|-------------|--------|
| main | {date} | 🔒 Protected |
| develop | {date} | 🔒 Protected |

### Active Feature Branches
| Branch | Task | Status | Age | Behind develop |
|--------|------|--------|-----|----------------|
| feature/TASK-00001-auth | TASK-00001 | in-progress | 2d | 0 commits |
| feature/TASK-00002-user | TASK-00002 | pending | 1d | 3 commits |

### Stale Branches (> 7 days no activity)
| Branch | Last Activity | Action Needed |
|--------|---------------|---------------|
| feature/TASK-00099-old | 14d ago | Delete or continue |

### Branches Ready to Merge
| Branch | Task | Review Status |
|--------|------|---------------|
| feature/TASK-00003-api | TASK-00003 | approved |
```

## Output
```
🌳 Branch Status

Active: {N} branches
- Feature: {X}
- Test: {Y}
- Fix: {Z}

Stale (> 7 days): {M} branches

Ready to merge: {K} branches

{If stale branches}
⚠️ Consider running /cleanup-branches to remove merged branches
```

## Human Checkpoint
Không cần — đây là lệnh reporting.

## Agent sử dụng
**Agent PM**
