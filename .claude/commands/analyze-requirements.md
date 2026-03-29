# /analyze-requirements [BRIEF-ID]

## Mô tả
Agent BA đọc file brief, phân tích yêu cầu, và tạo DRAFT spec với acceptance criteria dưới dạng Given/When/Then. PO review và phê duyệt bằng cách đổi tên file.

## Cú pháp
```
/analyze-requirements BRIEF-00001
/analyze-requirements BRIEF-00002
```

## Khi nào dùng
Sau khi đã tạo file brief tại `.claude/workspace/requirements/input/BRIEF-{ID}.md`

## Quy trình thực hiện

**Agent thực hiện**: BA (`agents/ba.md`)

### Bước 1: Branch Guard
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ]; then
  git checkout develop
  echo "ℹ️ Tự động chuyển sang develop"
fi
```

### Bước 2: Xác nhận Brief tồn tại
```bash
BRIEF_FILE=".claude/workspace/requirements/input/BRIEF-{ID}.md"
if [ ! -f "$BRIEF_FILE" ]; then
  echo "❌ Không tìm thấy $BRIEF_FILE"
  echo "   Tạo brief tại đường dẫn trên trước khi chạy lệnh này."
  exit 1
fi
```

### Bước 3: BA phân tích Brief
Thực hiện đầy đủ theo `agents/ba.md`:
- Đọc brief
- Xác định Actors, Features, Constraints, Ambiguities
- Viết DRAFT-REQ-{ID}.md với Given/When/Then

### Bước 4: Commit Draft
```bash
git add .claude/workspace/requirements/DRAFT-REQ-{ID}.md
git commit -m "docs(BA): tạo DRAFT-REQ-{ID} từ BRIEF-{ID}"
git push origin develop
```

### Bước 5: Thông báo PO
```
📋 BA đã tạo DRAFT-REQ-{ID}.md

📍 Vị trí: .claude/workspace/requirements/DRAFT-REQ-{ID}.md

❓ Open Questions cần PO trả lời:
  {list open questions}

⚠️ Ambiguous items:
  {list ambiguous items}

✅ Để phê duyệt spec:
  Đổi tên file: DRAFT-REQ-{ID}.md → REQ-{ID}.md
  Sau đó chạy: /plan-sprint
```

## Human Checkpoint ⚠️
**Spec Approval**: PO phải đổi tên `DRAFT-REQ-{ID}.md` → `REQ-{ID}.md` để phê duyệt.
Không được phép chạy `/plan-sprint` khi chỉ có DRAFT file.

## Agent sử dụng
**Agent BA** (Business Analyst)
