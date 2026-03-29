# /scan-untracked

## Mô tả
Phân loại tất cả untracked files trước mỗi commit kế hoạch (planning commit). Ngăn chặn việc commit nhầm credentials, file local temp, hay các file không cần thiết.

## Khi nào dùng
- Tự động trước `/plan-sprint`
- Thủ công khi muốn kiểm tra workspace

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: List Untracked Files
```bash
git status --porcelain | grep "^??" | cut -c4-
```

### Bước 2: Categorize Files

| Category | Pattern | Action |
|----------|---------|--------|
| Agent files | `.github-copilot/*` | Auto-include |
| Gitignored | Matches `.gitignore` | Skip |
| Secrets | `*.env`, `*secret*`, `*key*` | ⚠️ NEVER commit |
| Temp | `*.tmp`, `*.log`, `*.bak` | Skip or add to .gitignore |
| Human-created | Other | Ask PO |

### Bước 3: Security Scan
```bash
# Check for potential secrets
grep -rl "API_KEY\|PASSWORD\|SECRET\|TOKEN" . --include="*.env*" 2>/dev/null
```

### Bước 4: Generate Report

```markdown
## Untracked Files Scan

### ✅ Auto-include (Agent files)
- .github-copilot/workspace/tasks/TASK-00001.yaml
- .github-copilot/workspace/sprints/SPRINT-2024-01.md

### ⏭️ Skip (Gitignored patterns)
- node_modules/
- dist/

### ⚠️ DANGER — Potential Secrets
- .env.local (contains API_KEY)

### ❓ Needs Decision (Human-created)
- scripts/seed-data.sql
- notes.txt
```

### Bước 5: Ask for Decision
```markdown
For each file in "Needs Decision":
- [ ] Include in this commit
- [ ] Commit separately
- [ ] Add to .gitignore
- [ ] Skip for now
```

### Bước 6: Execute Decisions
```bash
# Add to .gitignore if selected
echo "{file}" >> .gitignore

# Stage for commit if selected
git add {file}
```

## Output
```
📁 Untracked Files Scan

Found: {N} untracked files

Auto-include: {X}
Skip: {Y}
⚠️ Secrets detected: {Z}
Need decision: {W}

{If secrets found}
🚨 SECRETS DETECTED:
- {file}: {type of secret}
DO NOT COMMIT these files!
Add to .gitignore immediately.

{If files need decision}
Files requiring PO decision:
1. {file} — {description}
   Options: include / commit separately / gitignore / skip
```

## Human Checkpoint
**BẮT BUỘC** nếu có secrets hoặc files cần quyết định.

## Agent sử dụng
**Agent PM**
