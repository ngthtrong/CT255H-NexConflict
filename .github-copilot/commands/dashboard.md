# /dashboard

## Mô tả
Hiển thị tổng quan toàn bộ trạng thái sprint hiện tại trong một màn hình: tasks, coverage, bugs, branch status. Sprint command center trong terminal.

## Cú pháp
```
/dashboard
```

## Quy trình thực hiện

**Agent thực hiện**: PM (`agents/pm.md`)

### Bước 1: Collect Data
```bash
# Tasks
TASKS_TOTAL=$(ls .github-copilot/workspace/tasks/TASK-*.yaml 2>/dev/null | wc -l)
TASKS_DONE=$(grep -l "status: done\|status: merged" .github-copilot/workspace/tasks/TASK-*.yaml 2>/dev/null | wc -l)

# Bugs
BUGS_OPEN=$(grep -l "status: open" .github-copilot/workspace/bugs/BUG-*.md 2>/dev/null | wc -l)

# Branches
BRANCHES=$(git branch | wc -l)
```

### Bước 2: Generate Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║                    SPRINT DASHBOARD                               ║
║                    {date}                                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📋 TASKS                          🐛 BUGS                       ║
║  ═══════════════════              ═══════════════════            ║
║  Total:    {N}                     Open:       {X}               ║
║  Done:     {M} ({%})               In Progress: {Y}              ║
║  Pending:  {K}                     Fixed:       {Z}              ║
║  Blocked:  {B}                                                   ║
║                                                                   ║
║  Progress: [████████░░░░░░░░░░] {X}%                            ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🌳 BRANCHES                       📊 COVERAGE                   ║
║  ═══════════════════              ═══════════════════            ║
║  Active:   {N}                     Current: {X}%                 ║
║  Merged:   {M}                     Target:  80%                  ║
║  Stale:    {K}                     Status:  {✅/❌}              ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🚨 ATTENTION NEEDED                                             ║
║  ═══════════════════                                             ║
║  {list of P1 bugs, blocked tasks, stale branches}                ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝

Quick Actions:
  /implement-task TASK-{next}    Continue development
  /bug-status                    Review bugs
  /branch-status                 Manage branches
```

## Output
Dashboard hiển thị trực tiếp trong terminal.

## Human Checkpoint
Không cần — đây là lệnh reporting.

## Agent sử dụng
**Agent PM**
