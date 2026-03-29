# PROJECT PROFILE: CT255H-NexConflict

**Analysis Date**: 2025-01-21  
**Analyst**: AI Agent (Comprehensive Brownfield Discovery)  
**Project Type**: Academic Movie Recommendation System  
**Status**: 🟡 Development / MVP Phase

---

## 📋 Executive Summary

**NexConflict** is a full-stack movie recommendation platform built for CT255H (Business Intelligence) course, implementing collaborative and content-based filtering on the MovieLens 20M dataset.

### Key Metrics
- **Total Lines of Code**: ~7,173
- **Services**: 3 (Frontend, Backend, AI Service)
- **Languages**: TypeScript, Java, Python
- **Test Coverage**: ~2% overall (🔴 CRITICAL)
- **Documentation Quality**: 30% accuracy (🔴 POOR)
- **Fragile Zones**: 17 identified (6 HIGH, 6 MEDIUM, 5 LOW)

### Health Score: **45/100** (🟡 MODERATE RISK)

| Dimension | Score | Status |
|-----------|-------|--------|
| Code Quality | 60/100 | 🟡 MODERATE |
| Test Coverage | 2/100 | 🔴 CRITICAL |
| Documentation | 30/100 | 🔴 POOR |
| Security | 40/100 | 🔴 CRITICAL |
| Performance | 65/100 | 🟡 MODERATE |
| Maintainability | 55/100 | 🟡 MODERATE |

---

## 🏗️ System Architecture

### Service Topology
```
┌────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│  Next.js 16 (React 19, TypeScript, Tailwind CSS) - Port 3000  │
└───────────────────────────┬────────────────────────────────────┘
                            │ REST/JWT
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                          BACKEND                                │
│   Spring Boot 3.4.4 (Java 21, Spring Security) - Port 8080    │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐ │
│  │Controller│──│ Service  │──│Repository │──│     H2 DB    │ │
│  │ (8 REST) │  │(4 logic) │  │(7 JPA)    │  │  (In-Memory) │ │
│  └──────────┘  └─────┬────┘  └───────────┘  └──────────────┘ │
└──────────────────────┼─────────────────────────────────────────┘
                       │ REST
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                        AI SERVICE                               │
│          FastAPI (Python 3.10+) - Port 8000                    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ SVD Model    │  │Content-Based │  │  MovieLens 20M Data  │ │
│  │(Surprise lib)│  │(Cosine Sim)  │  │  (62K movies,        │ │
│  │    *.pkl     │  │    *.pkl     │  │   1,128 genome tags) │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Next.js | 16.1.7 | Server-side rendering, App Router |
| | React | 19.2.3 | UI framework |
| | TypeScript | 5.x | Type safety |
| | Tailwind CSS | 4.2.1 | Styling |
| | Axios | 1.13.6 | HTTP client |
| **Backend** | Spring Boot | 3.4.4 | REST API framework |
| | Java | 21 | Programming language |
| | Spring Security | 3.4.4 | Authentication/authorization |
| | Spring Data JPA | 3.4.4 | ORM |
| | H2 Database | (runtime) | In-memory database |
| | PostgreSQL | 16 | Production database (configured) |
| | JWT (JJWT) | 0.11.5 | Token-based auth |
| **AI Service** | FastAPI | (latest) | API framework |
| | Python | 3.10+ | Programming language |
| | scikit-surprise | (latest) | SVD implementation |
| | scikit-learn | (latest) | Cosine similarity, TF-IDF |
| | pandas | (latest) | Data manipulation |
| | numpy | (latest) | Numerical computing |
| **Infrastructure** | Docker | - | Containerization (PostgreSQL only) |
| | Maven | 3.x | Java build tool |
| | npm | (latest) | Node package manager |

---

## 🚨 Fragile Zones Summary

### 🔴 HIGH RISK (6 zones)

| ID | Zone | Impact | Likelihood | Effort | Priority |
|----|------|--------|------------|--------|----------|
| **FZ-H01** | Duplicate JWT Security Classes | Critical | High | 2h | P1 |
| **FZ-H02** | Hardcoded JWT Secret | Critical | High | 1h | P1 |
| **FZ-H03** | Hardcoded TMDB API Key | High | Medium | 30m | P1 |
| **FZ-H04** | No DB Connection Pooling | High | Medium | 1h | P2 |
| **FZ-H05** | AI Service Single Point of Failure | High | High | 4h | P2 |
| **FZ-H06** | No Rating Input Validation | Medium | Medium | 1h | P2 |

**Total P1 Effort**: 3.5 hours  
**Total P2 Effort**: 6 hours

### 🟡 MEDIUM RISK (6 zones)

| ID | Zone | Impact | Likelihood | Effort | Priority |
|----|------|--------|------------|--------|----------|
| **FZ-M01** | God Function (AI Service) | Medium | Low | 3h | P3 |
| **FZ-M02** | Monolithic train.py | Medium | Low | 6h | P3 |
| **FZ-M03** | No Database Migrations | High | Medium | 4h | P2 |
| **FZ-M04** | Unbounded Movie Query | Medium | High | 2h | P3 |
| **FZ-M05** | No RestTemplate Timeout | Medium | Medium | 30m | P3 |
| **FZ-M06** | Onboarding Ratings Unused | Low | High | 2h | P3 |

**Total P3 Effort**: 13.5 hours

### 🟢 LOW RISK (5 zones)

| ID | Zone | Effort | Priority |
|----|------|--------|----------|
| **FZ-L01** | Frontend No Tests | 4h | P4 |
| **FZ-L02** | Backend Smoke Test Only | 6h | P4 |
| **FZ-L03** | AI Service No Tests | 4h | P4 |
| **FZ-L04** | No Logging Framework (FE) | 2h | P4 |
| **FZ-L05** | No API Rate Limiting | 2h | P4 |

**Total P4 Effort**: 18 hours

---

## 📊 Technical Debt Register

### 🔐 Security Debt (CRITICAL)

| Item | Description | Risk | Remediation |
|------|-------------|------|-------------|
| **SD-01** | Hardcoded JWT secret in source code | 🔴 HIGH | Move to environment variable, rotate secret |
| **SD-02** | Exposed TMDB API key in Git | 🔴 HIGH | Revoke key, use env var, add to .gitignore |
| **SD-03** | No JWT refresh mechanism | 🟡 MEDIUM | Implement refresh tokens (7-day expiry) |
| **SD-04** | CORS allows all origins (AI Service) | 🟡 MEDIUM | Restrict to known origins |
| **SD-05** | No rate limiting on endpoints | 🟡 MEDIUM | Add Bucket4j (100 req/min per user) |
| **SD-06** | No input validation on ratings | 🔴 HIGH | Add @Valid + Bean Validation constraints |
| **SD-07** | Admin endpoints not protected | 🟡 MEDIUM | Add ROLE_ADMIN authorization |

**Total Security Issues**: 7  
**Estimated Fix Effort**: 8 hours

---

### 🏗️ Architectural Debt

| Item | Description | Risk | Remediation |
|------|-------------|------|-------------|
| **AD-01** | No service discovery (hardcoded URLs) | 🟡 MEDIUM | Use Spring Cloud Config or Consul |
| **AD-02** | No API versioning (/api/v1/) | 🟡 MEDIUM | Add versioning strategy (URL or header) |
| **AD-03** | No circuit breaker for AI service | 🔴 HIGH | Add Resilience4j with fallback |
| **AD-04** | No caching layer (recommendations) | 🟡 MEDIUM | Add Redis with 1-hour TTL |
| **AD-05** | No message queue (async tasks) | 🟢 LOW | Consider RabbitMQ for poster sync |
| **AD-06** | Single AI service instance (no scaling) | 🟡 MEDIUM | Containerize + Kubernetes horizontal scaling |
| **AD-07** | No centralized logging (ELK) | 🟡 MEDIUM | Add ELK stack or CloudWatch |
| **AD-08** | No database migrations (Flyway) | 🔴 HIGH | Add Flyway, create V1__initial.sql |

**Total Architecture Issues**: 8  
**Estimated Fix Effort**: 20 hours

---

### 🧪 Testing Debt (CRITICAL)

| Service | Current Coverage | Target Coverage | Missing Tests | Effort |
|---------|------------------|-----------------|---------------|--------|
| **Backend** | ~5% | 60-70% | 24 tests | 12h |
| **Frontend** | 0% | 50-60% | 12 tests | 8h |
| **AI Service** | 0% | 40-50% | 11 tests | 6h |
| **Total** | **~2%** | **50-60%** | **47 tests** | **26h** |

**Critical Missing Tests**:
- JWT authentication flow (login, token validation, expiry)
- AI service fallback logic (when AI down)
- Rating validation (reject invalid values)
- Onboarding completion (set flag, save data)
- Recommendation algorithms (SVD, cosine similarity)

---

### 📝 Documentation Debt

| Item | Description | Status | Effort |
|------|-------------|--------|--------|
| **DD-01** | README.md has wrong tech stack (Gradio) | 🔴 CRITICAL | 1h |
| **DD-02** | README.md has wrong file names (rating.csv) | 🔴 HIGH | 30m |
| **DD-03** | README.md has wrong commands (python -m src.app) | 🔴 HIGH | 30m |
| **DD-04** | Missing docs/ARCHITECTURE.md | 🟡 MEDIUM | 3h |
| **DD-05** | Missing API documentation (Swagger) | 🟡 MEDIUM | 2h |
| **DD-06** | Missing docs/CONFIGURATION.md | 🟡 MEDIUM | 1h |
| **DD-07** | Missing docs/DEPLOYMENT.md | 🟡 MEDIUM | 2h |
| **DD-08** | No inline code comments | 🟢 LOW | 8h |

**Documentation Accuracy**: 30%  
**Total Fix Effort**: 18 hours

---

### 💾 Data Debt

| Item | Description | Risk | Remediation |
|------|-------------|------|-------------|
| **DT-01** | Onboarding ratings not used by AI | 🟡 MEDIUM | Save to `ratings` table (not separate) |
| **DT-02** | No database indexes on queries | 🟡 MEDIUM | Add indexes on `genres`, `user_id`, `movie_id` |
| **DT-03** | Full table scan on genre search | 🔴 HIGH | Add full-text index or native query |
| **DT-04** | No data validation at DB level | 🟡 MEDIUM | Add CHECK constraints (rating 0.5-5.0) |
| **DT-05** | No audit trail (created_at, updated_at) | 🟢 LOW | Add @CreatedDate, @LastModifiedDate |

**Total Data Issues**: 5  
**Estimated Fix Effort**: 6 hours

---

### 🚀 Performance Debt

| Item | Description | Impact | Remediation |
|------|-------------|--------|-------------|
| **PD-01** | AI prediction iterates 1000 movies on-demand | 🟡 MEDIUM | Add LRU cache (user_id → recs) |
| **PD-02** | No pagination on watchlist/ratings | 🟢 LOW | Add Pageable parameter |
| **PD-03** | No connection pooling config | 🟡 MEDIUM | Configure HikariCP (max 10, min 5) |
| **PD-04** | No RestTemplate timeout | 🔴 HIGH | Set 5s connect, 10s read timeout |
| **PD-05** | TMDB poster sync blocks startup | 🟡 MEDIUM | Make async with @Async |

**Total Performance Issues**: 5  
**Estimated Fix Effort**: 6 hours

---

## 📈 Code Quality Metrics

### Lines of Code by Service

| Service | Files | LOC | Avg LOC/File | Complexity |
|---------|-------|-----|--------------|------------|
| **Frontend** | 15 | ~2,000 | 133 | Low |
| **Backend** | 46 | ~4,500 | 98 | Medium |
| **AI Service** | 2 | ~673 | 337 | High |
| **TOTAL** | **63** | **~7,173** | **114** | **Medium** |

### Complexity Hotspots

| Function | File | Cyclomatic Complexity | LOC | Risk |
|----------|------|----------------------|-----|------|
| `get_recommendations()` | ai-service/main.py | ~8 | 43 | 🟡 HIGH |
| `build_content_model()` | ai-service/train.py | ~6 | 129 | 🟡 MEDIUM |
| `completeOnboarding()` | OnboardingController.java | ~5 | 56 | 🟡 MEDIUM |
| `getTopGenresMovies()` | RecommendationController.java | ~4 | 27 | 🟡 MEDIUM |

---

## 🔧 Recommended Improvements

### Phase 1: Critical Security Fixes (P1) - 3.5 hours
✅ **Must-Do Before Production**

1. Move JWT secret to environment variable
2. Move TMDB API key to environment variable
3. Delete duplicate JWT classes (`JwtUtil.java`, `JwtAuthFilter.java`)
4. Revoke and rotate TMDB API key

---

### Phase 2: Stability & Resilience (P2) - 10 hours
🟡 **Required for MVP**

1. Add HikariCP connection pooling configuration
2. Implement Circuit Breaker for AI service (Resilience4j)
3. Add database migrations (Flyway)
4. Add Bean Validation for ratings (0.5-5.0 range)
5. Add RestTemplate timeouts (5s connect, 10s read)

---

### Phase 3: Code Quality & Performance (P3) - 17.5 hours
🟢 **Recommended for Maintainability**

1. Refactor `get_recommendations()` into separate functions
2. Modularize `train.py` (split into data/, models/, utils/)
3. Optimize genre query (add database index)
4. Fix onboarding ratings integration
5. Add full-text search on movie titles

---

### Phase 4: Testing & Documentation (P4) - 36 hours
📚 **Required for Team Collaboration**

1. Add backend integration tests (24 tests, 12h)
2. Add frontend component tests (12 tests, 8h)
3. Add AI service unit tests (11 tests, 6h)
4. Fix README.md errors (2h)
5. Create missing docs (ARCHITECTURE, CONFIGURATION, DEPLOYMENT) (8h)

---

## 📊 Risk Matrix

### Probability vs. Impact

```
HIGH    │                 │ FZ-H02 (JWT)  │ FZ-H05 (AI)   │
        │                 │ FZ-H01 (Dup)  │               │
        │                 │               │               │
MEDIUM  │                 │ FZ-H03 (TMDB) │ FZ-M03 (Migrate)│
        │                 │ FZ-H04 (Pool) │ FZ-M04 (Query)│
        │                 │ FZ-M05 (Timeout)│             │
LOW     │ FZ-L01-05       │ FZ-M01 (God)  │               │
        │ (Low priority)  │ FZ-M02 (Train)│               │
        │                 │ FZ-M06 (Onboard)│             │
        └─────────────────┴───────────────┴───────────────┘
           LOW              MEDIUM           HIGH
                        IMPACT
```

**Legend**:
- 🔴 **Critical Risk**: Immediate action required (upper-right quadrant)
- 🟡 **Moderate Risk**: Address in next sprint (middle region)
- 🟢 **Low Risk**: Defer to backlog (lower-left quadrant)

---

## 🎯 Sprint Planning

### Sprint 1: Security & Documentation (1 week)
**Goal**: Make system production-ready

- [ ] Fix all 🔴 HIGH security issues (3.5h)
- [ ] Fix README.md critical errors (2h)
- [ ] Add Swagger/OpenAPI documentation (2h)
- [ ] Create ARCHITECTURE.md (3h)
- [ ] Add database migrations (4h)

**Total Effort**: 14.5 hours (2 developer-days)

---

### Sprint 2: Testing Foundation (1 week)
**Goal**: Achieve 50% test coverage

- [ ] Add backend authentication tests (8 tests, 4h)
- [ ] Add backend recommendation service tests (6 tests, 3h)
- [ ] Add frontend authentication tests (5 tests, 4h)
- [ ] Add AI service recommendation tests (6 tests, 3h)

**Total Effort**: 14 hours (2 developer-days)

---

### Sprint 3: Resilience & Performance (1 week)
**Goal**: Handle failures gracefully

- [ ] Implement Circuit Breaker (4h)
- [ ] Add RestTemplate timeouts (30m)
- [ ] Optimize genre query (2h)
- [ ] Add Redis caching for recommendations (4h)
- [ ] Configure connection pooling (1h)

**Total Effort**: 11.5 hours (1.5 developer-days)

---

### Sprint 4: Code Quality (1 week)
**Goal**: Reduce technical debt

- [ ] Refactor AI service God function (3h)
- [ ] Modularize train.py (6h)
- [ ] Fix onboarding ratings (2h)
- [ ] Add backend business logic tests (10 tests, 5h)
- [ ] Add logging framework (2h)

**Total Effort**: 18 hours (2.5 developer-days)

---

## 📋 Compliance & Standards

### Security Standards
- [ ] OWASP Top 10 (2021) - **40% compliant**
  - ❌ A02: Cryptographic Failures (hardcoded secrets)
  - ✅ A01: Broken Access Control (JWT authentication)
  - ❌ A04: Insecure Design (no circuit breaker)
  - ❌ A05: Security Misconfiguration (CORS allows all)
  - ❌ A07: Identification and Authentication Failures (no rate limiting)

### Code Quality Standards
- [ ] SonarQube Quality Gate - **Not configured**
- [ ] ESLint (Frontend) - **Configured** (eslint.config.mjs)
- [ ] Checkstyle (Backend) - **Not configured**
- [ ] Flake8 (AI Service) - **Not configured**

### Testing Standards
- [ ] Minimum 80% coverage - **Currently: 2%** 🔴
- [ ] Unit tests for all services - **0/3 services** 🔴
- [ ] Integration tests - **0 tests** 🔴

---

## 🔄 Change Log

### 2025-01-21: Initial Analysis
- Completed 10-phase brownfield discovery
- Identified 17 fragile zones
- Cataloged 33 technical debt items
- Recommended 67 hours of remediation work

---

## 📞 Contact & Resources

### Team
- **Developer**: Nguyễn Thị Hồng Trọng
- **Course**: CT255H - Business Intelligence Applications
- **Instructor**: [Add instructor name]

### Repository
- **GitHub**: https://github.com/ngthtrong/CT255H-NexConflict

### Documentation
- **Analysis Reports**: `.github-copilot/workspace/analysis/`
  - 01-stack.md
  - 02-module-map.md
  - 03-business-logic.md
  - 04-fragile-zones.md
  - 05-test-coverage.md
  - 06-api-surface.md
  - 07-drift-report.md

---

## 🎓 Academic Assessment

### Project Strengths ✅
1. Implements real ML algorithms (SVD, cosine similarity)
2. Full-stack architecture with clear separation of concerns
3. Uses modern tech stack (Next.js 16, Spring Boot 3.4, FastAPI)
4. Integrates external APIs (TMDB)
5. Implements advanced features (onboarding, genome-based filtering)

### Areas for Improvement 🔧
1. Test coverage is critically low (~2%)
2. Documentation has significant inaccuracies (30% accuracy)
3. Security vulnerabilities (hardcoded secrets)
4. No database migrations (production risk)
5. Missing architectural documentation

### Grade Impact
- **Technical Implementation**: A- (strong algorithm implementation)
- **Code Quality**: B (moderate complexity, some God functions)
- **Testing**: D (minimal coverage)
- **Documentation**: C (incomplete and inaccurate)
- **Security**: C (major vulnerabilities)

**Overall Estimated Grade**: **B** (70-79%)  
**With Remediation**: **A-** (85-89%)

---

## 🚀 Next Actions

### Immediate (This Week)
1. ✅ Fix README.md (tech stack, commands, file names)
2. ✅ Move secrets to environment variables
3. ✅ Delete duplicate JWT classes
4. ✅ Add database indexes

### Short-term (Next 2 Weeks)
1. ✅ Achieve 50% test coverage
2. ✅ Add Swagger API documentation
3. ✅ Implement Circuit Breaker
4. ✅ Create ARCHITECTURE.md

### Long-term (Next Month)
1. ✅ Refactor AI service God functions
2. ✅ Add Redis caching
3. ✅ Deploy to production with PostgreSQL
4. ✅ Add monitoring (Prometheus + Grafana)

---

**Last Updated**: 2025-01-21  
**Analyst Signature**: AI Codebase Analyst Agent  
**Approval Status**: ⏳ Pending Review
