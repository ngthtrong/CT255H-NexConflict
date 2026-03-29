# /create-skill

## Mô tả
Tạo một skill mới cho dự án, đóng gói một chuỗi workflow phức tạp thành đơn vị tái sử dụng.

## Khi nào dùng
- Cần đóng gói một quy trình lặp đi lặp lại thành skill tái sử dụng
- Muốn tạo workflow tùy chỉnh cho dự án cụ thể
- Cần mở rộng bộ skill có sẵn của Agentic Software Team

## Cú pháp
```
/create-skill <skill-name> [--description "mô tả ngắn"]
```

**Ví dụ:**
```
/create-skill data-migration --description "Quy trình migration database an toàn"
```

## Quy trình thực hiện

### Bước 1: Validate Input
```bash
# Kiểm tra skill-name hợp lệ (kebab-case, không chứa ký tự đặc biệt)
# Kiểm tra skill chưa tồn tại
if [ -d ".github-copilot/skills/$SKILL_NAME" ]; then
  echo "❌ Skill '$SKILL_NAME' đã tồn tại!"
  exit 1
fi
```

### Bước 2: Tạo Thư mục Skill
```bash
mkdir -p ".github-copilot/skills/$SKILL_NAME"
```

### Bước 3: Tạo SKILL.md từ Template
Tạo file `.github-copilot/skills/$SKILL_NAME/SKILL.md` với nội dung:

```yaml
---
name: <skill-name>
description: '<description hoặc placeholder>'
argument-hint: '<gợi ý tham số>'
user-invocable: true
---
# <Skill Name>

## When to Use
- [ ] Điền use case 1
- [ ] Điền use case 2

## Procedure
1. [ ] Điền bước 1
2. [ ] Điền bước 2
3. [ ] Điền bước 3

## Required References
- `.github-copilot/commands/relevant-command.md`
- `.github-copilot/agents/relevant-agent.md`

## Human Checkpoints
- [ ] Liệt kê các điểm cần human review (nếu có)

## Output Artifacts
- [ ] Liệt kê các file/artifact được tạo ra
```

### Bước 4: Hướng dẫn Người dùng
```
✅ Skill '$SKILL_NAME' đã được tạo!

📁 File: .github-copilot/skills/$SKILL_NAME/SKILL.md

📝 Các bước tiếp theo:
1. Mở file SKILL.md và điền nội dung cho các phần còn trống
2. Thay thế các placeholder bằng nội dung thực tế
3. Test skill bằng cách gọi tên skill trong chat

💡 Tip: Skill sẽ xuất hiện trong danh sách available_skills sau khi được định nghĩa đầy đủ.
```

### Bước 5: Commit (Tùy chọn)
```bash
# Hỏi người dùng có muốn commit ngay không
# Nếu có:
git add ".github-copilot/skills/$SKILL_NAME/"
git commit -m "feat: add skill '$SKILL_NAME'

- Tạo skill structure
- Thêm SKILL.md template

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Human Checkpoint
Không bắt buộc — người dùng có thể chọn commit ngay hoặc chỉnh sửa trước.

## Agent sử dụng
PM hoặc Tech Lead — tùy thuộc vào mục đích của skill.

## Các Skill Mẫu

### Skill cho quy trình test nâng cao
```yaml
---
name: advanced-testing
description: 'Run comprehensive test suite with coverage, mutation testing, and performance benchmarks'
argument-hint: 'test scope (unit/integration/e2e/all)'
user-invocable: true
---
```

### Skill cho deployment pipeline
```yaml
---
name: deploy-staging
description: 'Deploy to staging environment with pre-flight checks and smoke tests'
argument-hint: 'version tag or commit SHA'
user-invocable: true
---
```

## Lưu ý
- Tên skill nên dùng kebab-case (ví dụ: `my-custom-skill`)
- Mỗi skill phải có ít nhất 2 use cases và 3 bước trong procedure
- Required References phải trỏ đến các file thực sự tồn tại
- Skill có thể gọi các command khác trong procedure
