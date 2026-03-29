# Agentic Software Team — GitHub Copilot Configuration

Chào mừng đến với **Agentic Software Team v1.0** — một đội ngũ phát triển phần mềm đa tác nhân (multi-agent) chạy trên GitHub Copilot Chat.

## Cách hoạt động

Hệ thống này bao gồm **7 agent** với vai trò chuyên biệt và **24+ slash command** bao phủ toàn bộ vòng đời phát triển phần mềm.

Kiến trúc đã được tách lớp:
- `.github-copilot/` = workflow knowledge (persona/command/template/artifacts)
- `.github/` = native chat customizations (agents/instructions/prompts/skills/hooks)
- `.vscode/` = runtime integrations (MCP, plugin recommendations, workspace settings)

## Đội ngũ Agent

| Agent | File | Trách nhiệm chính |
|-------|------|-------------------|
| BA (Business Analyst) | `agents/ba.md` | Phân tích yêu cầu, viết spec với Given/When/Then |
| PM (Project Manager) | `agents/pm.md` | Phân rã task, quản lý sprint, commit planning artifacts |
| Tech Lead | `agents/techlead.md` | ADR, code review, PR gate, NFR checklist |
| Developer | `agents/developer.md` | TDD, implement feature, N+1 scan, coverage gate |
| Tester | `agents/tester.md` | E2E test, smoke test, sign-off report |
| Codebase Analyst | `agents/analyst.md` | Brownfield discovery 10 giai đoạn |
| Doc Sync | `agents/docsync.md` | Phát hiện drift tài liệu sau mỗi sprint |

## Slash Commands Nhanh

```
/setup-project       → Cài đặt dự án mới
/discover-codebase   → Phân tích hệ thống hiện có
/analyze-requirements BRIEF-xxxxx → BA phân tích brief
/plan-sprint         → PM lập kế hoạch sprint
/write-unit-tests TASK-xxxxx      → Viết test trước (TDD Red)
/implement-task TASK-xxxxx        → Developer triển khai
/create-pr TASK-xxxxx             → Tạo Pull Request
/techlead-review TASK-xxxxx       → Tech Lead review PR
/merge-pr TASK-xxxxx              → Merge PR sau approval
/smoke-test v1.0.0                → Chạy smoke test
/release v1.0.0                   → Release lên main
```

## Cấu trúc Workflow Knowledge

```
.github-copilot/
├── copilot-instructions.md  ← File này (entry point)
├── PROJECT-PROFILE.md       ← Stack, commands, smoke test scenarios
├── agents/                  ← Persona definitions cho từng agent
├── commands/                ← Slash command definitions
├── skills/                  ← Workflow tái sử dụng
│   ├── agentic-sprint/
│   │   └── SKILL.md
│   └── agentic-brownfield/
│       └── SKILL.md
├── templates/               ← File mẫu (brief, task, ADR, bug, smoke report)
└── workspace/
    ├── requirements/
    │   └── input/           ← Đặt BRIEF-xxxxx.md tại đây
    ├── tasks/               ← TASK-xxxxx.yaml được generate
    ├── sprints/             ← Sprint plan files
    ├── bugs/                ← BUG-xxxxx.md
    ├── analysis/            ← Brownfield analysis docs
    └── reviews/             ← PR review reports
```

## Skills: Workflow Tái sử dụng

| Skill | Mô tả |
|-------|-------|
| `agentic-sprint` | Sprint end-to-end từ requirements → release |
| `agentic-brownfield` | Brownfield discovery 10 giai đoạn |

Tạo skill mới: `/create-skill my-custom-workflow`

## Cấu trúc Runtime Customizations

```text
.github/
├── copilot-instructions.md
├── AGENTS.md
├── agents/*.agent.md
├── instructions/*.instructions.md
├── prompts/*.prompt.md
├── skills/*/SKILL.md
└── hooks/*.json

.vscode/
├── settings.json
├── mcp.json
└── extensions.json
```

## Quy tắc Nhánh Git (Branch Rules)

- `main` — chỉ nhận merge từ `develop` qua `/release`
- `develop` — nơi merge các feature branch, chứa tất cả planning artifacts
- `feature/TASK-xxxxx-*` — nhánh làm việc của developer, tạo từ `develop`
- **NGHIÊM CẤM**: push trực tiếp lên `main` hay `develop`

## Điểm Controls Cần Human Review

1. **Stack Review** — sau `/detect-stack`
2. **Spec Approval** — đổi tên `DRAFT-REQ-xxxxx.md` → `REQ-xxxxx.md`
3. **Untracked Files** — trước mỗi commit planning
4. **ADR Review** — đọc ADR trước khi code bắt đầu
5. **Bug P1** — quyết định hotfix hay pause sprint
6. **Smoke Test Sign-off** — ký duyệt báo cáo smoke test
7. **Release Confirmation** — gõ `YES` để xác nhận release

## Bắt đầu ngay

```bash
# Dự án mới
/setup-project

# Hệ thống có sẵn (brownfield)
/detect-stack
/discover-codebase

# Xem hướng dẫn đầy đủ
# Đọc file .github-copilot/USAGE-GUIDE.md
```

## Cách sử dụng với GitHub Copilot

### Trong VS Code với GitHub Copilot Chat:
1. Mở Copilot Chat (Ctrl+Shift+I hoặc Cmd+Shift+I)
2. Sử dụng `@workspace` để chat với context của project
3. Chọn custom agent trong `.github/agents/*.agent.md` khi cần role cụ thể
4. Gõ `/` để chạy prompt/skill trong `.github/prompts` và `.github/skills`
5. Runtime policy được enforce qua `.github/hooks` và `.vscode/settings.json`

### Ví dụ:
```
@workspace Hãy thực hiện /analyze-requirements cho BRIEF-00001
@workspace Hãy chạy /plan-sprint để tạo task từ REQ đã được phê duyệt
@workspace Hãy thực hiện /implement-task TASK-00002 theo quy trình TDD
```

---
*Hệ thống được xây dựng dựa trên nguyên tắc: AI thực thi kỷ luật, con người giữ quyền phán đoán.*
