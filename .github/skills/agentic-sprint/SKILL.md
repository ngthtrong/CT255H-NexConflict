---
name: agentic-sprint
description: 'Run full sprint workflow for Agentic Software Team: requirements, planning, implementation, review, testing, and release gates.'
argument-hint: 'REQ-ID/TASK-ID or sprint objective'
user-invocable: true
---
# Agentic Sprint Skill

## When to Use
- Cần một luồng sprint end-to-end từ requirement đến release.
- Cần đảm bảo team follow đúng command order và checkpoints.

## Procedure
1. Validate input và xác định phase hiện tại.
2. Chọn command tiếp theo trong `.github-copilot/commands/`.
3. Thực thi và cập nhật artifact trong `.github-copilot/workspace/`.
4. Dừng lại tại mỗi human checkpoint để xin phê duyệt.
5. Tổng hợp kết quả và next action.

## Required References
- `.github-copilot/USAGE-GUIDE.md`
- `.github-copilot/copilot-instructions.md`
- `.github-copilot/commands/*.md`
- `.github/AGENTS.md`
