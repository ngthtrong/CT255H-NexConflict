---
name: Plan Sprint
description: "Tạo task chain TDD và sprint plan từ các REQ đã được phê duyệt."
argument-hint: "REQ-00001 (optional filter)"
agent: agent-pm
tools: [read, search, edit, execute, todo]
---
Thực hiện `/plan-sprint` theo PM workflow.

Yêu cầu:
1. Xác minh branch và branch guard.
2. Tạo chuỗi TASK: unit-test -> implementation -> e2e-test.
3. Tạo sprint plan và liệt kê dependencies.
4. Báo cáo danh sách artifact đã tạo/cập nhật.
