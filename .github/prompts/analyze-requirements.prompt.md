---
name: Analyze Requirements
description: "Phân tích BRIEF theo BA workflow và tạo DRAFT-REQ với Given/When/Then."
argument-hint: "BRIEF-00001"
agent: agent-ba
tools: [read, search, edit]
---
Thực hiện `/analyze-requirements` cho BRIEF ID do người dùng cung cấp.

Yêu cầu:
1. Đọc `.github-copilot/commands/analyze-requirements.md` và `.github-copilot/agents/ba.md`.
2. Tạo/cập nhật file DRAFT-REQ đúng định dạng.
3. Liệt kê OPEN QUESTIONS cần PO trả lời.
4. Kết thúc bằng hướng dẫn phê duyệt DRAFT-REQ -> REQ.
