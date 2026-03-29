# Hướng Dẫn Sử Dụng Agentic Software Team với GitHub Copilot

> Phiên bản đã tinh chỉnh để tận dụng native chat customizations: agents, instructions, prompts, skills, hooks, MCP servers, và VS Code plugins.

---

## Mục Lục

1. [Tổng quan](#tong-quan)
2. [Kiến trúc 3 lớp](#kien-truc-3-lop)
3. [Config đặt ở đâu](#config-dat-o-dau)
4. [Cài đặt nhanh](#cai-dat-nhanh)
5. [Đội ngũ Agent](#doi-ngu-agent)
6. [Quy trình chuẩn](#quy-trinh-chuan)
7. [Prompt và Skill](#prompt-va-skill)
8. [Hooks và Runtime Guardrails](#hooks-va-runtime-guardrails)
9. [MCP Servers và Plugins](#mcp-servers-va-plugins)
10. [Human Checkpoints](#human-checkpoints)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Tổng quan

**Agentic Software Team** được chia rõ 2 loại tri thức:

- **Workflow knowledge**: nằm trong `.github-copilot/` (persona, command, template, artifacts)
- **Runtime customization**: nằm trong `.github/` và `.vscode/` (agents, instructions, prompts, skills, hooks, MCP, plugin settings)

Triết lý vẫn giữ nguyên:

> AI thực thi kỷ luật, con người giữ quyền phán đoán.

---

## Kiến trúc 3 lớp

```text
Lop 1 - Workflow/Knowledge (Source of truth)
.github-copilot/
  agents/
  commands/
  templates/
  workspace/
  PROJECT-PROFILE.md

Lop 2 - Copilot Chat Customizations (Native)
.github/
  copilot-instructions.md
  AGENTS.md
  agents/*.agent.md
  instructions/*.instructions.md
  prompts/*.prompt.md
  skills/*/SKILL.md
  hooks/*.json

Lop 3 - IDE Runtime Integration
.vscode/
  settings.json
  mcp.json
  extensions.json
```

---

## Config đặt ở đâu

| Nhóm config | Vị trí khuyến nghị | Mục đích |
|-------------|--------------------|----------|
| Persona và workflow command | `.github-copilot/agents`, `.github-copilot/commands` | Nguồn sự thật để thực thi quy trình |
| Always-on project instruction | `.github/copilot-instructions.md` | Rule runtime chung cho Copilot Chat |
| Agent modes (chat custom agents) | `.github/agents/*.agent.md` | Chọn role nhanh trong Chat |
| File-scoped guidance | `.github/instructions/*.instructions.md` | Rule theo file pattern (`applyTo`) |
| Slash prompts tái sử dụng | `.github/prompts/*.prompt.md` | Mẫu prompt chạy nhanh qua `/` |
| Workflow skill đã đóng gói | `.github/skills/*/SKILL.md` | Tác vụ lặp lại, có quy trình rõ |
| Runtime policy hooks | `.github/hooks/*.json` + scripts | Chặn hành vi rủi ro ở cấp tool |
| MCP server definitions | `.vscode/mcp.json` | Kết nối công cụ/nguồn dữ liệu bên ngoài |
| Plugin recommendations | `.vscode/extensions.json` | Đồng bộ môi trường làm việc cho team |
| Workspace-level chat settings | `.vscode/settings.json` | Bật/tắt tính năng chat theo dự án |

**Lưu ý quan trọng**:
- Không đặt custom agent/prompt/instruction/hook vào `.github-copilot/`.
- `.github-copilot/` là nơi lưu workflow docs, KHÔNG phải runtime config directory của Copilot Chat.

---

## Cài đặt nhanh

### 1. Kiểm tra các thư mục cần thiết

- `.github-copilot/` đã có đủ `agents/commands/templates/workspace`
- `.github/` đã có `copilot-instructions`, `agents`, `instructions`, `prompts`, `skills`, `hooks`
- `.vscode/` đã có `settings.json`, `mcp.json`, `extensions.json`

### 2. Cài extension khuyến nghị

Mở VS Code -> Extensions -> cài theo `.vscode/extensions.json`:
- GitHub Copilot
- GitHub Copilot Chat
- GitHub Pull Requests and Issues
- GitLens
- PowerShell

### 3. Bật instruction files và prompt files

Đảm bảo workspace đang dùng `.vscode/settings.json` và extension Copilot Chat đã active.

### 4. Khởi động với orchestrator

Trong Chat:

```text
@workspace Sử dụng agent-orchestrator và thực hiện /setup-project
```

Hoặc gõ `/` để chọn prompt đã định nghĩa (Analyze Requirements, Plan Sprint, Implement Task, ...).

---

## Đội ngũ Agent

### Nguồn persona

- Persona gốc: `.github-copilot/agents/*.md`
- Chat custom agents: `.github/agents/*.agent.md`

### Mapping role

| Role | Custom agent | Persona gốc |
|------|--------------|-------------|
| BA | `agent-ba` | `.github-copilot/agents/ba.md` |
| PM | `agent-pm` | `.github-copilot/agents/pm.md` |
| Developer | `agent-developer` | `.github-copilot/agents/developer.md` |
| Tech Lead | `agent-techlead` | `.github-copilot/agents/techlead.md` |
| Tester | `agent-tester` | `.github-copilot/agents/tester.md` |
| Analyst | `agent-analyst` | `.github-copilot/agents/analyst.md` |
| Doc Sync | `agent-docsync` | `.github-copilot/agents/docsync.md` |
| Orchestrator | `agent-orchestrator` | `.github/AGENTS.md` + command routing |

---

## Quy trình chuẩn

```text
1) Setup va discovery
   /setup-project -> /detect-stack -> /discover-codebase -> /update-agents

2) Requirements
   Tạo BRIEF -> /analyze-requirements -> PO đổi tên DRAFT-REQ -> REQ

3) Planning
   /plan-sprint -> commit planning artifacts vao develop

4) Development loop
   /write-unit-tests -> /implement-task -> /run-tests -> /check-coverage
   -> /create-pr -> /techlead-review -> /merge-pr

5) Release
   /smoke-test -> PO sign-off -> /release (xác nhận YES)
```

### Rule branch bắt buộc

- Không push trực tiếp lên `main`/`develop`
- Feature trên `feature/TASK-xxxxx-*`
- Bug fix trên `fix/BUG-xxxxx-*`

---

## Prompt và Skill

### Prompt files (`.github/prompts/*.prompt.md`)

Được gọi nhanh qua `/` trong Chat:
- Analyze Requirements
- Plan Sprint
- Implement Task
- Tech Lead Review
- Smoke Test
- Release

### Skills (`.github/skills/*/SKILL.md`)

- `agentic-sprint`: điều phối sprint end-to-end
- `agentic-brownfield`: brownfield discovery + drift detection

Khi task lặp lại, ưu tiên skill thay vì viết prompt tự do mỗi lần.

### Tạo Skill mới

```
/create-skill my-custom-workflow --description "Mô tả workflow"
```

Lệnh này tạo skill mới trong `.github-copilot/skills/` với template chuẩn.

### Cấu trúc thư mục Skills

```
.github-copilot/skills/
├── agentic-sprint/
│   └── SKILL.md
├── agentic-brownfield/
│   └── SKILL.md
└── [custom-skill]/
    └── SKILL.md
```

---

## Hooks và Runtime Guardrails

### Hook files

- Config: `.github/hooks/policy.json`
- Scripts: `.github/hooks/scripts/*.ps1`

### Mục tiêu

- Inject system message ngay SessionStart
- Chặn command rủi ro cao trước khi tool chạy (PreToolUse)

### Các command đang bị chặn (mặc định)

- `git reset --hard`
- `git checkout --`
- `git clean -fd`
- `git push origin main`
- `git push origin develop`

Bạn có thể tùy chỉnh thêm pattern theo quy định team.

---

## MCP Servers và Plugins

### MCP config

File `.vscode/mcp.json` đang có sample servers:
- `filesystem`
- `github`
- `sequential-thinking`

**Lưu ý**:
- Server `github` cần token (`GITHUB_PERSONAL_ACCESS_TOKEN`)
- Nếu chưa cần dùng MCP nào, có thể xóa/tắt server đó trong `mcp.json`

### Plugin recommendations

File `.vscode/extensions.json` giúp team cài cùng bộ extension để tránh lệch môi trường.

---

## Human Checkpoints

7 điểm không được bỏ qua:

1. Stack review sau `/detect-stack`
2. Spec approval (DRAFT-REQ -> REQ)
3. Untracked files trước planning commit
4. ADR review trước architectural change
5. Bug P1 triage
6. Smoke test sign-off
7. Release confirmation (`YES`)

---

## Troubleshooting

### Không thấy custom agents trong chat

- Kiểm tra file `.github/agents/*.agent.md` có frontmatter hợp lệ
- Kiểm tra extension GitHub Copilot Chat đã bật
- Reload window trong VS Code

### Prompt/Skill không hiện khi gõ `/`

- Kiểm tra tên file đúng đuôi `.prompt.md` hoặc `SKILL.md`
- Kiểm tra `description` có đủ rõ ràng trigger phrase
- Kiểm tra `name` trong SKILL trùng với tên folder

### Instruction không được áp dụng

- Kiểm tra `applyTo` pattern có match file đang sửa
- Kiểm tra setting instruction files đã bật trong `.vscode/settings.json`

### Hook không chạy

- Kiểm tra JSON syntax trong `.github/hooks/policy.json`
- Kiểm tra script path tồn tại và có thể thực thi bằng `pwsh`

### MCP server không kết nối

- Kiểm tra đã cài runtime cần thiết (`node`, `npx`)
- Kiểm tra env vars và token
- Thử chạy command server thủ công trong terminal để debug

---

## Best Practices

1. Dùng `.github-copilot` cho tri thức workflow, dùng `.github` cho chat runtime customization.
2. Mỗi role có custom agent riêng, tránh một agent làm tất cả.
3. Prompt cho tác vụ đơn, Skill cho workflow lặp lại.
4. Hooks để enforce policy bắt buộc; instructions chỉ để hướng dẫn.
5. Luôn cập nhật `PROJECT-PROFILE.md` sau mỗi lần thay đổi stack/command.
6. Commit planning artifacts sớm để tránh mất state giữa các phiên chat.
7. Không bỏ qua human checkpoints dù deadline gấp.

---

*Agentic Software Team v1.1 for GitHub Copilot Chat*  
*Kỷ luật workflow ở `.github-copilot`, runtime customizations ở `.github` và `.vscode`.*
