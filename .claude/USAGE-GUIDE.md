# 📖 Hướng dẫn sử dụng: Agentic Software Team

> Một đội ngũ phát triển AI đa tác nhân chạy hoàn toàn trên Claude Code — 7 agents, 24 slash commands, không cần infrastructure.

---

## 🚀 Bắt đầu nhanh (5 phút)

### 1. Mở Claude Code tại thư mục dự án
```bash
cd /đường/dẫn/đến/dự-án
claude
```

### 2. Chạy lệnh setup
```
/setup-project
```

### 3. Tạo brief đầu tiên
Copy file `.claude/templates/BRIEF-template.md` sang `.claude/workspace/requirements/input/BRIEF-00001.md` và điền thông tin.

### 4. Bắt đầu sprint
```
/analyze-requirements BRIEF-00001
```
*(chờ PO đổi tên DRAFT-REQ → REQ)*
```
/plan-sprint
/write-unit-tests TASK-00001
/implement-task TASK-00002
```

---

## 🏗️ Cấu trúc hệ thống

```
.claude/
├── CLAUDE.md                    ← Entry point (Claude Code tự đọc)
├── PROJECT-PROFILE.md           ← Stack, commands, smoke test scenarios
├── agents/                      ← Persona definitions
│   ├── ba.md                    ← Business Analyst
│   ├── pm.md                    ← Project Manager
│   ├── techlead.md              ← Tech Lead
│   ├── developer.md             ← Developer (TDD)
│   ├── tester.md                ← QA / Tester
│   ├── analyst.md               ← Codebase Analyst
│   └── docsync.md               ← Documentation Sync
├── commands/                    ← Slash command definitions
│   ├── setup-project.md         → /setup-project
│   ├── detect-stack.md          → /detect-stack
│   ├── discover-codebase.md     → /discover-codebase
│   ├── analyze-requirements.md  → /analyze-requirements
│   ├── plan-sprint.md           → /plan-sprint
│   ├── write-unit-tests.md      → /write-unit-tests
│   ├── implement-task.md        → /implement-task
│   ├── check-coverage.md        → /check-coverage
│   ├── run-tests.md             → /run-tests
│   ├── create-pr.md             → /create-pr
│   ├── techlead-review.md       → /techlead-review
│   ├── merge-pr.md              → /merge-pr
│   ├── smoke-test.md            → /smoke-test
│   ├── release.md               → /release
│   ├── report-bug.md            → /report-bug
│   ├── triage-bug.md            → /triage-bug
│   ├── verify-fix.md            → /verify-fix
│   ├── bug-status.md            → /bug-status
│   ├── branch-status.md         → /branch-status
│   ├── cleanup-branches.md      → /cleanup-branches
│   ├── scan-untracked.md        → /scan-untracked
│   ├── update-agents.md         → /update-agents
│   ├── doc-sync.md              → /doc-sync
│   ├── dashboard.md             → /dashboard
│   └── create-skill.md          → /create-skill
├── skills/                      ← Workflow tái sử dụng
│   ├── agentic-sprint/
│   │   └── SKILL.md             ← Sprint end-to-end workflow
│   └── agentic-brownfield/
│       └── SKILL.md             ← Brownfield discovery workflow
├── templates/                   ← File mẫu
│   ├── BRIEF-template.md
│   ├── TASK-template.yaml
│   ├── ADR-template.md
│   └── BUG-template.md
└── workspace/                   ← Dữ liệu runtime
    ├── requirements/
    │   └── input/               ← Đặt BRIEF-*.md tại đây
    ├── tasks/                   ← TASK-*.yaml (tạo bởi PM)
    ├── sprints/                 ← Sprint plans
    ├── bugs/                    ← BUG-*.md
    ├── analysis/                ← Codebase analysis docs
    └── reviews/                 ← PR review reports
```

---

## 👥 7 Agents và Vai trò

| Agent | Kích hoạt bởi | Trách nhiệm |
|-------|--------------|-------------|
| **BA** | `/analyze-requirements` | Phân tích brief → DRAFT-REQ với Given/When/Then |
| **PM** | `/plan-sprint`, `/dashboard`, `/bug-status` | Phân rã task, quản lý sprint, commit planning artifacts |
| **Tech Lead** | `/techlead-review`, `/merge-pr`, ADR | Review PR với checklist NFR bắt buộc |
| **Developer** | `/write-unit-tests`, `/implement-task`, `/create-pr` | TDD, code, N+1 scan, coverage gate |
| **Tester** | `/run-tests`, `/smoke-test`, `/verify-fix` | E2E test, smoke test live env, verify bugs |
| **Analyst** | `/discover-codebase`, `/detect-stack` | Brownfield discovery 10 giai đoạn |
| **Doc Sync** | `/doc-sync` (tự động sau merge) | Phát hiện drift tài liệu vs code |

---

## ⚙️ Quy tắc Git bất biến

```
main ──────────────────────────────────── (chỉ nhận từ /release)
        ↑
develop ───────────────────────────────── (planning artifacts + merges)
        ↑                ↑
feature/TASK-00002   fix/BUG-00001        (chỉ từ develop, chỉ về develop)
```

- **NGHIÊM CẤM** commit trực tiếp lên `main` hay `develop`
- Mọi planning artifact phải commit vào `develop` TRƯỚC khi code bắt đầu
- `/release` là lệnh duy nhất được phép merge `develop` → `main`

---

## 🛡️ 7 Điểm Human-in-the-Loop

| # | Khi nào | Hành động cần làm |
|---|---------|------------------|
| 1 | Sau `/detect-stack` | Review `STACK.md` — xác nhận stack đúng |
| 2 | Sau `/analyze-requirements` | Đổi tên `DRAFT-REQ-*.md` → `REQ-*.md` |
| 3 | Trước planning commit | Quyết định cho từng untracked file |
| 4 | Sau Tech Lead tạo ADR | Đọc và đồng ý ADR trước khi code bắt đầu |
| 5 | Bug P1 xuất hiện | Quyết định: hotfix ngay hay next sprint |
| 6 | `/smoke-test` hoàn thành | Ký vào báo cáo (APPROVED) |
| 7 | `/release` chạy | Gõ `YES` để xác nhận release |

---

## 📋 Workflow đầy đủ: Greenfield Project

```
# === SETUP ===
/setup-project                 → Cài đặt hệ thống, tạo develop branch

# === PHÂN TÍCH STACK (dự án có sẵn) ===
/detect-stack                  → Phát hiện công nghệ
                               ← Human: Verify STACK.md
/discover-codebase             → Phân tích 10 giai đoạn
/update-agents                 → Cập nhật guardrails với commands thực

# === PLANNING ===
# Tạo brief: .claude/workspace/requirements/input/BRIEF-00001.md
/analyze-requirements BRIEF-00001  → BA viết DRAFT-REQ-00001.md
                                   ← Human: Đổi tên → REQ-00001.md
/plan-sprint                       → PM tạo và commit task sequence

# === IMPLEMENTATION (lặp lại với từng TASK) ===
/write-unit-tests TASK-00001   → Viết failing tests (TDD Red)
/implement-task TASK-00002     → Implement + N+1 scan + coverage gate
/run-tests TASK-00003          → Viết E2E tests
/create-pr TASK-00002          → Tạo PR
/techlead-review TASK-00002    → Tech Lead review với PR checklist đầy đủ
/merge-pr TASK-00002           → Squash merge → develop, tự trigger doc-sync

# === RELEASE ===
/smoke-test v1.0.0             → Test trên live env (không dùng mock)
                               ← Human: Ký vào báo cáo (APPROVED)
/release v1.0.0                → Cross-check hash → regression tests → YES → merge main → tag
```

---

## 🐛 Workflow xử lý Bug

```
/report-bug "Mô tả bug ngắn gọn"   → Tạo BUG-*.md và commit
/triage-bug BUG-00001               → PM + Tech Lead phân tích
                                    ← Human (P1): Quyết định hotfix hay schedule
/verify-fix BUG-00001               → Tester xác nhận đã fix
/bug-status                         → Xem tổng quan tất cả bugs
```

---

## 🔧 Commands tiện ích

| Command | Mục đích |
|---------|---------|
| `/dashboard` | Tổng quan sprint: tasks, bugs, branches trong 1 màn hình |
| `/branch-status` | Liệt kê tất cả branches và trạng thái |
| `/cleanup-branches` | Xóa branches đã merged, giữ git clean |
| `/scan-untracked` | Kiểm tra untracked files trước khi commit |
| `/check-coverage` | Xem coverage breakdown chi tiết |
| `/doc-sync` | Đồng bộ tài liệu thủ công |
| `/create-skill` | Tạo skill mới để đóng gói workflow |

---

## 🧩 Skills: Workflow Tái sử dụng

Skills là các đơn vị workflow đóng gói, cho phép tái sử dụng các chuỗi hành động phức tạp.

### Cấu trúc thư mục Skills

```
.claude/skills/
├── agentic-sprint/
│   └── SKILL.md
├── agentic-brownfield/
│   └── SKILL.md
└── [custom-skill]/
    └── SKILL.md
```

### Skills có sẵn

| Skill | Mô tả |
|-------|-------|
| `agentic-sprint` | Chạy toàn bộ sprint từ requirements → release với các checkpoint |
| `agentic-brownfield` | Phân tích brownfield 10 giai đoạn và drift detection |

### Tạo Skill mới

```
/create-skill my-custom-workflow --description "Mô tả workflow"
```

### Format SKILL.md

```yaml
---
name: skill-name
description: 'Mô tả ngắn gọn'
argument-hint: 'Gợi ý tham số'
user-invocable: true
---
# Tên Skill

## When to Use
- Use case 1
- Use case 2

## Procedure
1. Bước 1
2. Bước 2

## Required References
- `.claude/commands/relevant.md`
```

---

## 💡 Tips & Best Practices

### Khi bắt đầu phiên Claude Code mới
```
/dashboard    ← Xem trạng thái hiện tại ngay lập tức
```

### Khi không biết làm gì tiếp theo
```
/dashboard    ← Nhìn vào TASKS section, task nào đang pending?
```

### Viết Brief tốt
- Càng cụ thể càng tốt — BA chỉ phân tích được những gì bạn cung cấp
- Nêu rõ Out of Scope để tránh feature creep
- Liệt kê cả edge cases bạn đang nghĩ đến

### Làm việc với ADR
- Tech Lead sẽ tự động đề xuất ADR khi phát hiện quyết định kiến trúc quan trọng
- **Đừng bỏ qua ADR** — chúng là memory của hệ thống về lý do tại sao code có dạng này

### Release an toàn
- Chạy `/smoke-test` chỉ khi `/develop` branch ổn định
- Hãy đọc kỹ báo cáo smoke test trước khi ký
- Sau khi ký, **đừng commit thêm vào develop** — nếu cần hotfix, phải smoke test lại

---

## ❓ Troubleshooting

**"TASK YAML chưa trong git"**
→ Chạy `/plan-sprint` trước, PM sẽ commit vào develop.

**"Đang ở main, không thể implement"**
→ `git checkout develop`, sau đó thử lại lệnh.

**"Coverage < 80%"**
→ Xem `/check-coverage` để biết file nào thiếu test. Thêm test hoặc ghi tech debt.

**"Smoke test hash mismatch"**
→ Có commit push lên develop sau khi smoke test. Cần chạy `/smoke-test` lại.

**"PR bị CHANGES REQUESTED"**
→ Đọc file review tại `.claude/workspace/reviews/REVIEW-TASK-*.md`, sửa BLOCKER items, rồi `/create-pr` lại.

---

*Agentic Software Team v1.0 — AI thực thi kỷ luật, con người giữ quyền phán đoán.*
