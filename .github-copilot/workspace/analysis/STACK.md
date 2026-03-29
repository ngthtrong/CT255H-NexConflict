# Stack Detection Report

**Ngày**: 2026-03-29  
**Detected by**: Agent Codebase Analyst

---

## Architecture Overview

Đây là hệ thống **microservices** gồm 3 components chính:
- **Frontend**: Next.js (TypeScript/React)
- **Backend**: Spring Boot (Java)
- **AI Service**: FastAPI (Python)
- **Database**: PostgreSQL

## Frontend Stack

### Language & Runtime
- **Primary Language**: TypeScript
- **Runtime**: Node.js
- **Framework Version**: Next.js 16.1.7

### Framework & Libraries
- **Web Framework**: Next.js (React 19.2.3)
- **UI Framework**: Tailwind CSS 4.2.1
- **HTTP Client**: Axios 1.13.6
- **Styling**: PostCSS + Autoprefixer

### Testing
- **Test Runner**: Not configured (no test framework detected in package.json)
- **Linter**: ESLint 9 (eslint-config-next)

### Build & Deploy
- **Build Tool**: npm/Next.js build system
- **Package Manager**: npm
- **Scripts**:
  - Dev: `npm run dev`
  - Build: `npm run build`
  - Start: `npm start`
  - Lint: `npm run lint`

---

## Backend Stack

### Language & Runtime
- **Primary Language**: Java
- **Version**: Java 21
- **Framework**: Spring Boot 3.4.4

### Framework & Libraries
- **Web Framework**: Spring Boot Web (REST API)
- **ORM**: Spring Data JPA
- **Database Driver**: PostgreSQL driver + H2 (in-memory for testing)
- **Security**: Spring Security + JWT (jjwt 0.11.5)
- **Validation**: Spring Boot Validation
- **Utilities**: 
  - Lombok 1.18.38 (code generation)
  - Apache Commons CSV 1.10.0 (CSV processing)

### Testing
- **Test Runner**: JUnit (Spring Boot Test Starter)
- **Security Testing**: Spring Security Test
- **Coverage Tool**: Not explicitly configured (Maven default: JaCoCo recommended)

### Build & Deploy
- **Build Tool**: Maven (mvnw wrapper included)
- **Container**: Docker (via docker-compose.yml)
- **CI/CD**: Not configured (no .github/workflows detected)

---

## AI Service Stack

### Language & Runtime
- **Primary Language**: Python
- **Version**: Python 3.x (inferred from dependencies)
- **Framework**: FastAPI 0.109.1+

### Framework & Libraries
- **Web Framework**: FastAPI + Uvicorn 0.27.0
- **ML Libraries**:
  - scikit-surprise 1.1.3 (Collaborative Filtering)
  - scikit-learn 1.4.0 (ML utilities)
  - pandas 2.2.0 (data manipulation)
  - numpy 1.26.0+ (numerical computing)
- **UI**: Gradio 6.7.0+ (demo interface)
- **Visualization**: matplotlib 3.8.0, seaborn 0.13.0
- **Utilities**: 
  - joblib 1.3.0 (model persistence)
  - python-dotenv 1.0.0 (environment variables)

### Testing
- **Test Runner**: Not configured (pytest recommended but not in requirements.txt)
- **Coverage Tool**: Not configured

### Build & Deploy
- **Package Manager**: pip
- **Container**: Docker (via docker-compose.yml)

---

## Database Stack

### Primary Database
- **Database**: PostgreSQL 16 (Alpine)
- **Connection**: 
  - Host: postgres-db (Docker service)
  - Port: 5432
  - User: root
  - Database: nexconflict_db

### Testing Database
- **H2**: In-memory database for backend testing

---

## Infrastructure & DevOps

### Containerization
- **Docker**: Docker Compose 3.8
- **Services**:
  - postgres-db (PostgreSQL 16-alpine)
  - (Frontend, Backend, AI Service likely need separate service definitions)

### Version Control
- **VCS**: Git + GitHub
- **Repository**: ngthtrong/CT255H-NexConflict
- **Branching**: main, develop, feature branches

### CI/CD
- **Status**: ❌ Not configured
- **Recommendation**: Setup GitHub Actions for automated testing & deployment

---

## Recommended Commands

### Frontend (Next.js)
```yaml
directory: ./frontend
start: "npm run dev"
build: "npm run build"
test: "(not configured - recommend adding Jest/Vitest)"
lint: "npm run lint"
health_check_url: "http://localhost:3000"
```

### Backend (Spring Boot)
```yaml
directory: ./backend
start: "./mvnw spring-boot:run"
stop: "pkill -f 'spring-boot'"
test: "./mvnw test"
coverage: "./mvnw test jacoco:report"
lint: "(not configured - recommend Checkstyle/SpotBugs)"
health_check_url: "http://localhost:8080/actuator/health"
```

### AI Service (FastAPI)
```yaml
directory: ./ai-service
start: "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
stop: "pkill -f 'uvicorn'"
test: "(not configured - recommend pytest)"
lint: "(not configured - recommend pylint/black/ruff)"
health_check_url: "http://localhost:8000/docs"
```

### Full Stack (Docker Compose)
```yaml
directory: ./
start: "docker-compose up -d"
stop: "docker-compose down"
test: "(run per-service tests)"
health_check_url: "http://localhost:3000"
```

---

## Gaps & Recommendations

### Testing Coverage ⚠️
- ✅ Backend: Test framework configured (Spring Boot Test)
- ❌ Frontend: No test framework detected
- ❌ AI Service: No test framework detected
- **Recommendation**: Add Jest/Vitest for Frontend, pytest for AI Service

### Code Quality Tools ⚠️
- ✅ Frontend: ESLint configured
- ❌ Backend: No linter configured
- ❌ AI Service: No linter configured
- **Recommendation**: Add Checkstyle for Java, Black/Ruff for Python

### CI/CD Pipeline ⚠️
- ❌ No GitHub Actions workflows detected
- **Recommendation**: Setup automated testing, building, and deployment

### Documentation ⚠️
- ✅ README.md exists (basic)
- ❓ API documentation status unknown
- **Recommendation**: Add OpenAPI/Swagger docs, architecture diagrams

---

## External Dependencies

### Third-party Services
- PostgreSQL (self-hosted via Docker)
- MovieLens 20M Dataset (data source)

### External Libraries (Summary)
- **Security**: JWT (jsonwebtoken), Spring Security
- **Data**: PostgreSQL driver, pandas, numpy
- **ML**: scikit-surprise, scikit-learn
- **HTTP**: Axios, Uvicorn, Spring Web

---

## Next Steps

1. ✅ Review this STACK.md for accuracy
2. ⏭️ Run `/discover-codebase` for deeper analysis
3. ⏭️ Run `/update-agents` to configure agent commands based on stack
4. ⏭️ Add missing test frameworks (Frontend + AI Service)
5. ⏭️ Setup CI/CD pipeline
