# /techlead-review [TASK-ID]

## Mô tả
Agent Tech Lead chạy review checklist đầy đủ trên PR của task: code quality, testing, performance, security, architecture. Kết quả là APPROVED, APPROVED WITH CONDITIONS, hoặc CHANGES REQUESTED.

## Cú pháp
```
/techlead-review TASK-00002
```

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead (`agents/techlead.md`)

### Bước 1: Xác định PR và diff
```bash
git log develop..feature/TASK-{ID}-* --oneline
git diff develop...feature/TASK-{ID}-*
```

### Bước 2: Chạy Full Review Checklist
Thực hiện đầy đủ theo `agents/techlead.md` — không được bỏ qua mục nào:

```
✅ Code Quality
✅ Testing (coverage ≥ 80%)
✅ Performance & Database (N+1, index, LIMIT)
✅ Security (no credentials, input validation, SQL injection)
✅ Architecture (layer separation, no circular deps)
✅ Documentation
```

### Bước 3: Phân loại Feedback

- 🚫 **BLOCKER** — Phải sửa trước khi merge
- ⚠️ **IMPORTANT** — Cần sửa hoặc track trong ticket
- 💡 **SUGGESTION** — Optional improvement
- 📝 **NOTE** — Ghi chú cho team

### Bước 4: Xác định kết luận

| Tình huống | Kết luận |
|-----------|---------|
| Không có BLOCKER, không có IMPORTANT | ✅ APPROVED |
| Không có BLOCKER, có IMPORTANT + cam kết track | ✅ APPROVED WITH CONDITIONS |
| Có ít nhất 1 BLOCKER | ❌ CHANGES REQUESTED |

### Bước 5: Ghi Review Report

Tạo file `.claude/workspace/reviews/REVIEW-TASK-{ID}.md`:

```markdown
# PR Review — TASK-{ID}
**Reviewer**: Tech Lead Agent
**Date**: {date}
**Kết luận**: {APPROVED / CHANGES REQUESTED}

## Checklist Results
{Kết quả từng mục}

## Feedback
### 🚫 Blockers
{list hoặc "Không có"}

### ⚠️ Important
{list hoặc "Không có"}

### 💡 Suggestions
{list hoặc "Không có"}

## NFR Assessment
- Performance: {ok / concerns}
- Security: {ok / concerns}
- Scalability: {ok / concerns}
```

### Bước 6: Thông báo
```
{APPROVED ✅ / CHANGES REQUESTED ❌} — TASK-{ID}

{Nếu APPROVED}:
  Bước tiếp theo: /merge-pr TASK-{ID}

{Nếu CHANGES REQUESTED}:
  Developer cần sửa các BLOCKER items và chạy lại /create-pr
```

## Human Checkpoint ⚠️
**ADR Review**: Nếu có quyết định kiến trúc mới trong PR này, Tech Lead đề nghị PO/team đọc ADR trước khi approve.

## Agent sử dụng
**Agent Tech Lead**
