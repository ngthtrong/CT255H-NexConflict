# /triage-bug [BUG-ID]

## Mô tả
PM và Tech Lead cùng đánh giá bug, xác định priority thực sự, và quyết định hướng xử lý — hotfix ngay hay schedule vào sprint tiếp theo.

## Cú pháp
```
/triage-bug BUG-00001
```

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`) + Tech Lead (`agents/techlead.md`)

### Bước 1: Đọc Bug Report
```bash
cat .github-copilot/workspace/bugs/BUG-{ID}.md
```

### Bước 2: Đánh giá Severity

| Factor | P1 (Critical) | P2 (Important) | P3 (Minor) |
|--------|---------------|----------------|------------|
| User Impact | Tất cả users bị block | Nhiều users bị ảnh hưởng | Ít users, có workaround |
| Data Loss | Có | Không | Không |
| Security | Có | Không | Không |
| Workaround | Không | Có nhưng khó | Có và dễ |

### Bước 3: Quyết định Action

| Priority | Action |
|----------|--------|
| P1 | **HOTFIX NOW** — Dừng sprint, fix ngay |
| P2 | **NEXT SPRINT** — Schedule vào sprint tiếp |
| P3 | **BACKLOG** — Thêm vào backlog, fix khi có thời gian |

### Bước 4: Update Bug Report
```bash
# Cập nhật section Triage Decision trong bug report
yq -i '.priority = "P{X}"' # trong frontmatter
```

```markdown
## Triage Decision
- **Priority Confirmed**: P{X}
- **Action**: {hotfix now / next sprint / backlog}
- **Decision by**: PM + Tech Lead
- **Decision date**: {date}
- **Rationale**: {lý do}
```

### Bước 5: Nếu P1 — Tạo Hotfix Task ngay
```bash
if [ "$PRIORITY" = "P1" ]; then
  # Tạo TASK-HOTFIX-{BUG-ID}.yaml
  # Set depends_on: [] (không phụ thuộc)
  # Set priority: P1
fi
```

### Bước 6: Commit Decision
```bash
git add .github-copilot/workspace/bugs/
git commit -m "triage: BUG-{ID} → P{X} — {action}"
git push origin develop
```

## Output
```
⚖️ Bug Triaged — BUG-{ID}

Priority: P{X}
Action: {hotfix now / next sprint / backlog}

{If P1}
⚠️ P1 BUG — HOTFIX REQUIRED
Task created: TASK-HOTFIX-{BUG-ID}
Bước tiếp theo:
  /implement-task TASK-HOTFIX-{BUG-ID}

{If P2}
📋 Scheduled for next sprint
Bug sẽ được plan trong /plan-sprint tiếp theo

{If P3}
📝 Added to backlog
Sẽ được xem xét khi có resource
```

## Human Checkpoint
**BẮT BUỘC cho P1**: PO phải confirm decision trước khi dừng sprint.

## Agent sử dụng
**Agent PM** + **Agent Tech Lead**
