# Agentic Software Team - GitHub Copilot Runtime Instructions

Tài liệu trong `.github-copilot/` là nguồn tri thức và workflow chuẩn của team.
Các file trong `.github/` là lớp chat customization native cho GitHub Copilot Chat.

## Mục tiêu
- Giữ kỷ luật TDD-first, Git discipline, và human checkpoints.
- Dùng đúng role (BA/PM/Developer/Tech Lead/Tester/Analyst/Doc Sync) cho đúng công việc.
- Không để planning artifact chỉ tồn tại local.

## Nguồn sự thật (source of truth)
1. Persona: `.github-copilot/agents/*.md`
2. Workflow command: `.github-copilot/commands/*.md`
3. Template: `.github-copilot/templates/*`
4. Workspace artifacts: `.github-copilot/workspace/**`

Nếu có xung đột giữa custom prompt và command docs, ưu tiên command docs.

## Quy tắc branch bắt buộc
- Không push trực tiếp lên `main` hoặc `develop`.
- Development phải trên `feature/TASK-xxxxx-*` hoặc `fix/BUG-xxxxx-*`.
- Planning artifacts cần commit vào `develop` theo workflow PM.

## Cách xử lý khi user gọi slash command
Khi user nhắc đến `/command-name`, phải:
1. Đọc `.github-copilot/commands/command-name.md`
2. Đọc persona liên quan trong `.github-copilot/agents/`
3. Thực thi đúng thứ tự bước, nếu thiếu input thì hỏi tối thiểu
4. Báo cáo kết quả với đường dẫn file được tạo/cập nhật

## Human checkpoints không được bỏ qua
1. Stack review sau `/detect-stack`
2. Spec approval (DRAFT-REQ -> REQ)
3. Untracked files trước planning commit
4. ADR review trước code thay đổi kiến trúc
5. Bug P1 triage
6. Smoke test sign-off
7. Release confirmation (`YES`)

## Chat customization map
- Custom agents: `.github/agents/*.agent.md`
- File instructions: `.github/instructions/*.instructions.md`
- Prompt files: `.github/prompts/*.prompt.md`
- Skills: `.github/skills/*/SKILL.md`
- Hooks: `.github/hooks/*.json`
- MCP/plugins/settings: `.vscode/*`
