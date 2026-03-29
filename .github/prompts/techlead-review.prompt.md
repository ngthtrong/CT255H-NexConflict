---
name: Tech Lead Review
description: "Review TASK/PR theo checklist kỹ thuật, bảo mật, hiệu năng, NFR."
argument-hint: "TASK-00002 hoac PR context"
agent: agent-techlead
tools: [read, search, execute]
---
Thực hiện `/techlead-review` theo checklist chuẩn.

Yêu cầu:
1. Ưu tiên findings theo mức độ nghiêm trọng.
2. Phân loại BLOCKER, IMPORTANT, SUGGESTION, NOTE.
3. Nếu không có finding, phải nói rõ residual risk/testing gap.
4. Kết luận review status rõ ràng.
