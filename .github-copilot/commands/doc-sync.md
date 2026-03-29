# /doc-sync

## Mô tả
Chạy Doc Sync Agent để phát hiện drift giữa tài liệu và code, cập nhật analysis documents. Nên chạy sau mỗi sprint hoặc sau mỗi PR được merge.

## Khi nào dùng
- Sau `/merge-pr` (tự động được trigger)
- Sau mỗi sprint kết thúc

## Quy trình thực hiện

**Agent thực hiện**: Doc Sync (`agents/docsync.md`)

### Bước 1: Xác định Phạm vi Thay đổi
```bash
LAST_SYNC=$(cat .github-copilot/workspace/.last-sync-date 2>/dev/null || echo "1970-01-01")
git log --oneline --since="$LAST_SYNC" --name-only | head -100
```

### Bước 2: Check Each Analysis Document

| Document | Check |
|----------|-------|
| 01-stack.md | Package versions changed? |
| 02-module-map.md | New imports/modules? |
| 06-api-surface.md | Endpoints changed? |
| PROJECT-PROFILE.md | Commands still work? |

### Bước 3: Create Drift Report
```markdown
# Documentation Drift Report — {date}

## Drift Found

### 🔴 HIGH — Needs immediate update
| Document | Item | Current Value | Note |
|----------|------|---------------|------|

### 🟡 MEDIUM — Update this sprint
| Document | Item | Current Value | Note |
|----------|------|---------------|------|

### 🟢 LOW — Low priority
| Document | Item | Current Value | Note |
|----------|------|---------------|------|
```

### Bước 4: Auto-fix Safe Drifts
```bash
# Version numbers, simple path changes, etc.
```

### Bước 5: Update Last Sync Date
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > .github-copilot/workspace/.last-sync-date
```

### Bước 6: Commit Changes
```bash
git add .github-copilot/workspace/
git commit -m "docs: sync documentation — {N} drifts addressed"
git push origin develop
```

## Output
```
📄 Doc Sync Complete

Drift Report: .github-copilot/workspace/drift-{date}.md

Summary:
- HIGH: {N} (needs manual review)
- MEDIUM: {M}
- LOW: {K}
- Auto-fixed: {X}

{If HIGH drift}
⚠️ HIGH PRIORITY DRIFTS FOUND:
- {drift 1}
- {drift 2}
Please review and update manually.
```

## Human Checkpoint
Khuyến nghị review HIGH priority drifts.

## Agent sử dụng
**Agent Doc Sync**
