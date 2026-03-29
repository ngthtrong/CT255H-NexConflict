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
- Muốn tự động hóa toàn bộ quy trình phát triển với các human checkpoints.

## Procedure
1. **Validate Input** — Xác định phase hiện tại dựa trên REQ-ID/TASK-ID được cung cấp.
2. **Requirements Phase** — Nếu chưa có REQ, chạy `/analyze-requirements` để tạo spec.
3. **Planning Phase** — Sau khi REQ được phê duyệt, chạy `/plan-sprint` để tạo chuỗi tasks.
4. **Development Phase** — Với mỗi task:
   - `/write-unit-tests` cho task test
   - `/implement-task` cho task implementation
   - `/check-coverage` để đảm bảo coverage ≥ 80%
5. **Review Phase** — Tạo PR với `/create-pr` và review với `/techlead-review`.
6. **Testing Phase** — Chạy `/run-tests` cho E2E tests.
7. **Merge Phase** — Merge PR với `/merge-pr` sau khi được approved.
8. **Release Phase** — Chạy `/smoke-test` và `/release` với human sign-off.

## Human Checkpoints
- ✅ **Spec Approval** — PO đổi tên DRAFT-REQ → REQ để phê duyệt
- ✅ **Untracked Files** — Review các file không được track trước planning commit
- ✅ **Tech Lead Review** — Approve/Request changes trên PR
- ✅ **Smoke Test Sign-off** — PO ký duyệt báo cáo smoke test
- ✅ **Release Confirmation** — Gõ `YES` để xác nhận release

## Required References
- `.github-copilot/USAGE-GUIDE.md`
- `.github-copilot/copilot-instructions.md`
- `.github-copilot/commands/*.md`
- `.github-copilot/agents/*.md`

## Output Artifacts
- `DRAFT-REQ-xxxxx.md` / `REQ-xxxxx.md` trong `workspace/requirements/`
- `TASK-xxxxx.yaml` trong `workspace/tasks/`
- `SPRINT-xxxxx.md` trong `workspace/sprints/`
- Pull Request trên GitHub
- Release tag trên `main`
