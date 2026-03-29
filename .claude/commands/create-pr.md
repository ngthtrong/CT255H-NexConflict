# /create-pr [TASK-ID]

## Mô tả
Tạo Pull Request cho feature branch, chuẩn bị description đầy đủ với context từ task và kết quả tests/coverage.

## Cú pháp
```
/create-pr TASK-00002
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Xác nhận trên Feature Branch
```bash
BRANCH=$(git branch --show-current)
if [[ ! "$BRANCH" == feature/* ]]; then
  echo "❌ Cần phải đang ở feature branch để tạo PR"
  echo "   Current branch: $BRANCH"
  exit 1
fi
```

### Bước 2: Đảm bảo branch up-to-date
```bash
git fetch origin develop
git rebase origin/develop
# Resolve conflicts nếu có
```

### Bước 3: Push lần cuối
```bash
git push origin $BRANCH
```

### Bước 4: Tạo PR Description

Tạo PR với body đầy đủ:

```markdown
## 📋 TASK-{ID}: {Feature Name}

### Mô tả
{Tóm tắt những gì đã implement từ TASK YAML}

### Thay đổi
- {File/component thay đổi 1}
- {File/component thay đổi 2}

### Testing
- Unit tests: {X} tests passing
- Coverage: {Y}% (Gate: 80% — ✅/❌)
- E2E tests: {Z} scenarios

### Performance Scan
- N+1 queries: {clean ✅ / {N} fixed ✅ / {N} deferred - xem TECH-DEBT.md}
- Database indexes: {ok ✅ / added on {column} ✅}
- Query limits: {ok ✅}

### Tech Debt
{none / Xem TECH-DEBT.md — {N} items được tracked}

### Checklist Developer
- [ ] Tất cả failing tests hiện đã pass
- [ ] Coverage ≥ 80%
- [ ] Performance scan đã chạy
- [ ] Không có credential trong code
- [ ] Commit messages rõ ràng

### Liên kết
- Task: `.claude/workspace/tasks/TASK-{ID}.yaml`
- Spec: `.claude/workspace/requirements/REQ-{REQ-ID}.md`
```

### Bước 5: Tạo PR
```bash
gh pr create \
  --base develop \
  --head $BRANCH \
  --title "feat(TASK-{ID}): {feature name}" \
  --body-file /tmp/pr-body.md
# Hoặc hướng dẫn tạo PR thủ công nếu gh CLI không có
```

### Bước 6: Thông báo
```
✅ PR đã tạo — TASK-{ID}

Branch: {branch} → develop
Coverage: {Y}%

Bước tiếp theo:
  /techlead-review TASK-{ID}  → Tech Lead review PR
```

## Agent sử dụng
**Agent Developer**
