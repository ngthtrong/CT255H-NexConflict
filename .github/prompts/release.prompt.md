---
name: Release
description: "Thực hiện release gate theo workflow và xác nhận sign-off/checkpoints."
argument-hint: "v1.0.0"
agent: agent-orchestrator
tools: [read, search, execute, todo, agent]
---
Thực hiện `/release` cho version được truyền vào.

Yêu cầu:
1. Verify smoke sign-off và commit hash cross-check.
2. Verify tất cả human checkpoints đã đạt.
3. Nếu thiếu điều kiện, dừng lại và nêu rõ blocker.
4. Chỉ cho phép tiếp tục khi có xác nhận `YES`.
