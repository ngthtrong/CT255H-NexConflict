# /detect-stack

## Mô tả
Phát hiện tự động công nghệ, framework, và toolchain của dự án. Tạo `STACK.md` và bắt đầu điền vào `PROJECT-PROFILE.md`.

## Khi nào dùng
- Sau `/setup-project` cho dự án mới
- Khi bắt đầu làm việc với repo unfamiliar
- Khi stack của dự án thay đổi đáng kể

## Quy trình thực hiện

### Bước 1: Phát hiện Ngôn ngữ chính
```bash
# Node/TypeScript
[ -f package.json ] && echo "Node.js/TypeScript detected"
# Go
[ -f go.mod ] && echo "Go detected" && cat go.mod | head -5
# Python
[ -f requirements.txt ] || [ -f pyproject.toml ] && echo "Python detected"
# Ruby
[ -f Gemfile ] && echo "Ruby detected"
# Java/Kotlin
[ -f pom.xml ] || [ -f build.gradle ] && echo "JVM detected"
# Rust
[ -f Cargo.toml ] && echo "Rust detected"
```

### Bước 2: Phát hiện Frameworks
```bash
# Web frameworks
grep -r "express\|fastify\|gin\|echo\|fiber\|django\|flask\|fastapi\|rails\|spring" \
  package.json go.mod requirements.txt Gemfile 2>/dev/null | head -10

# Database
grep -ri "postgres\|mysql\|mongodb\|sqlite\|redis\|dynamodb" \
  package.json go.mod requirements.txt .env.example docker-compose.yml 2>/dev/null | head -10

# Testing frameworks
grep -ri "jest\|vitest\|pytest\|go test\|rspec\|junit" \
  package.json pyproject.toml Makefile 2>/dev/null | head -10
```

### Bước 3: Phát hiện Infrastructure
```bash
[ -f docker-compose.yml ] && echo "Docker Compose detected" && cat docker-compose.yml | grep "image:\|services:" | head -10
[ -f Dockerfile ] && echo "Dockerfile detected"
[ -f .github/workflows/*.yml ] && echo "GitHub Actions detected"
[ -f Makefile ] && echo "Makefile detected" && grep "^[a-z]*:" Makefile | head -10
```

### Bước 4: Extract Commands quan trọng
```bash
# Start command
cat package.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('scripts',{}))"
# Test command  
grep -E "test:|test =" Makefile package.json 2>/dev/null | head -5
```

### Bước 5: Tạo STACK.md
Tạo `.claude/workspace/STACK.md`:
```markdown
# STACK.md — Cấu hình Công nghệ Dự án

**Phát hiện tự động bởi Agent Analyst**
**Cần Human Review trước khi sử dụng**

## Ngôn ngữ
- **Primary**: {Go / TypeScript / Python / ...}
- **Version**: {1.21 / 18.x / 3.11 / ...}

## Frameworks
- **Web**: {Gin / Express / FastAPI / ...}
- **ORM**: {GORM / Prisma / SQLAlchemy / ...}
- **Testing**: {testify / Jest / pytest / ...}

## Database
- **Primary**: {PostgreSQL / MongoDB / MySQL / ...}
- **Cache**: {Redis / Memcached / ...}

## Infrastructure
- **Container**: {Docker / Docker Compose / ...}
- **CI/CD**: {GitHub Actions / ...}
- **Deploy**: {AWS / GCP / Heroku / local / ...}

## Commands
- **Start**: `{command}`
- **Test**: `{command}`
- **Coverage**: `{command}`
- **Lint**: `{command}`
- **Build**: `{command}`

---
> ⚠️ **HUMAN REVIEW REQUIRED**: Xác nhận các thông tin trên là chính xác.
> Sau khi verify, xóa dòng này và chạy `/update-agents` để cập nhật guardrails.
```

### Bước 6: Cập nhật PROJECT-PROFILE.md

### Bước 7: Commit
```bash
git add .claude/workspace/STACK.md .claude/PROJECT-PROFILE.md
git commit -m "chore: detect stack — {detected_stack}"
```

## Human Checkpoint ⚠️
**Stack Review Required**: Xác nhận `STACK.md` phản ánh đúng công nghệ thực tế trước khi tiếp tục.

## Agent sử dụng
**Agent Analyst** (Codebase Analyst) chủ trì.
