---
name: agentic-brownfield
description: 'Discover and document existing systems with 10-phase brownfield analysis and drift detection workflows.'
argument-hint: 'analysis scope (full/module/api/database)'
user-invocable: true
---
# Agentic Brownfield Skill

## When to Use
- Mới tiếp quản một codebase có sẵn.
- Cần cập nhật phân tích và drift report sau nhiều thay đổi.

## Procedure
1. Chạy discover-codebase theo thứ tự 10 giai đoạn.
2. Tạo/cập nhật tài liệu trong `.github-copilot/workspace/analysis/`.
3. Đánh dấu fragile zones với risk level.
4. Đối chiếu tài liệu hiện tại và code để tạo drift report.
5. Đề xuất ưu tiên khắc phục theo risk.

## Required References
- `.github-copilot/commands/discover-codebase.md`
- `.github-copilot/commands/doc-sync.md`
- `.github-copilot/agents/analyst.md`
- `.github-copilot/agents/docsync.md`
