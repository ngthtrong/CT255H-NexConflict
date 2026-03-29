# /report-bug "description"

## Mô tả
Tạo bug report có cấu trúc. Agent Tester ghi chép đầy đủ thông tin tái hiện lỗi, severity, và commit vào develop để tracking.

## Cú pháp
```
/report-bug "Login button không phản hồi trên mobile"
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Lấy Bug ID tiếp theo
```bash
LAST_ID=$(ls .github-copilot/workspace/bugs/BUG-*.md 2>/dev/null | \
  sed 's/.*BUG-//' | sed 's/.md//' | sort -n | tail -1)
NEXT_ID=$(printf "%05d" $((${LAST_ID:-0} + 1)))
```

### Bước 2: Thu thập Context
```bash
BRANCH=$(git branch --show-current)
COMMIT=$(git rev-parse HEAD)
```

### Bước 3: Tạo Bug Report
Tạo `.github-copilot/workspace/bugs/BUG-{ID}.md` theo template:

```markdown
---
id: BUG-{ID}
title: "{description}"
priority: P2
status: open
reported-by: Agent Tester
reported-date: {date}
assignee: ""
related-task: ""
related-req: ""
---

# BUG-{ID}: {description}

## Mô tả
{Chi tiết mô tả bug}

## Steps to Reproduce
1. {Bước 1}
2. {Bước 2}
3. {Bước 3}

## Expected Behavior
{Mô tả behavior đúng}

## Actual Behavior
{Mô tả behavior sai}

## Environment
- **Branch**: {branch}
- **Commit**: {commit}
- **OS**: {OS}
- **Browser/Runtime**: {nếu applicable}

## Logs / Error Output
```
{error logs}
```

## Severity Assessment
- **User Impact**: {mô tả}
- **Workaround**: {có/không}
- **Data Loss Risk**: {có/không}
- **Security Risk**: {có/không}

## Triage Decision
<!-- Điền sau /triage-bug -->
```

### Bước 4: Commit Bug Report
```bash
git add .github-copilot/workspace/bugs/
git commit -m "bug: report BUG-{ID} — {short description}"
git push origin develop
```

## Output
```
🐛 Bug Reported — BUG-{ID}

Title: {description}
Priority: P2 (default, cần triage)
File: .github-copilot/workspace/bugs/BUG-{ID}.md

Bước tiếp theo:
  /triage-bug BUG-{ID}    → PM/Tech Lead đánh giá priority
```

## Human Checkpoint
Sau `/triage-bug` — PM và Tech Lead quyết định hướng xử lý.

## Agent sử dụng
**Agent Tester**
