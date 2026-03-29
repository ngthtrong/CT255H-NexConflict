# /create-pr [TASK-ID]

## Mô tả
Tạo Pull Request cho feature branch, chuẩn bị description đầy đủ với context từ task và kết quả tests/coverage.

## Cú pháp
```
/create-pr TASK-00002
```

## Điều kiện tiên quyết
- Đang ở trên branch `feature/TASK-{ID}-*`
- Tất cả tests pass
- Coverage đã được đánh giá

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Verify Branch
```bash
BRANCH=$(git branch --show-current)
if [[ ! "$BRANCH" =~ ^feature/TASK-{ID} ]]; then
  echo "❌ Phải ở trên branch feature/TASK-{ID}-* để tạo PR!"
  exit 1
fi
```

### Bước 2: Đọc Task Context
```bash
cat .github-copilot/workspace/tasks/TASK-{ID}.yaml
# Lấy: feature name, description, acceptance criteria, coverage, tech debt notes
```

### Bước 3: Chạy Final Tests
```bash
{test_command}
if [ $? -ne 0 ]; then
  echo "❌ Tests failing — không thể tạo PR!"
  exit 1
fi
```

### Bước 4: Generate PR Description

```markdown
## 🎯 Mục đích
Implement {feature} theo TASK-{ID}

## 📋 Liên kết
- Task: `.github-copilot/workspace/tasks/TASK-{ID}.yaml`
- Spec: `REQ-{ID}.md`

## ✅ Acceptance Criteria
- [x] Given {condition} When {action} Then {result}
- [x] Given {condition} When {action} Then {result}

## 🧪 Testing
- **Unit tests**: {N} passing
- **Coverage**: {X}%
- **E2E tests**: {pending / not applicable}

## 🔍 Performance Scan
- **N+1 queries**: {clean / {N} issues, see TECH-DEBT.md}
- **Missing indexes**: {none / added on {columns}}
- **Missing LIMIT**: {none / fixed}

## 📝 Tech Debt
{none / Xem TECH-DEBT.md — {summary}}

## 👀 Review Checklist (for Tech Lead)
- [ ] Code follows project conventions
- [ ] Tests cover edge cases
- [ ] No security issues
- [ ] Performance acceptable
- [ ] Documentation updated if needed
```

### Bước 5: Push và Tạo PR
```bash
git push origin $BRANCH

# Tạo PR trên GitHub (nếu có gh CLI)
gh pr create --title "feat(TASK-{ID}): {feature}" \
  --body "{PR_DESCRIPTION}" \
  --base develop \
  --head $BRANCH
```

## Output
```
🔃 Pull Request Created — TASK-{ID}

PR: #{number}
Branch: feature/TASK-{ID}-{slug} → develop
URL: {pr_url}

Bước tiếp theo:
  /techlead-review TASK-{ID}    → Request Tech Lead review
```

## Human Checkpoint
Không bắt buộc tại bước này — PR sẽ được review ở bước tiếp theo.

## Agent sử dụng
**Agent Developer**
