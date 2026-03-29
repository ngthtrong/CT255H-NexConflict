# /techlead-review [TASK-ID]

## Mô tả
Agent Tech Lead chạy review checklist đầy đủ trên PR của task: code quality, testing, performance, security, architecture. Kết quả là APPROVED, APPROVED WITH CONDITIONS, hoặc CHANGES REQUESTED.

## Cú pháp
```
/techlead-review TASK-00002
```

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead (`agents/techlead.md`)

### Bước 1: Tìm PR
```bash
# Tìm branch feature/TASK-{ID}-*
BRANCH=$(git branch -a | grep "feature/TASK-{ID}" | head -1 | xargs)
# Hoặc dùng gh CLI để tìm PR
gh pr list --head "feature/TASK-{ID}" --json number,url
```

### Bước 2: Checkout và Diff
```bash
git fetch origin
git diff develop...$BRANCH
```

### Bước 3: Chạy Review Checklist

```markdown
## PR Review Checklist — TASK-{ID}

### ✅ Code Quality
- [ ] Code tuân theo conventions (linting pass)
- [ ] Không có dead code / commented-out code
- [ ] Không có magic numbers/strings
- [ ] Error handling đầy đủ
- [ ] Logging hợp lý

### ✅ Testing
- [ ] Unit test coverage ≥ 80%
- [ ] Edge cases được cover
- [ ] Test names mô tả đúng behavior
- [ ] Không có `.skip()` / `.only()` không lý do

### ✅ Performance & Database
- [ ] Không có N+1 queries
- [ ] Các cột WHERE/JOIN đã có index
- [ ] Query có LIMIT
- [ ] Không có full table scan

### ✅ Security
- [ ] Không có credentials trong code
- [ ] Input validation đầy đủ
- [ ] SQL dùng parameterized statements
- [ ] Không expose sensitive data

### ✅ Architecture
- [ ] Code nằm đúng layer
- [ ] Không có circular dependency
- [ ] Contract changes có versioning
```

### Bước 4: Viết Review

Phân loại mỗi issue:
- 🚫 **BLOCKER** — phải sửa trước merge
- ⚠️ **IMPORTANT** — cần sửa, có thể defer nếu có plan
- 💡 **SUGGESTION** — optional improvement
- 📝 **NOTE** — FYI cho team

### Bước 5: Kết luận

**APPROVED**: Không có BLOCKER, tất cả IMPORTANT đã xử lý
**APPROVED WITH CONDITIONS**: Có IMPORTANT, Developer cam kết xử lý
**CHANGES REQUESTED**: Có BLOCKER, cần sửa và re-review

### Bước 6: Ghi Review Report
Tạo `.github-copilot/workspace/reviews/REVIEW-TASK-{ID}.md`:

```markdown
# Tech Lead Review — TASK-{ID}

**Ngày**: {date}
**Reviewer**: Agent Tech Lead
**Branch**: {branch}
**Verdict**: {APPROVED / APPROVED WITH CONDITIONS / CHANGES REQUESTED}

## Checklist Summary
- Code Quality: {✅ / ⚠️}
- Testing: {✅ / ⚠️}
- Performance: {✅ / ⚠️}
- Security: {✅ / ⚠️}
- Architecture: {✅ / ⚠️}

## Issues Found
### 🚫 BLOCKER
{none / list}

### ⚠️ IMPORTANT
{none / list}

### 💡 SUGGESTION
{none / list}

## Conditions (nếu APPROVED WITH CONDITIONS)
- {condition 1}
- {condition 2}
```

## Output
```
📝 Review Complete — TASK-{ID}

Verdict: {APPROVED / APPROVED WITH CONDITIONS / CHANGES REQUESTED}

{If APPROVED}
Bước tiếp theo:
  /merge-pr TASK-{ID}    → Merge vào develop

{If CHANGES REQUESTED}
Developer cần:
1. {fix 1}
2. {fix 2}
Sau khi sửa: chạy lại /techlead-review TASK-{ID}
```

## Human Checkpoint
Tech Lead có thể yêu cầu human review cho architectural decisions.

## Agent sử dụng
**Agent Tech Lead**
