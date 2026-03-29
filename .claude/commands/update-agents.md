# /update-agents

## Mô tả
Cập nhật guardrails của các agent (đặc biệt là test commands, coverage commands, start/stop commands) sau khi `/detect-stack` và `PROJECT-PROFILE.md` đã được điền đầy đủ.

## Khi nào dùng
- Sau `/detect-stack` + human review STACK.md
- Khi tech stack của project thay đổi

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead

### Bước 1: Đọc PROJECT-PROFILE.md
Lấy các giá trị cụ thể:
- `test_command`
- `coverage_command`
- `start_command` / `stop_command`
- `health_check_url`
- `lint_command`

### Bước 2: Cập nhật placeholder trong agents

Tìm và thay thế các placeholder `{test_command}`, `{coverage_command}` v.v. trong:
- `.claude/agents/developer.md`
- `.claude/agents/tester.md`
- `.claude/commands/implement-task.md`
- `.claude/commands/smoke-test.md`
- `.claude/commands/check-coverage.md`

### Bước 3: Commit
```bash
git add .claude/agents/ .claude/commands/
git commit -m "chore: update agent guardrails với stack-specific commands"
git push origin develop
```

### Bước 4: Báo cáo
```
✅ Agents đã được cập nhật với commands thực tế:

  Test:     {test_command}
  Coverage: {coverage_command}
  Start:    {start_command}
  Health:   {health_check_url}

Agents cập nhật: developer.md, tester.md
Commands cập nhật: implement-task.md, smoke-test.md, check-coverage.md
```

## Agent sử dụng
**Agent Tech Lead**
