# /detect-stack

## Mô tả
Phát hiện tự động công nghệ, framework, và toolchain của dự án. Tạo `STACK.md` và bắt đầu điền vào `PROJECT-PROFILE.md`.

## Khi nào dùng
- Sau `/setup-project` cho dự án mới
- Khi bắt đầu làm việc với repo unfamiliar

## Quy trình thực hiện

**Agent thực hiện**: Codebase Analyst (`agents/analyst.md`)

### Bước 1: Scan Package Files
```bash
echo "=== Scanning for package files ==="
ls package.json go.mod requirements.txt Gemfile pom.xml Cargo.toml 2>/dev/null
```

### Bước 2: Detect Language & Framework

**Node.js/TypeScript:**
```bash
if [ -f package.json ]; then
  LANG="JavaScript/TypeScript"
  FRAMEWORK=$(cat package.json | jq -r '.dependencies | keys[]' | grep -E "express|fastify|nest|next|react|vue|angular" | head -1)
  TEST_RUNNER=$(cat package.json | jq -r '.devDependencies | keys[]' | grep -E "jest|mocha|vitest" | head -1)
fi
```

**Go:**
```bash
if [ -f go.mod ]; then
  LANG="Go"
  FRAMEWORK=$(cat go.mod | grep -E "gin|echo|fiber|chi" | head -1)
  TEST_RUNNER="go test"
fi
```

**Python:**
```bash
if [ -f requirements.txt ] || [ -f pyproject.toml ]; then
  LANG="Python"
  FRAMEWORK=$(grep -E "flask|django|fastapi|tornado" requirements.txt 2>/dev/null | head -1)
  TEST_RUNNER="pytest"
fi
```

### Bước 3: Detect Database
```bash
grep -rh "postgresql\|mysql\|mongodb\|sqlite\|redis" \
  package.json go.mod requirements.txt docker-compose.yml .env* 2>/dev/null | head -5
```

### Bước 4: Tạo STACK.md
Tạo `.github-copilot/workspace/analysis/STACK.md`:

```markdown
# Stack Detection Report

**Ngày**: {date}
**Detected by**: Agent Codebase Analyst

## Language & Runtime
- **Primary Language**: {language}
- **Version**: {version nếu tìm được}

## Framework
- **Web Framework**: {framework}
- **ORM/Database**: {orm}

## Testing
- **Test Runner**: {test_runner}
- **Coverage Tool**: {coverage_tool}

## Build & Deploy
- **Build Tool**: {npm/yarn/go build/pip/etc.}
- **Container**: {Docker nếu có Dockerfile}
- **CI/CD**: {GitHub Actions/GitLab CI/etc. nếu có}

## Recommended Commands

```yaml
start: "{detected start command}"
test: "{detected test command}"
coverage: "{detected coverage command}"
lint: "{detected lint command}"
```
```

### Bước 5: Update PROJECT-PROFILE.md
Điền thông tin vào `.github-copilot/PROJECT-PROFILE.md`.

### Bước 6: Commit
```bash
git add .github-copilot/workspace/analysis/STACK.md .github-copilot/PROJECT-PROFILE.md
git commit -m "docs: detect stack — {language} + {framework}"
git push origin develop
```

## Output
```
🔍 Stack Detection Complete

Detected:
- Language: {language}
- Framework: {framework}
- Database: {database}
- Test Runner: {test_runner}

Files created:
- .github-copilot/workspace/analysis/STACK.md
- .github-copilot/PROJECT-PROFILE.md (updated)

⚠️ HUMAN REVIEW REQUIRED:
Vui lòng review STACK.md và PROJECT-PROFILE.md để xác nhận detection chính xác.
```

## Human Checkpoint
**Khuyến nghị**: Review stack detection trước khi tiếp tục.

## Agent sử dụng
**Agent Codebase Analyst**
