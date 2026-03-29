---
name: Implement Task
description: "Implement TASK-xxxxx theo TDD, coverage gate, và performance scan."
argument-hint: "TASK-00002"
agent: agent-developer
tools: [read, search, edit, execute, todo]
---
Thực hiện workflow `/implement-task` cho TASK ID được truyền vào.

Yêu cầu:
1. Verify TASK yaml đã có trong git.
2. Tuân thủ branch policy và TDD cycle.
3. Chạy test + coverage gate + performance scan.
4. Báo cáo kết quả và technical debt (nếu có).
