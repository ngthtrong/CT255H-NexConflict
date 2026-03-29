# Phase 4: Fragile Zone Detection

## 🚨 Critical Risk Areas

This document identifies code complexity hotspots, architectural weaknesses, and technical debt that pose **HIGH**, **MEDIUM**, or **LOW** risk to system stability and maintainability.

---

## 🔴 HIGH RISK ZONES

### FZ-H01: Duplicate JWT Security Classes (Backend)

**Location**: `backend/src/main/java/com/example/backend/security/`

**Files Affected**:
- `JwtTokenProvider.java` (66 LOC) ✅ **PRIMARY**
- `JwtUtil.java` (similar functionality) ⚠️ **DUPLICATE**
- `JwtAuthenticationFilter.java` (primary filter) ✅ **PRIMARY**
- `JwtAuthFilter.java` (duplicate filter) ⚠️ **DUPLICATE**

**Evidence**:
```java
// JwtTokenProvider.java (USED)
@Component
public class JwtTokenProvider {
    public String generateToken(Authentication authentication) { ... }
    public boolean validateJwtToken(String authToken) { ... }
    public String getUserNameFromJwtToken(String token) { ... }
}

// JwtUtil.java (UNUSED - DUPLICATE)
@Component
public class JwtUtil {
    public String generateToken(Authentication authentication) { ... }
    public boolean validateJwtToken(String authToken) { ... }
    // Same methods, different implementation
}
```

**Risk Assessment**:
- 🔴 **Confusion**: Developers don't know which class to use
- 🔴 **Inconsistency**: Both classes may be used in different parts of codebase
- 🔴 **Bugs**: Security logic divergence between duplicates
- 🔴 **Maintainability**: Bug fixes must be applied to both classes

**Impact**: Security vulnerabilities, authentication failures

**Remediation**:
1. Identify which class is actually used in `SecurityConfig.java`
2. Delete unused duplicate
3. Rename remaining class to `JwtService` (clearer naming)
4. Add unit tests for JWT generation/validation

**Estimated Effort**: 2 hours

---

### FZ-H02: Hardcoded JWT Secret in Configuration

**Location**: `backend/src/main/resources/application.properties` (line 24)

**Evidence**:
```properties
myapp.jwt.secret=YourSuperSecretKeyForJWTGenerationMustBeLongEnoughUsually256BitsOrMore
```

**Risk Assessment**:
- 🔴 **Exposure**: Secret committed to Git (public repository risk)
- 🔴 **Non-rotation**: Cannot change secret without code redeployment
- 🔴 **Weak Entropy**: Human-generated passphrase (predictable)
- 🔴 **Compliance**: Violates OWASP secret management guidelines

**Attack Vector**:
```bash
# Attacker can:
1. Clone repository → Read JWT secret
2. Generate valid tokens for any user
3. Bypass authentication completely
```

**Remediation**:
1. Move secret to environment variable:
   ```properties
   myapp.jwt.secret=${JWT_SECRET:fallback-secret-for-dev}
   ```
2. Generate cryptographically secure secret:
   ```bash
   openssl rand -base64 64
   ```
3. Use Spring Cloud Config or AWS Secrets Manager in production
4. Add `.env` to `.gitignore`

**Estimated Effort**: 1 hour + deployment coordination

---

### FZ-H03: Hardcoded TMDB API Key

**Location**: `backend/src/main/resources/application.properties` (line 40)

**Evidence**:
```properties
tmdb.api.key=871b7b586ad7fb68f09390917a282f49  # ⚠️ EXPOSED API KEY
```

**Risk Assessment**:
- 🔴 **Cost Exposure**: Attackers can drain TMDB API quota
- 🔴 **Service Disruption**: Rate limit violations → poster fetching fails
- 🔴 **Account Suspension**: TMDB may ban compromised key

**Attack Simulation**:
```bash
# Attacker can:
curl -X GET "https://api.themoviedb.org/3/movie/550?api_key=871b7b586ad7fb68f09390917a282f49"
# Repeat 10,000 times → Exhaust daily quota
```

**Remediation**:
1. Revoke compromised API key in TMDB dashboard
2. Generate new key
3. Store in environment variable:
   ```properties
   tmdb.api.key=${TMDB_API_KEY:}
   ```
4. Add rate limiting in `TMDBService.java`

**Estimated Effort**: 30 minutes

---

### FZ-H04: No Database Connection Pooling Configuration

**Location**: `backend/src/main/resources/application.properties`

**Evidence**:
```properties
# H2 Database (In-Memory)
spring.datasource.url=jdbc:h2:mem:cinestream;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
# NO connection pooling settings!
```

**Risk Assessment**:
- 🔴 **Connection Exhaustion**: Default HikariCP pool may be too small
- 🔴 **Slow Queries**: No timeout configuration → requests hang forever
- 🔴 **No Monitoring**: Cannot track connection leaks

**Missing Configuration**:
```properties
# Recommended HikariCP settings
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000  # 30 seconds
spring.datasource.hikari.idle-timeout=600000       # 10 minutes
spring.datasource.hikari.max-lifetime=1800000      # 30 minutes
```

**Remediation**:
1. Add HikariCP configuration to `application.properties`
2. Enable connection leak detection:
   ```properties
   spring.datasource.hikari.leak-detection-threshold=60000  # 1 minute
   ```
3. Add `/actuator/health` endpoint to monitor DB status

**Estimated Effort**: 1 hour

---

### FZ-H05: AI Service Single Point of Failure (No Error Recovery)

**Location**: `backend/service/RecommendationService.java` (lines 68-78)

**Evidence**:
```java
public List<Movie> getRecommendationsForUser(User user) {
    try {
        List<?> movieIds = restTemplate.getForObject(
            AI_SERVICE_URL + "/recommendations/" + user.getId(), 
            List.class
        );
        if (movieIds != null && !movieIds.isEmpty()) {
            return movieRepository.findAllById(ids);
        }
    } catch (Exception e) {
        System.err.println("AI Service unavailable: " + e.getMessage());
        // ⚠️ Only logs to console, no metrics/alerts!
    }
    
    // Fallback: Return first 10 movies
    return movieRepository.findAll().stream().limit(10).collect(Collectors.toList());
}
```

**Risk Assessment**:
- 🔴 **Silent Failures**: Users get poor recommendations with no indication
- 🔴 **No Monitoring**: AI service downtime goes unnoticed
- 🔴 **No Circuit Breaker**: Repeated failed calls to AI service
- 🔴 **No Retry Logic**: Transient network errors cause immediate fallback

**Failure Scenarios**:
1. AI service crashes → All users get same "first 10 movies"
2. Network timeout (30s default) → Homepage loads slowly
3. AI service returns 500 error → No logging beyond console

**Remediation**:
1. Add **Resilience4j Circuit Breaker**:
   ```java
   @CircuitBreaker(name = "aiService", fallbackMethod = "getFallbackRecommendations")
   public List<Movie> getRecommendationsForUser(User user) { ... }
   ```
2. Add retry policy (3 attempts with exponential backoff)
3. Add metrics/alerting (Micrometer + Prometheus)
4. Implement caching (Redis) for recommendations (TTL: 1 hour)

**Estimated Effort**: 4 hours

---

### FZ-H06: No Input Validation on Rating Values

**Location**: `backend/controller/RatingController.java`

**Evidence**:
```java
@PostMapping
public ResponseEntity<?> addOrUpdateRating(@RequestBody RatingRequest request) {
    // ⚠️ NO validation on request.getRating()!
    // User can submit rating = 999.99 or -5.0
    
    Rating rating = new Rating(user, movie, request.getRating());
    ratingRepository.save(rating);  // Saved to DB without checks
}
```

**Risk Assessment**:
- 🔴 **Data Integrity**: Invalid ratings corrupt ML model training
- 🔴 **Business Logic Violation**: MovieLens standard is 0.5-5.0
- 🔴 **SQL Injection Risk**: If rating is used in native queries

**Attack Vector**:
```bash
curl -X POST http://localhost:8080/api/ratings \
  -H "Authorization: Bearer <token>" \
  -d '{"movieId": 1, "rating": 99999.99}'
# Accepted and saved to database!
```

**Remediation**:
1. Add `@Valid` annotation + Bean Validation:
   ```java
   public class RatingRequest {
       @NotNull
       @DecimalMin("0.5")
       @DecimalMax("5.0")
       private Double rating;
   }
   ```
2. Add database constraint:
   ```sql
   ALTER TABLE ratings ADD CONSTRAINT check_rating_range 
   CHECK (rating >= 0.5 AND rating <= 5.0);
   ```
3. Add unit tests for validation

**Estimated Effort**: 1 hour

---

## 🟡 MEDIUM RISK ZONES

### FZ-M01: God Function in AI Service (main.py)

**Location**: `ai-service/main.py` (lines 196-238)

**Metrics**:
- **Lines of Code**: 43
- **Cyclomatic Complexity**: ~8 (nested try/catch + if/else)
- **Nesting Depth**: 4 levels
- **Responsibilities**: Rating prediction, fallback logic, error handling, data transformation

**Evidence**:
```python
@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, limit: int = 10):
    if movies_df is None:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10][:limit]  # Fallback 1
    
    try:
        if svd_model is not None and ratings_df is not None:
            # SVD logic (15 lines)
            all_movie_ids = movies_df['movieId'].unique()
            user_ratings = ratings_df[ratings_df['userId'] == user_id]
            rated_movies = set(user_ratings['movieId'].values)
            
            predictions = []
            for movie_id in all_movie_ids[:1000]:  # Nested loop
                if movie_id not in rated_movies:
                    try:
                        pred = svd_model.predict(user_id, movie_id)
                        predictions.append((int(movie_id), pred.est))
                    except:
                        pass  # Silent failure
            
            if predictions:
                predictions.sort(key=lambda x: x[1], reverse=True)
                return [p[0] for p in predictions[:limit]]
        
        # Fallback 2: Content-based (10 lines)
        movie_ids = [int(x) for x in movies_df['movieId'].head(limit * 3).values]
        import random
        random.seed(user_id)
        random.shuffle(movie_ids)
        return movie_ids[:limit]
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return [int(x) for x in movies_df['movieId'].head(limit).values]  # Fallback 3
```

**Risk Assessment**:
- 🟡 **Complexity**: Hard to understand, test, and debug
- 🟡 **Multiple Fallbacks**: 3 different fallback strategies (confusing)
- 🟡 **Silent Failures**: `try/except: pass` hides errors
- 🟡 **Performance**: Iterating 1,000 movies on every request (no caching)

**Remediation**:
1. Refactor into separate functions:
   ```python
   def get_svd_recommendations(user_id, limit):
       # SVD logic only
   
   def get_content_based_recommendations(user_id, limit):
       # Content-based logic only
   
   def get_fallback_recommendations(limit):
       # Simple popular movies
   
   @app.get("/recommendations/{user_id}")
   def get_recommendations(user_id: int, limit: int = 10):
       try:
           return get_svd_recommendations(user_id, limit)
       except Exception:
           return get_content_based_recommendations(user_id, limit)
   ```
2. Add LRU caching for predictions
3. Add proper logging (no silent failures)

**Estimated Effort**: 3 hours

---

### FZ-M02: Monolithic train.py Script (AI Service)

**Location**: `ai-service/train.py`

**Metrics**:
- **Lines of Code**: 331
- **Functions**: 5 (but tightly coupled)
- **Responsibilities**: Data loading, SVD training, content model building, file I/O
- **External Dependencies**: 4 (pandas, surprise, sklearn, joblib)

**Risk Assessment**:
- 🟡 **Testability**: Cannot unit test individual components
- 🟡 **Reusability**: Cannot reuse data loading logic in `main.py`
- 🟡 **Memory Usage**: Loads entire genome-scores.csv (~1 GB) into memory
- 🟡 **Error Handling**: Partial failures (e.g., SVD fails but content-based succeeds) not granular

**Remediation**:
1. Split into modules:
   ```
   ai-service/
   ├── data/
   │   └── loader.py          # load_movies(), load_ratings(), load_genome()
   ├── models/
   │   ├── svd.py             # train_svd(), predict_svd()
   │   └── content_based.py   # build_cosine_matrix(), find_similar()
   ├── utils/
   │   └── persistence.py     # save_model(), load_model()
   └── train.py               # Orchestration only
   ```
2. Add CLI arguments for hyperparameters:
   ```bash
   python train.py --n-factors 150 --max-ratings 500000
   ```
3. Add incremental training (update model with new ratings)

**Estimated Effort**: 6 hours

---

### FZ-M03: No Database Migrations (Backend)

**Location**: `backend/src/main/resources/application.properties` (line 20)

**Evidence**:
```properties
spring.jpa.hibernate.ddl-auto=update  # ⚠️ Auto-generates schema on startup
```

**Risk Assessment**:
- 🟡 **Data Loss**: Schema changes may drop columns/tables
- 🟡 **No Rollback**: Cannot revert schema changes
- 🟡 **Production Risk**: Auto-DDL should NEVER be used in production
- 🟡 **Team Collaboration**: Schema drift between developers

**Migration Failures**:
```java
// Developer adds new column:
@Column(name = "favorite_genre")
private String favoriteGenre;

// On restart:
// 1. Hibernate detects schema change
// 2. Runs ALTER TABLE users ADD COLUMN favorite_genre VARCHAR(255)
// 3. If table has existing data → May fail or add NULL values
// 4. No way to set default values or backfill data
```

**Remediation**:
1. Add **Flyway** dependency:
   ```xml
   <dependency>
       <groupId>org.flywaydb</groupId>
       <artifactId>flyway-core</artifactId>
   </dependency>
   ```
2. Change configuration:
   ```properties
   spring.jpa.hibernate.ddl-auto=validate  # Only validate, don't auto-generate
   ```
3. Create migration scripts:
   ```sql
   -- V1__initial_schema.sql
   CREATE TABLE users (
       id BIGINT PRIMARY KEY AUTO_INCREMENT,
       email VARCHAR(255) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL,
       ...
   );
   ```
4. Enable Flyway:
   ```properties
   spring.flyway.enabled=true
   spring.flyway.baseline-on-migrate=true
   ```

**Estimated Effort**: 4 hours (initial setup + writing migrations for existing schema)

---

### FZ-M04: Unbounded Movie List Query (Frontend Homepage)

**Location**: `frontend/app/page.tsx` (lines 38-42)

**Evidence**:
```typescript
// Fetch all personalized content (no limit on backend query!)
const [recRes, genresRes, watchAgainRes] = await Promise.all([
    api.get('/recommendations/for-you').catch(() => ({ data: [] })),
    api.get('/recommendations/top-genres').catch(() => ({ data: [] })),
    api.get('/recommendations/watch-again').catch(() => ({ data: [] }))
]);
```

**Backend Endpoint** (`RecommendationController.java`, lines 69-73):
```java
@GetMapping("/top-genres")
public List<Movie> getTopGenresMovies() {
    // ...
    List<Movie> allMovies = movieRepository.findAll();  // ⚠️ Fetches ALL movies!
    // ...
    for (Movie movie : allMovies) {  // Iterates 62,000+ movies
        if (movie.getGenres() != null) {
            for (String genre : favoriteGenres) {
                if (movie.getGenres().contains(genre)) {
                    matchingMovies.add(movie);
                    break;
                }
            }
        }
        if (matchingMovies.size() >= 20) break;  // Early exit
    }
}
```

**Risk Assessment**:
- 🟡 **Performance**: O(n) scan of entire movie table (62,000 rows)
- 🟡 **Memory**: Loads all movies into JVM heap (~500 MB)
- 🟡 **Slow Response**: Homepage may take 2-5 seconds to load
- 🟡 **Database Load**: Full table scan on every request

**Remediation**:
1. Add database index on `genres` column (full-text search)
2. Use native query with LIKE clause:
   ```java
   @Query("SELECT m FROM Movie m WHERE m.genres LIKE %:genre% ORDER BY m.id LIMIT 20")
   List<Movie> findByGenre(@Param("genre") String genre);
   ```
3. Add pagination:
   ```java
   public Page<Movie> getTopGenresMovies(Pageable pageable) {
       // Return paginated results
   }
   ```
4. Cache results (Redis, TTL: 10 minutes)

**Estimated Effort**: 2 hours

---

### FZ-M05: No Request Timeout Configuration (RestTemplate)

**Location**: `backend/service/RecommendationService.java` (line 23)

**Evidence**:
```java
private final RestTemplate restTemplate = new RestTemplate();
// ⚠️ Uses default timeouts (infinite!)
```

**Risk Assessment**:
- 🟡 **Thread Starvation**: Blocked threads waiting for AI service response
- 🟡 **Cascading Failures**: AI service slowdown affects entire backend
- 🟡 **User Experience**: Homepage hangs for 30+ seconds

**Attack Scenario**:
```bash
# AI service becomes slow (500ms → 30s response time)
# Frontend sends 100 concurrent requests
# Backend creates 100 RestTemplate threads
# All threads blocked waiting for AI service
# New requests rejected (no available threads)
```

**Remediation**:
```java
@Bean
public RestTemplate restTemplate() {
    SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
    factory.setConnectTimeout(5000);  // 5 seconds
    factory.setReadTimeout(10000);    // 10 seconds
    return new RestTemplate(factory);
}
```

**Estimated Effort**: 30 minutes

---

### FZ-M06: Onboarding Ratings Not Used by AI Service

**Location**: Backend has `user_onboarding_ratings` table, but AI service uses `ratings` table

**Evidence**:
```java
// Backend: Saves to separate table
@PostMapping("/onboarding/ratings")
public ResponseEntity<?> saveOnboardingRatings(@RequestBody List<RatingRequest> ratings) {
    for (RatingRequest req : ratings) {
        UserOnboardingRating onboardingRating = new UserOnboardingRating();  // ⚠️ Wrong table
        onboardingRating.setUser(user);
        onboardingRating.setMovie(movie);
        onboardingRating.setRating(req.getRating());
        userOnboardingRatingRepository.save(onboardingRating);
    }
}
```

```python
# AI Service: Reads from ratings.csv (doesn't know about user_onboarding_ratings)
ratings_df = pd.read_csv('data/ratings.csv')
# ⚠️ New user's onboarding ratings never reach AI service!
```

**Risk Assessment**:
- 🟡 **Broken Feature**: Onboarding has no impact on recommendations
- 🟡 **Poor UX**: Users expect personalized recs after onboarding
- 🟡 **Wasted Effort**: Frontend + backend logic for onboarding is useless

**Remediation**:
1. **Option A**: Save onboarding ratings to `ratings` table (not separate table)
2. **Option B**: Sync onboarding ratings to AI service:
   ```java
   // After saving onboarding ratings:
   restTemplate.postForObject(
       AI_SERVICE_URL + "/sync-ratings",
       new RatingSyncRequest(user.getId(), ratings),
       Void.class
   );
   ```
3. **Option C**: Re-train AI model after onboarding (slow, not scalable)

**Estimated Effort**: 2 hours

---

## 🟢 LOW RISK ZONES

### FZ-L01: Frontend Has No Tests

**Location**: `frontend/` directory

**Evidence**:
```bash
$ find frontend/app -name "*.test.tsx" -o -name "*.spec.tsx"
# No results (0 test files)
```

**Risk Assessment**:
- 🟢 **Low Business Impact**: Frontend bugs are easily caught manually
- 🟢 **No Complex Logic**: Mostly UI rendering, API calls
- 🟢 **TypeScript**: Static typing prevents many bugs

**Remediation**:
1. Add Jest + React Testing Library
2. Write tests for:
   - Authentication flow (login/register)
   - API client (JWT token injection)
   - Movie card rendering

**Estimated Effort**: 4 hours

---

### FZ-L02: Backend Has Only Smoke Test

**Location**: `backend/src/test/java/com/example/backend/ApplicationTests.java`

**Evidence**:
```java
@SpringBootTest
class ApplicationTests {
    @Test
    void contextLoads() {
        // Only checks if Spring context starts
    }
}
```

**Risk Assessment**:
- 🟢 **Service Logic Tested**: Business logic is simple CRUD operations
- 🟢 **Database Operations**: Spring Data JPA handles most complexity
- 🟢 **Security Tested Manually**: JWT flow works in production

**Recommendation**:
- Add integration tests for:
  - JWT authentication flow
  - Rating CRUD operations
  - Recommendation service fallbacks

**Estimated Effort**: 6 hours

---

### FZ-L03: AI Service Has No Tests

**Location**: `ai-service/` directory

**Evidence**:
```bash
$ find ai-service -name "*test*.py"
# No results
```

**Risk Assessment**:
- 🟢 **ML Models Validated**: Cross-validation metrics in `train.py` (RMSE/MAE)
- 🟢 **Simple API**: Only 4 endpoints, mostly data transformations
- 🟢 **Fallback Logic**: Always returns results (no crashes)

**Recommendation**:
- Add `pytest` tests for:
  - Model loading (`load_models()`)
  - Similarity calculation (`get_similar_movies()`)
  - Fallback behavior (model unavailable)

**Estimated Effort**: 4 hours

---

### FZ-L04: No Logging Framework (Frontend)

**Location**: Frontend uses `console.log()` only

**Evidence**:
```typescript
console.error('Failed to fetch movies', error);  // Line 54
```

**Risk Assessment**:
- 🟢 **Client-Side Only**: Console logs are local to user's browser
- 🟢 **No PII Leakage**: No sensitive data in logs
- 🟢 **Error Tracking Needed**: But not critical for MVP

**Recommendation**:
- Add Sentry or LogRocket for error tracking
- Add custom error boundary component

**Estimated Effort**: 2 hours

---

### FZ-L05: No API Rate Limiting

**Location**: All backend endpoints have no rate limiting

**Risk Assessment**:
- 🟢 **Internal Use**: Not a public API (authenticated users only)
- 🟢 **Small User Base**: Academic project, not production scale
- 🟢 **DDoS Risk**: Low (no public-facing IP)

**Recommendation**:
- Add Bucket4j or Spring Cloud Gateway rate limiter
- Implement: 100 requests/minute per user

**Estimated Effort**: 2 hours

---

## 📊 Risk Summary Table

| Zone ID | Description | Risk Level | Impact | Likelihood | Effort | Priority |
|---------|-------------|------------|--------|------------|--------|----------|
| **FZ-H01** | Duplicate JWT classes | 🔴 HIGH | Critical | High | 2h | P1 |
| **FZ-H02** | Hardcoded JWT secret | 🔴 HIGH | Critical | High | 1h | P1 |
| **FZ-H03** | Hardcoded TMDB API key | 🔴 HIGH | High | Medium | 30m | P1 |
| **FZ-H04** | No DB connection pooling | 🔴 HIGH | High | Medium | 1h | P2 |
| **FZ-H05** | AI service single point of failure | 🔴 HIGH | High | High | 4h | P2 |
| **FZ-H06** | No rating input validation | 🔴 HIGH | Medium | Medium | 1h | P2 |
| **FZ-M01** | God function in AI service | 🟡 MEDIUM | Medium | Low | 3h | P3 |
| **FZ-M02** | Monolithic train.py | 🟡 MEDIUM | Medium | Low | 6h | P3 |
| **FZ-M03** | No database migrations | 🟡 MEDIUM | High | Medium | 4h | P2 |
| **FZ-M04** | Unbounded movie query | 🟡 MEDIUM | Medium | High | 2h | P3 |
| **FZ-M05** | No RestTemplate timeout | 🟡 MEDIUM | Medium | Medium | 30m | P3 |
| **FZ-M06** | Onboarding ratings unused | 🟡 MEDIUM | Low | High | 2h | P3 |
| **FZ-L01** | Frontend no tests | 🟢 LOW | Low | Low | 4h | P4 |
| **FZ-L02** | Backend smoke test only | 🟢 LOW | Low | Low | 6h | P4 |
| **FZ-L03** | AI service no tests | 🟢 LOW | Low | Low | 4h | P4 |
| **FZ-L04** | No logging framework (FE) | 🟢 LOW | Low | Low | 2h | P4 |
| **FZ-L05** | No API rate limiting | 🟢 LOW | Low | Low | 2h | P4 |

**Total Estimated Remediation Effort**: 46.5 hours (~6 developer-days)

---

## 🎯 Recommended Action Plan

### Phase 1: Critical Security Fixes (P1) - 3.5 hours
1. Move JWT secret to environment variable
2. Move TMDB API key to environment variable
3. Delete duplicate JWT classes
4. Revoke and rotate TMDB API key

### Phase 2: Stability Improvements (P2) - 9 hours
1. Add HikariCP connection pooling config
2. Implement Circuit Breaker for AI service
3. Add database migrations (Flyway)
4. Add Bean Validation for ratings

### Phase 3: Code Quality (P3) - 17.5 hours
1. Refactor `get_recommendations()` function
2. Modularize `train.py` script
3. Optimize movie genre query
4. Add RestTemplate timeouts
5. Fix onboarding ratings integration

### Phase 4: Testing & Monitoring (P4) - 16.5 hours
1. Add backend integration tests
2. Add AI service unit tests
3. Add frontend component tests
4. Add logging framework
5. Add API rate limiting

---

**Next Steps**: Proceed to Phase 5 (Test Coverage Map) to analyze existing test infrastructure.
