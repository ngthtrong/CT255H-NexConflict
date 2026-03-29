---
description: "Use when creating or editing sprint task files, dependency chains, or task metadata for TASK-xxxxx YAML files."
applyTo: ".github-copilot/workspace/tasks/**/*.yaml"
---
# TASK YAML Instructions

- Task ID phải theo định dạng `TASK-00001` (5 digits).
- Mỗi feature nên có chuỗi: `unit-test` -> `implementation` -> `e2e-test`.
- `implementation` phải depend vào `unit-test` cùng feature.
- `e2e-test` phải depend vào `implementation`.
- Mô tả task phải action-oriented, testable, và có output artifact rõ ràng.
- Không tạo task trùng ID, không nhảy cóc sequence nếu không có lý do.
