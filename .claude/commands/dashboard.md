# /dashboard

## Mô tả
Hiển thị tổng quan toàn bộ trạng thái sprint hiện tại trong một màn hình: tasks, coverage, bugs, branch status. Sprint command center trong terminal.

## Quy trình thực hiện

**Agent thực hiện**: PM

```bash
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           AGENTIC SOFTWARE TEAM — DASHBOARD              ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Sprint: $(ls .claude/workspace/sprints/ | tail -1)      "
echo "║  Branch: $(git branch --show-current)                    "
echo "║  Date:   $(date +%Y-%m-%d)                                "
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  TASKS                                                    "

# Đọc tất cả tasks và hiện status
for YAML in .claude/workspace/tasks/TASK-*.yaml; do
  ID=$(basename $YAML .yaml)
  TYPE=$(grep "^type:" $YAML | awk '{print $2}')
  STATUS=$(grep "^status:" $YAML | awk '{print $2}')
  DESC=$(grep "^description:" $YAML | cut -d: -f2- | cut -c1-35)
  
  ICON="⬜"
  [ "$STATUS" = "done" ] && ICON="✅"
  [ "$STATUS" = "in-progress" ] && ICON="🔄"
  [ "$STATUS" = "merged" ] && ICON="✅"
  [ "$STATUS" = "blocked" ] && ICON="🚫"
  
  printf "║  %s %s [%s] %s\n" "$ICON" "$ID" "$TYPE" "$DESC"
done

echo "╠══════════════════════════════════════════════════════════╣"
echo "║  BUGS                                                     "

# P1 bugs
P1_OPEN=$(ls .claude/workspace/bugs/BUG-*.md 2>/dev/null | \
  xargs grep -l "priority: P1" | xargs grep -l "status: open" | wc -l)
P2_OPEN=$(ls .claude/workspace/bugs/BUG-*.md 2>/dev/null | \
  xargs grep -l "priority: P2" | xargs grep -l "status: open" 2>/dev/null | wc -l)
echo "║  🔴 P1 Open: $P1_OPEN    🟡 P2 Open: $P2_OPEN           "

echo "╠══════════════════════════════════════════════════════════╣"
echo "║  BRANCHES                                                 "
git branch | grep -E "feature/|fix/|test/" | while read B; do
  echo "║    $B"
done

echo "╠══════════════════════════════════════════════════════════╣"
echo "║  QUICK COMMANDS                                          ║"
echo "║  /plan-sprint  /implement-task  /smoke-test  /release   ║"
echo "╚══════════════════════════════════════════════════════════╝"
```

## Output mẫu
```
╔══════════════════════════════════════════════════════════╗
║           AGENTIC SOFTWARE TEAM — DASHBOARD              ║
╠══════════════════════════════════════════════════════════╣
║  Sprint: SPRINT-2025-03-26.md
║  Branch: develop
║  Date:   2025-03-26
╠══════════════════════════════════════════════════════════╣
║  TASKS
║  ✅ TASK-00001 [unit-test]       Viết failing tests cho auth
║  🔄 TASK-00002 [implementation]  Implement auth feature
║  ⬜ TASK-00003 [e2e-test]        E2E tests cho auth
╠══════════════════════════════════════════════════════════╣
║  BUGS
║  🔴 P1 Open: 0    🟡 P2 Open: 1
╠══════════════════════════════════════════════════════════╣
║  BRANCHES
║    feature/TASK-00002-auth-login
╚══════════════════════════════════════════════════════════╝
```

## Agent sử dụng
**Agent PM**
