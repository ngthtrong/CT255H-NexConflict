# /bug-status

## Mô tả
Hiển thị tổng quan trạng thái tất cả bugs đang được track — open, in-progress, fixed, verified.

## Cú pháp
```
/bug-status
```

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: Scan Bug Files
```bash
find .github-copilot/workspace/bugs -name "BUG-*.md" -exec cat {} \;
```

### Bước 2: Parse Status từ Frontmatter
```bash
for file in .github-copilot/workspace/bugs/BUG-*.md; do
  ID=$(yq -f extract '.id' $file)
  STATUS=$(yq -f extract '.status' $file)
  PRIORITY=$(yq -f extract '.priority' $file)
  echo "$ID|$STATUS|$PRIORITY"
done
```

### Bước 3: Generate Report

```markdown
## Bug Status Dashboard

**Tổng**: {total} bugs

### By Status
| Status | Count |
|--------|-------|
| 🔴 Open | {N} |
| 🟡 In Progress | {M} |
| 🟢 Fixed | {K} |
| ✅ Verified | {L} |
| ⚫ Won't Fix | {X} |

### By Priority
| Priority | Open | In Progress | Fixed |
|----------|------|-------------|-------|
| P1 | {N} | {M} | {K} |
| P2 | {N} | {M} | {K} |
| P3 | {N} | {M} | {K} |

### Active Bugs (Open + In Progress)

| ID | Title | Priority | Status | Assignee | Age |
|----|-------|----------|--------|----------|-----|
| BUG-00001 | {title} | P1 | open | {assignee} | 3d |
| BUG-00002 | {title} | P2 | in-progress | {assignee} | 1d |
```

## Output
```
🐛 Bug Status Dashboard

Summary:
- Open: {N}
- In Progress: {M}
- Fixed (awaiting verification): {K}
- Verified: {L}

{If any P1 bugs}
⚠️ P1 BUGS REQUIRING ATTENTION:
- BUG-{ID}: {title}

{If no open bugs}
✅ No open bugs! Great job team.
```

## Human Checkpoint
Không cần — đây là lệnh reporting.

## Agent sử dụng
**Agent PM**
