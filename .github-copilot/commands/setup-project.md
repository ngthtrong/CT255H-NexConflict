# /setup-project

## Mô tả
Khởi tạo hệ thống Agentic Software Team cho một dự án mới (greenfield). Tạo cấu trúc workspace, thiết lập git branching strategy, và commit hệ thống vào `develop`.

## Khi nào dùng
- Bắt đầu dự án hoàn toàn mới
- Thêm hệ thống agent vào repo hiện có chưa có `.github-copilot/`

## Quy trình thực hiện

### Bước 1: Kiểm tra Git Repository
```bash
git status > /dev/null 2>&1 || git init
git log --oneline -1 > /dev/null 2>&1 || git commit --allow-empty -m "chore: initial commit"
```

### Bước 2: Thiết lập Branch Strategy
```bash
# Tạo develop nếu chưa có
git checkout -b develop 2>/dev/null || git checkout develop

# Tạo .gitignore nếu chưa có
if [ ! -f .gitignore ]; then
  cat > .gitignore << 'EOF'
node_modules/
*.env
*.env.local
.DS_Store
dist/
build/
*.log
EOF
fi
```

### Bước 3: Tạo Workspace Structure
Tạo các thư mục và placeholder files:
```
.github-copilot/workspace/requirements/input/.gitkeep
.github-copilot/workspace/tasks/.gitkeep
.github-copilot/workspace/sprints/.gitkeep
.github-copilot/workspace/bugs/.gitkeep
.github-copilot/workspace/analysis/.gitkeep
.github-copilot/skills/.gitkeep
```

### Bước 4: Tạo PROJECT-PROFILE.md Sơ khai
Tạo `.github-copilot/PROJECT-PROFILE.md` với template trống để người dùng và `/detect-stack` điền vào.

### Bước 5: Commit Hệ thống
```bash
git add .github-copilot/ .gitignore
git commit -m "chore: setup Agentic Software Team v1.0

- Thêm agent definitions (BA, PM, Tech Lead, Developer, Tester, Analyst, DocSync)
- Thêm slash commands
- Thiết lập workspace structure
- Thiết lập branch strategy (main/develop/feature)"
git push origin develop 2>/dev/null || echo "Remote chưa được cấu hình — commit local OK"
```

### Bước 6: Báo cáo và Hướng dẫn tiếp theo
```
✅ Agentic Software Team đã được cài đặt!

Bước tiếp theo:
1. Chạy /detect-stack để phát hiện công nghệ dự án
2. Chạy /discover-codebase nếu đây là dự án hiện có
3. Tạo brief tại .github-copilot/workspace/requirements/input/BRIEF-00001.md
4. Chạy /analyze-requirements BRIEF-00001
```

## Human Checkpoint
Không cần — đây là lệnh setup tự động hoàn toàn.

## Agent sử dụng
Lệnh tổng quát — tất cả agents đều tham gia trong setup.
