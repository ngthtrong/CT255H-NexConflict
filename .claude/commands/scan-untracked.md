# /scan-untracked

## Mô tả
Phân loại tất cả untracked files trước mỗi commit kế hoạch (planning commit). Ngăn chặn việc commit nhầm credentials, file local temp, hay các file không cần thiết.

## Khi nào dùng
- Tự động trước `/plan-sprint`
- Thủ công khi muốn kiểm tra workspace

## Quy trình thực hiện

**Agent thực hiện**: PM (tự gọi trước commit)

### Bước 1: Lấy danh sách untracked files
```bash
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -z "$UNTRACKED" ]; then
  echo "✅ Không có untracked files"
  exit 0
fi
```

### Bước 2: Phân loại từng file

```bash
echo "$UNTRACKED" | while read FILE; do
  # Category 1: Agent documents (auto-include)
  if echo "$FILE" | grep -qE "^\.claude/workspace/"; then
    echo "🤖 AGENT_DOC: $FILE → Sẽ được commit tự động"

  # Category 2: Gitignore patterns (skip)
  elif git check-ignore -q "$FILE" 2>/dev/null; then
    echo "🚫 GITIGNORED: $FILE → Bỏ qua"

  # Category 3: Potential secrets (WARN)
  elif echo "$FILE" | grep -qiE "\.env|secret|credential|api.key|password|token"; then
    echo "🔴 POTENTIAL SECRET: $FILE → ⚠️ CẢNH BÁO — Cần review thủ công!"

  # Category 4: Human files (ask)
  else
    echo "👤 HUMAN_FILE: $FILE → Hỏi PO quyết định"
  fi
done
```

### Bước 3: Quyết định cho Human Files

Với mỗi `HUMAN_FILE`, hỏi PO:
```
Tìm thấy file không thuộc agent: {filename}

Hành động:
  A) Đưa vào commit này (agent docs commit)
  B) Commit riêng lẻ
  C) Thêm vào .gitignore
  D) Tạm thời bỏ qua (git stash)
  E) Giữ untracked

Lựa chọn [A/B/C/D/E]:
```

### Bước 4: Báo cáo
```
📋 Untracked File Scan Complete

Agent docs (auto-commit): {N} files
Gitignored (skipped): {N} files
🔴 Potential secrets: {N} files — REVIEW REQUIRED
Human files (decided): {N} files
```

## Human Checkpoint ⚠️
**Potential Secrets**: Dừng lại và hỏi PO về bất kỳ file nào bị nghi ngờ là credential.

## Agent sử dụng
**Agent PM** (tự động) + tất cả agents (chuẩn bị trước planning commit)
