# /analyze-requirements [BRIEF-ID]

## Mô tả
Agent BA đọc file brief, phân tích yêu cầu, và tạo DRAFT spec với acceptance criteria dưới dạng Given/When/Then. PO review và phê duyệt bằng cách đổi tên file.

## Cú pháp
```
/analyze-requirements BRIEF-00001
```

## Quy trình thực hiện

**Agent thực hiện**: BA (`agents/ba.md`)

### Bước 1: Branch Guard
```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ]; then
  echo "⚠️ Đang ở nhánh main — chuyển sang develop"
  git checkout develop
fi
```

### Bước 2: Đọc Brief
```bash
BRIEF_PATH=".github-copilot/workspace/requirements/input/BRIEF-{ID}.md"
if [ ! -f "$BRIEF_PATH" ]; then
  echo "❌ Không tìm thấy brief: $BRIEF_PATH"
  exit 1
fi
```

### Bước 3: Phân tích
- Xác định **Actors** (ai thực hiện)
- Xác định **Features** (tính năng cần xây dựng)
- Xác định **Constraints** (ràng buộc)
- Đánh dấu **Ambiguities** (điểm mơ hồ)
- Ghi nhận **Out of Scope**

### Bước 4: Tạo DRAFT Spec
Tạo file `.github-copilot/workspace/requirements/DRAFT-REQ-{ID}.md` theo template trong `agents/ba.md`.

**Yêu cầu bắt buộc**:
- Mỗi yêu cầu phải có Acceptance Criteria dạng Given/When/Then
- Điểm mơ hồ đánh dấu `⚠️ AMBIGUOUS:`
- Open Questions phải rõ ràng

### Bước 5: Commit vào Develop
```bash
git add .github-copilot/workspace/requirements/
git commit -m "docs(REQ): tạo DRAFT-REQ-{ID} từ BRIEF-{ID}"
git push origin develop
```

## Output
```
📄 Đã tạo DRAFT-REQ-{ID}.md

Thống kê:
- {N} Functional Requirements
- {M} Open Questions cần PO trả lời
- {K} điểm mơ hồ đánh dấu

⚠️ Open Questions:
1. {question 1}
2. {question 2}

📝 Hướng dẫn PO:
- Trả lời Open Questions bằng cách sửa trực tiếp file
- Phê duyệt spec: đổi tên DRAFT-REQ-{ID}.md → REQ-{ID}.md
- Sau khi phê duyệt: chạy /plan-sprint
```

## Human Checkpoint
**PO phải phê duyệt** bằng cách đổi tên file từ `DRAFT-REQ-*` → `REQ-*`.

## Agent sử dụng
**Agent BA**
