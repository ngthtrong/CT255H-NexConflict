---
description: "Use when running Agentic Software Team workflows, slash commands, or role-based execution (BA/PM/Developer/Tech Lead/Tester/Analyst/Doc Sync)."
---
# Agentic Workflow Instructions

- Luôn map user request vào command tương ứng trong `.github-copilot/commands/` trước khi hành động.
- Nếu user chỉ đưa TASK-ID/BRIEF-ID, phải xác minh file đầu vào tồn tại trước khi tiếp tục.
- Không bỏ qua human checkpoints được mô tả trong `copilot-instructions.md`.
- Khi tạo artifact mới, đặt đúng folder trong `.github-copilot/workspace/`.
- Khi gặp ambiguity trong requirement, đánh dấu `OPEN QUESTION` thay vì tự diễn giải.
- Khi review, ưu tiên bug/risk/regression trước style.
