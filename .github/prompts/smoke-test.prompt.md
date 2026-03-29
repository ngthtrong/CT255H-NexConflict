---
name: Smoke Test
description: "Chạy smoke-test trên live environment và tạo report cho PO sign-off."
argument-hint: "v1.0.0"
agent: agent-tester
tools: [read, search, edit, execute]
---
Thực hiện `/smoke-test` cho version được truyền vào.

Yêu cầu:
1. Đọc PROJECT-PROFILE trước khi chạy.
2. Record commit hash va cross-check release readiness.
3. Tạo report với bảng kết quả PASS/FAIL.
4. Nhắc PO sign-off trước release.
