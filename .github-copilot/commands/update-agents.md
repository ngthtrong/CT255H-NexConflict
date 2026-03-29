# /update-agents

## Mô tả
Cập nhật guardrails của các agent (đặc biệt là test commands, coverage commands, start/stop commands) sau khi `/detect-stack` và `PROJECT-PROFILE.md` đã được điền đầy đủ.

## Khi nào dùng
- Sau `/detect-stack` + human review STACK.md
- Khi tech stack của project thay đổi

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead (`agents/techlead.md`)

### Bước 1: Read PROJECT-PROFILE.md
```bash
cat .github-copilot/PROJECT-PROFILE.md
# Extract: test, coverage, lint, start, stop commands
```

### Bước 2: Update Agent Guardrails

Cập nhật các placeholder trong agent files:
- `{test_command}` → actual test command
- `{coverage_command}` → actual coverage command
- `{lint_command}` → actual lint command
- `{start_command}` → actual start command
- `{stop_command}` → actual stop command

### Bước 3: Validate Commands
```bash
# Test that commands work
{test_command} --help 2>/dev/null || echo "⚠️ Test command may not work"
{lint_command} --help 2>/dev/null || echo "⚠️ Lint command may not work"
```

### Bước 4: Update Command Files
Cập nhật các command markdown files với actual commands.

### Bước 5: Commit Changes
```bash
git add .github-copilot/agents/ .github-copilot/commands/
git commit -m "chore: update agent guardrails with project-specific commands"
git push origin develop
```

## Output
```
🔧 Agent Guardrails Updated

Commands configured:
- Test: {test_command} ✅
- Coverage: {coverage_command} ✅
- Lint: {lint_command} ✅
- Start: {start_command} ✅
- Stop: {stop_command} ✅

Agents updated:
- developer.md
- tester.md

Commands updated:
- implement-task.md
- write-unit-tests.md
- check-coverage.md
- smoke-test.md

All agents are now configured for this project's stack.
```

## Human Checkpoint
Khuyến nghị verify commands work trước khi chạy actual tasks.

## Agent sử dụng
**Agent Tech Lead**
