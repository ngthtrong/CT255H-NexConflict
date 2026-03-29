# Phase 5: Test Coverage Map

## 📊 Test Infrastructure Overview

**Current State**: ⚠️ **Minimal Test Coverage** across all services

| Service | Test Files | Test Frameworks | Coverage Estimate | Status |
|---------|-----------|----------------|-------------------|--------|
| **Backend** | 1 file | JUnit 5, Spring Boot Test | ~5% | 🔴 CRITICAL |
| **Frontend** | 0 files | None | 0% | 🔴 CRITICAL |
| **AI Service** | 0 files | None | 0% | 🔴 CRITICAL |

---

## 🔧 Backend Tests

### Test Files Found
```
backend/src/test/java/com/example/backend/
└── ApplicationTests.java  (13 LOC)
```

### Test Analysis: ApplicationTests.java

**Location**: `backend/src/test/java/com/example/backend/ApplicationTests.java`

**Code**:
```java
package com.example.backend;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class ApplicationTests {

    @Test
    void contextLoads() {
        // Empty test - only verifies Spring context can start
    }

}
```

**Test Type**: **Smoke Test** (Spring Context Initialization)

**What It Tests**:
- ✅ Spring Boot application can start
- ✅ All beans can be instantiated
- ✅ No circular dependency errors
- ✅ Configuration files are valid

**What It DOESN'T Test**:
- ❌ Authentication logic (JWT generation/validation)
- ❌ Database operations (CRUD)
- ❌ Business logic (recommendations, ratings)
- ❌ API endpoints (REST controllers)
- ❌ Security filters (JWT authentication filter)
- ❌ External service integration (AI service, TMDB API)
- ❌ Error handling
- ❌ Input validation

**Coverage Estimate**: **~5%** (only startup logic)

---

### Untested Business Logic (Backend)

#### 🔴 Critical: Authentication (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Login endpoint | `AuthController.java` | 49-71 | 🔴 HIGH | P1 |
| JWT generation | `JwtTokenProvider.java` | 30-41 | 🔴 HIGH | P1 |
| JWT validation | `JwtTokenProvider.java` | 48-64 | 🔴 HIGH | P1 |
| Password verification | `AuthService.java` | ~20 LOC | 🔴 HIGH | P1 |
| JWT filter chain | `JwtAuthenticationFilter.java` | ~60 LOC | 🔴 HIGH | P1 |

**Missing Test Scenarios**:
```java
// Test: Successful login with valid credentials
// Test: Login failure with invalid password
// Test: Login failure with non-existent email
// Test: JWT generation includes correct claims (email, expiry)
// Test: JWT validation rejects expired tokens
// Test: JWT validation rejects tampered tokens
// Test: JWT validation rejects tokens with wrong signature
// Test: Authentication filter extracts JWT from header
// Test: Authentication filter sets SecurityContext correctly
```

---

#### 🔴 Critical: Recommendation Service (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| AI service integration | `RecommendationService.java` | 31-81 | 🔴 HIGH | P1 |
| Watchlist-based recs | `RecommendationService.java` | 31-64 | 🟡 MEDIUM | P2 |
| Similar movies | `RecommendationService.java` | 83-96 | 🟡 MEDIUM | P2 |
| Fallback logic | `RecommendationService.java` | 76-80 | 🔴 HIGH | P1 |

**Missing Test Scenarios**:
```java
// Test: AI service returns recommendations → Backend forwards them
// Test: AI service down → Fallback to popular movies
// Test: AI service timeout → Fallback triggered
// Test: User with watchlist → Use watchlist-based endpoint
// Test: User without watchlist → Use SVD-based endpoint
// Test: Empty watchlist → Fallback to popular movies
// Test: AI service returns invalid data (null, empty) → Handled gracefully
```

---

#### 🟡 Medium: Rating CRUD (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Add rating | `RatingController.java` | ~30 LOC | 🟡 MEDIUM | P2 |
| Update rating | `RatingController.java` | ~20 LOC | 🟡 MEDIUM | P2 |
| Get user ratings | `RatingController.java` | ~15 LOC | 🟢 LOW | P3 |

**Missing Test Scenarios**:
```java
// Test: User rates a movie (first time) → Rating created
// Test: User re-rates a movie → Rating updated, not duplicated
// Test: Rating value validation (0.5 to 5.0) → Rejects invalid values
// Test: Rating for non-existent movie → Returns 404
// Test: Unauthenticated user → Returns 401
// Test: Get all ratings for a user → Returns correct list
// Test: Unique constraint enforced (user_id + movie_id)
```

---

#### 🟡 Medium: Watchlist Operations (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Add to watchlist | `WatchlistController.java` | ~25 LOC | 🟡 MEDIUM | P2 |
| Remove from watchlist | `WatchlistController.java` | ~20 LOC | 🟡 MEDIUM | P2 |
| Get watchlist | `WatchlistController.java` | ~15 LOC | 🟢 LOW | P3 |

**Missing Test Scenarios**:
```java
// Test: Add movie to watchlist → Movie added
// Test: Add duplicate movie → Returns error
// Test: Remove movie from watchlist → Movie removed
// Test: Remove non-existent movie → Returns 404
// Test: Get watchlist → Returns sorted by addedAt DESC
// Test: Unique constraint enforced
```

---

#### 🟡 Medium: Onboarding Flow (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Save genre preferences | `OnboardingController.java` | ~25 LOC | 🟡 MEDIUM | P2 |
| Save onboarding ratings | `OnboardingController.java` | ~30 LOC | 🟡 MEDIUM | P2 |

**Missing Test Scenarios**:
```java
// Test: User saves 3 genres → 3 UserPreference records created
// Test: User re-saves genres → Old preferences deleted, new ones created
// Test: User completes onboarding → onboardingCompleted = true
// Test: Onboarding ratings saved to user_onboarding_ratings table
// Test: User cannot complete onboarding without rating movies
```

---

#### 🟢 Low: Movie CRUD (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Get all movies | `MovieController.java` | ~10 LOC | 🟢 LOW | P3 |
| Get movie by ID | `MovieController.java` | ~10 LOC | 🟢 LOW | P3 |
| Search movies | `MovieService.java` | ~20 LOC | 🟡 MEDIUM | P2 |

**Missing Test Scenarios**:
```java
// Test: Get all movies → Returns paginated list
// Test: Search movies by title → Returns matching movies
// Test: Get movie by ID → Returns correct movie
// Test: Get non-existent movie → Returns 404
```

---

### Recommended Test Suite (Backend)

#### Priority 1: Authentication & Security (8 tests)
```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthenticationTests {
    
    @Test
    void loginWithValidCredentials_ReturnsJWT() { }
    
    @Test
    void loginWithInvalidPassword_Returns401() { }
    
    @Test
    void loginWithNonExistentEmail_Returns401() { }
    
    @Test
    void generateJWT_IncludesCorrectClaims() { }
    
    @Test
    void validateJWT_RejectsExpiredToken() { }
    
    @Test
    void validateJWT_RejectsTamperedToken() { }
    
    @Test
    void jwtFilter_ExtractsTokenFromHeader() { }
    
    @Test
    void protectedEndpoint_RequiresAuthentication() { }
}
```

#### Priority 2: Recommendation Service (6 tests)
```java
@SpringBootTest
class RecommendationServiceTests {
    
    @MockBean
    private RestTemplate restTemplate;
    
    @Test
    void getRecommendations_AIServiceUp_ReturnsMovies() { }
    
    @Test
    void getRecommendations_AIServiceDown_ReturnsFallback() { }
    
    @Test
    void getRecommendations_WithWatchlist_UsesWatchlistEndpoint() { }
    
    @Test
    void getRecommendations_EmptyWatchlist_UsesSVDEndpoint() { }
    
    @Test
    void getSimilarMovies_ValidMovieId_ReturnsResults() { }
    
    @Test
    void getSimilarMovies_AIServiceTimeout_ReturnsEmpty() { }
}
```

#### Priority 3: Business Logic (10 tests)
```java
@SpringBootTest
@AutoConfigureMockMvc
class BusinessLogicTests {
    
    // Rating Tests
    @Test
    void addRating_NewMovie_CreatesRating() { }
    
    @Test
    void addRating_ExistingMovie_UpdatesRating() { }
    
    @Test
    void addRating_InvalidValue_Returns400() { }
    
    // Watchlist Tests
    @Test
    void addToWatchlist_ValidMovie_Succeeds() { }
    
    @Test
    void addToWatchlist_Duplicate_Returns400() { }
    
    @Test
    void removeFromWatchlist_ExistingMovie_Succeeds() { }
    
    // Onboarding Tests
    @Test
    void saveGenres_ValidList_SavesPreferences() { }
    
    @Test
    void completeOnboarding_SetsFlag() { }
    
    @Test
    void onboardingRatings_SavedToCorrectTable() { }
    
    @Test
    void getMovies_Pagination_ReturnsCorrectPage() { }
}
```

**Total Recommended Tests**: 24 tests  
**Estimated Coverage**: 60-70%  
**Effort**: 12 hours

---

## 🎨 Frontend Tests

### Current State
```
frontend/app/
├── components/
├── lib/
└── *.tsx pages

NO test files found (0 *.test.tsx, *.spec.tsx files)
```

**Test Framework**: ❌ Not installed (no Jest, Vitest, or React Testing Library)

**Coverage**: **0%**

---

### Untested Components (Frontend)

#### 🔴 Critical: Authentication Flow (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| AuthContext provider | `lib/authContext.tsx` | ~100 LOC | 🔴 HIGH | P1 |
| Login page | `login/page.tsx` | ~80 LOC | 🔴 HIGH | P1 |
| Register page | `register/page.tsx` | ~80 LOC | 🔴 HIGH | P1 |
| API client (JWT injection) | `lib/api.ts` | 21 LOC | 🔴 HIGH | P1 |

**Missing Test Scenarios**:
```typescript
// Test: User logs in → JWT saved to localStorage
// Test: Invalid credentials → Error message shown
// Test: AuthContext provides user state to children
// Test: Protected route redirects to login if not authenticated
// Test: Logout clears localStorage and user state
// Test: API client adds JWT to Authorization header
// Test: API client handles 401 response (expired token)
```

---

#### 🟡 Medium: Homepage Logic (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| Conditional rendering (3 rows) | `page.tsx` | 93-196 | 🟡 MEDIUM | P2 |
| API data fetching | `page.tsx` | 28-72 | 🟡 MEDIUM | P2 |
| Error handling | `page.tsx` | 53-66 | 🟡 MEDIUM | P2 |

**Missing Test Scenarios**:
```typescript
// Test: Guest user → Shows "Trending" row only
// Test: Logged-in user (not onboarded) → Shows "Trending"
// Test: Onboarded user → Shows 3 personalized rows
// Test: API failure → Shows error message
// Test: Empty recommendations → Shows fallback message
// Test: Loading state → Shows spinner
```

---

#### 🟢 Low: UI Components (0% Coverage)

| Component | File | Lines | Risk | Test Priority |
|-----------|------|-------|------|---------------|
| MovieCard | `components/MovieCard.tsx` | ~50 LOC | 🟢 LOW | P3 |
| Navbar | `components/Navbar.tsx` | ~60 LOC | 🟢 LOW | P3 |

**Missing Test Scenarios**:
```typescript
// Test: MovieCard renders movie title and poster
// Test: MovieCard links to correct movie detail page
// Test: Navbar shows login button when not authenticated
// Test: Navbar shows user profile when authenticated
```

---

### Recommended Test Suite (Frontend)

#### Setup
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event
npm install --save-dev jest-environment-jsdom
```

**jest.config.js**:
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
};
```

#### Priority 1: Authentication (5 tests)
```typescript
// __tests__/lib/authContext.test.tsx
describe('AuthContext', () => {
  test('provides user state to children', () => { });
  test('login saves JWT to localStorage', () => { });
  test('logout clears user state', () => { });
});

// __tests__/lib/api.test.ts
describe('API Client', () => {
  test('adds JWT to Authorization header', () => { });
  test('handles 401 response (expired token)', () => { });
});
```

#### Priority 2: Homepage (4 tests)
```typescript
// __tests__/page.test.tsx
describe('Homepage', () => {
  test('guest user sees trending row', () => { });
  test('onboarded user sees 3 personalized rows', () => { });
  test('API failure shows error message', () => { });
  test('loading state shows spinner', () => { });
});
```

#### Priority 3: Components (3 tests)
```typescript
// __tests__/components/MovieCard.test.tsx
describe('MovieCard', () => {
  test('renders movie title and poster', () => { });
  test('links to movie detail page', () => { });
});

// __tests__/components/Navbar.test.tsx
describe('Navbar', () => {
  test('shows login button when not authenticated', () => { });
});
```

**Total Recommended Tests**: 12 tests  
**Estimated Coverage**: 50-60%  
**Effort**: 8 hours

---

## 🤖 AI Service Tests

### Current State
```
ai-service/
├── main.py (342 LOC)
├── train.py (331 LOC)
└── NO test files
```

**Test Framework**: ❌ Not installed (no pytest, unittest)

**Coverage**: **0%**

---

### Untested Logic (AI Service)

#### 🔴 Critical: Recommendation Algorithms (0% Coverage)

| Function | File | Lines | Risk | Test Priority |
|----------|------|-------|------|---------------|
| `get_recommendations()` | `main.py` | 196-238 | 🔴 HIGH | P1 |
| `get_similar_movies()` | `main.py` | 240-277 | 🔴 HIGH | P1 |
| `get_recommendations_based_on_movies()` | `main.py` | 279-329 | 🟡 MEDIUM | P2 |
| `load_models()` | `main.py` | 60-117 | 🔴 HIGH | P1 |

**Missing Test Scenarios**:
```python
# Test: SVD model loaded → Returns personalized recs
# Test: SVD model missing → Fallback to content-based
# Test: No ratings for user → Fallback to popular movies
# Test: get_similar_movies() returns correct movies
# Test: Cosine similarity matrix not loaded → Fallback
# Test: Watchlist-based recs aggregate similarity scores correctly
# Test: Model loading handles missing files gracefully
```

---

#### 🟡 Medium: Model Training (0% Coverage)

| Function | File | Lines | Risk | Test Priority |
|----------|------|-------|------|---------------|
| `train_svd_model()` | `train.py` | 69-138 | 🟡 MEDIUM | P2 |
| `build_content_model()` | `train.py` | 141-269 | 🟡 MEDIUM | P2 |
| `save_models()` | `train.py` | 272-304 | 🟢 LOW | P3 |

**Missing Test Scenarios**:
```python
# Test: SVD training with sample data → Model saved
# Test: Content model with genome data → Cosine matrix computed
# Test: Content model without genome → Fallback to TF-IDF
# Test: Model artifacts saved to correct paths
# Test: Cross-validation metrics within expected range
```

---

### Recommended Test Suite (AI Service)

#### Setup
```bash
cd ai-service
pip install pytest pytest-cov
```

**pytest.ini**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### Priority 1: Recommendation Logic (6 tests)
```python
# tests/test_recommendations.py
import pytest
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_recommendations_with_svd_model():
    response = client.get("/recommendations/1")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_recommendations_user_not_found():
    response = client.get("/recommendations/999999")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_similar_movies_valid_movie():
    response = client.get("/similar/1")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_similar_movies_invalid_movie():
    response = client.get("/similar/999999")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_watchlist_based_recommendations():
    response = client.post(
        "/recommendations/based-on-movies",
        json=[1, 2, 3]
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
```

#### Priority 2: Model Loading (3 tests)
```python
# tests/test_model_loading.py
import pytest
from main import load_models, fallback_train

def test_load_models_success(mocker):
    mocker.patch('os.path.exists', return_value=True)
    result = load_models()
    assert result is True

def test_load_models_failure_triggers_fallback(mocker):
    mocker.patch('os.path.exists', return_value=False)
    # Should trigger fallback_train()
    result = load_models()
    assert result is False

def test_fallback_train_creates_models():
    # Test fallback training logic
    pass
```

#### Priority 3: Model Training (2 tests)
```python
# tests/test_training.py
import pytest
from train import train_svd_model, build_content_model

def test_train_svd_model_with_sample_data():
    # Use small sample dataset
    result = train_svd_model()
    assert result is not None

def test_build_content_model_with_sample_data():
    result = build_content_model()
    assert result is not None
```

**Total Recommended Tests**: 11 tests  
**Estimated Coverage**: 40-50%  
**Effort**: 6 hours

---

## 📊 Overall Coverage Summary

| Service | Current Coverage | Recommended Coverage | Gap | Effort |
|---------|------------------|---------------------|-----|--------|
| **Backend** | ~5% | 60-70% | 55-65% | 12 hours |
| **Frontend** | 0% | 50-60% | 50-60% | 8 hours |
| **AI Service** | 0% | 40-50% | 40-50% | 6 hours |
| **TOTAL** | **~2%** | **50-60%** | **48-58%** | **26 hours** |

---

## 🎯 Test Coverage Roadmap

### Sprint 1: Critical Security & API Tests (12 hours)
- ✅ Backend authentication tests (8 tests)
- ✅ Backend recommendation service tests (6 tests)
- ✅ Frontend authentication tests (5 tests)

### Sprint 2: Business Logic Tests (10 hours)
- ✅ Backend rating/watchlist tests (10 tests)
- ✅ Frontend homepage tests (4 tests)
- ✅ AI service recommendation tests (6 tests)

### Sprint 3: Integration & Edge Cases (4 hours)
- ✅ AI service model loading tests (3 tests)
- ✅ Frontend component tests (3 tests)
- ✅ Backend movie CRUD tests (3 tests)

---

## 🔍 Critical Untested Business Logic

### Backend (Highest Risk)
1. **JWT Authentication Flow** - No validation of token generation/expiration
2. **AI Service Fallback Logic** - Fallback to popular movies never tested
3. **Rating Validation** - No tests for invalid rating values (e.g., 999.99)
4. **Onboarding Completion** - Flag setting logic untested
5. **Duplicate Rating/Watchlist** - Unique constraints not tested

### Frontend (High Risk)
1. **JWT Storage/Retrieval** - localStorage management untested
2. **Protected Route Guards** - Redirect logic untested
3. **API Error Handling** - 401/500 error responses untested
4. **Conditional Rendering** - 3-row logic untested

### AI Service (Medium Risk)
1. **Model Loading Fallback** - Pre-trained vs. on-the-fly training paths untested
2. **Similarity Calculation** - Cosine similarity math untested
3. **Empty Dataset Handling** - Behavior with no movies/ratings untested

---

## 🚀 Quick Wins (< 2 hours each)

1. **Backend**: Add JWT validation test (catch expired tokens)
2. **Backend**: Add rating validation test (reject invalid values)
3. **Frontend**: Add API client test (JWT injection)
4. **AI Service**: Add health endpoint test
5. **Backend**: Add recommendation fallback test (AI service down)

---

**Next Steps**: Proceed to Phase 6 (API Surface Documentation) to map all REST endpoints.
