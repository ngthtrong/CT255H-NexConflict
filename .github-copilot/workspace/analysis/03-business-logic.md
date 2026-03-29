# Phase 3: Business Logic Extraction

## 🎯 Core Business Domains

The system implements **movie recommendation** as its primary business capability, with supporting domains for authentication, ratings, and watchlists.

---

## 🤖 Domain 1: Recommendation Engine (AI Service)

### Algorithm 1: SVD-Based Collaborative Filtering

**Location**: `ai-service/train.py` (lines 69-138) + `ai-service/main.py` (lines 196-238)

**Mathematical Foundation**:
```python
# Matrix Factorization (Singular Value Decomposition)
# R ≈ U × Σ × V^T
# 
# Prediction formula:
# rating(u, i) = μ + b_u + b_i + q_i^T × p_u
#
# Where:
#   μ = global mean rating
#   b_u = user bias
#   b_i = item (movie) bias
#   q_i = latent factor vector for movie i (100 dimensions)
#   p_u = latent factor vector for user u (100 dimensions)
```

**Training Parameters** (from `train.py`):
```python
SVD_PARAMS = {
    'n_factors': 100,      # Number of latent dimensions
    'n_epochs': 20,        # Gradient descent iterations
    'lr_all': 0.005,       # Learning rate
    'reg_all': 0.02,       # L2 regularization (prevent overfitting)
    'random_state': 42,    # Reproducibility
}
```

**Training Process**:
1. Load `ratings.csv` (limited to 200,000 rows for performance)
2. 3-fold cross-validation to measure RMSE/MAE
3. Train on full dataset with validated parameters
4. Save model to `models/svd_model.pkl`

**Prediction Logic** (`main.py`, lines 206-225):
```python
def get_recommendations(user_id: int, limit: int = 10):
    # 1. Get movies user has already rated
    user_ratings = ratings_df[ratings_df['userId'] == user_id]
    rated_movies = set(user_ratings['movieId'].values)
    
    # 2. Predict rating for ALL unrated movies (first 1000 for speed)
    predictions = []
    for movie_id in all_movie_ids[:1000]:
        if movie_id not in rated_movies:
            pred = svd_model.predict(user_id, movie_id)
            predictions.append((movie_id, pred.est))  # pred.est = estimated rating
    
    # 3. Sort by predicted rating (descending), return top N
    predictions.sort(key=lambda x: x[1], reverse=True)
    return [movie_id for (movie_id, score) in predictions[:limit]]
```

**Business Rules**:
- ✅ Never recommend movies the user has already rated
- ✅ Limit scan to 1,000 movies (performance optimization)
- ✅ Return top 10 by predicted rating score

**Fallback Strategy**:
```python
# If SVD model unavailable → Use content-based filtering
# If content-based fails → Return popular movies (first N in dataset)
# Shuffle based on user_id seed for consistency
```

---

### Algorithm 2: Content-Based Filtering (Genome Scores + Cosine Similarity)

**Location**: `ai-service/train.py` (lines 141-269) + `ai-service/main.py` (lines 240-277)

**Data Source**:
- **Primary**: `genome-scores.csv` (1,128 semantic tags × ~13,000 movies)
- **Fallback**: `genres` field from `movies.csv` (TF-IDF vectorization)

**Genome Tags** (Examples):
```
- "dark comedy"
- "space travel"
- "twist ending"
- "strong female lead"
- "political intrigue"
... (1,128 total tags)
```

**Algorithm Flow**:
```python
# 1. Build Feature Matrix
genome_matrix = pivot(
    index='movieId',
    columns='tagId',
    values='relevance'  # 0.0 to 1.0 (how relevant the tag is)
)
# Result: (13,000 movies × 1,128 tags)

# 2. Compute Cosine Similarity
cosine_sim = cosine_similarity(genome_matrix[:5000], genome_matrix[:5000])
# Result: (5000 × 5000) matrix where:
#   cosine_sim[i][j] = similarity between movie_i and movie_j
#   Value range: 0 (completely different) to 1 (identical)

# 3. Find Similar Movies
def get_similar_movies(movie_id, limit=5):
    idx = movie_id_to_index[movie_id]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores.sort(key=lambda x: x[1], reverse=True)
    similar_indices = [i for (i, score) in sim_scores[1:limit+1]]  # Skip self
    return [index_to_movie_id[i] for i in similar_indices]
```

**Cosine Similarity Formula**:
```
cos(A, B) = (A · B) / (||A|| × ||B||)

Where:
  A, B = genome score vectors for two movies
  A · B = dot product (sum of element-wise products)
  ||A|| = L2 norm (Euclidean length of vector A)
```

**Business Rules**:
- ✅ Use genome scores if available (more accurate than genres)
- ✅ Fall back to TF-IDF genres if genome data missing
- ✅ Limit similarity matrix to 5,000 movies (memory constraint)
- ✅ Exclude the query movie itself from results

**Performance Characteristics**:
- **Training**: ~30-60 seconds (depends on genome data availability)
- **Inference**: O(1) lookup (pre-computed matrix)
- **Memory**: ~200 MB (5000×5000 float64 matrix)

---

### Algorithm 3: Hybrid Recommendation (Watchlist-Based)

**Location**: `ai-service/main.py` (lines 279-329) + `backend/RecommendationService.java` (lines 31-64)

**Scenario**: User has watchlist but no rating history (cold start problem)

**Algorithm**:
```python
def get_recommendations_based_on_movies(movie_ids: list[int], limit=10):
    # 1. For each movie in watchlist, find similar movies
    all_similar = {}
    for movie_id in movie_ids:
        idx = movie_id_to_index[movie_id]
        sim_scores = cosine_sim[idx]
        
        # 2. Aggregate similarity scores (use MAX if movie appears multiple times)
        for i, score in enumerate(sim_scores):
            similar_movie_id = index_to_movie_id[i]
            if similar_movie_id not in movie_ids:  # Don't recommend watchlist items
                all_similar[similar_movie_id] = max(
                    all_similar.get(similar_movie_id, 0), 
                    score
                )
    
    # 3. Sort by aggregated similarity score
    sorted_movies = sorted(all_similar.items(), key=lambda x: x[1], reverse=True)
    return [movie_id for (movie_id, score) in sorted_movies[:limit]]
```

**Business Rules**:
- ✅ Use **content-based filtering** (not SVD, no ratings yet)
- ✅ Aggregate similarity scores using **MAX** operator
- ✅ Never recommend movies already in watchlist
- ✅ Prioritize movies similar to MULTIPLE watchlist items (higher scores)

**Backend Integration** (`RecommendationService.java`):
```java
public List<Movie> getRecommendationsForUser(User user) {
    List<Watchlist> watchlist = watchlistRepository.findByUserOrderByAddedAtDesc(user);
    
    if (!watchlist.isEmpty()) {
        // Use watchlist-based recommendations
        List<Long> watchlistMovieIds = watchlist.stream()
            .map(w -> w.getMovie().getId())
            .collect(Collectors.toList());
        
        // Call AI service POST /recommendations/based-on-movies
        List<?> movieIds = restTemplate.postForObject(
            AI_SERVICE_URL + "/recommendations/based-on-movies?limit=10",
            new HttpEntity<>(watchlistMovieIds, headers),
            List.class
        );
        return movieRepository.findAllById(movieIds);
    }
    
    // Fallback: Use SVD-based recommendations
    return getSVDRecommendations(user.getId());
}
```

---

## 🔐 Domain 2: Authentication & Authorization

### Algorithm: Manual Password Verification + JWT Generation

**Location**: `backend/controller/AuthController.java` (lines 49-71)

**Authentication Flow**:
```java
@PostMapping("/login")
public ResponseEntity<?> authenticateUser(@RequestBody LoginRequest loginRequest) {
    // 1. Manual password verification (NO Spring Security AuthenticationManager)
    boolean isValid = authService.authUser(
        loginRequest.getEmail(), 
        loginRequest.getPassword()
    );
    
    if (!isValid) {
        return ResponseEntity.status(UNAUTHORIZED).body("Invalid email or password");
    }
    
    // 2. Create authentication token manually
    Authentication authentication = new UsernamePasswordAuthenticationToken(
        loginRequest.getEmail(),
        null,  // No credentials needed after verification
        List.of(new SimpleGrantedAuthority("ROLE_USER"))
    );
    
    // 3. Set security context
    SecurityContextHolder.getContext().setAuthentication(authentication);
    
    // 4. Generate JWT token
    String jwt = tokenProvider.generateToken(authentication);
    
    return ResponseEntity.ok(new JwtAuthenticationResponse(jwt));
}
```

**Password Verification** (`AuthService.java`):
```java
public boolean authUser(String email, String password) {
    Optional<User> userOpt = userRepository.findByEmail(email);
    if (userOpt.isEmpty()) {
        return false;
    }
    User user = userOpt.get();
    return passwordEncoder.matches(password, user.getPassword());  // BCrypt
}
```

**JWT Token Generation** (`JwtTokenProvider.java`):
```java
public String generateToken(Authentication authentication) {
    String username = authentication.getName();
    Date now = new Date();
    Date expiryDate = new Date(now.getTime() + jwtExpirationMs);  // 24 hours
    
    return Jwts.builder()
        .setSubject(username)
        .setIssuedAt(now)
        .setExpiration(expiryDate)
        .signWith(key(), SignatureAlgorithm.HS256)  // HMAC-SHA256
        .compact();
}

private Key key() {
    return Keys.hmacShaKeyFor(jwtSecret.getBytes());
}
```

**JWT Secret** (from `application.properties`):
```properties
myapp.jwt.secret=YourSuperSecretKeyForJWTGenerationMustBeLongEnoughUsually256BitsOrMore
myapp.jwt.expiration=86400000  # 24 hours in milliseconds
```

**⚠️ Security Issues**:
1. **Hardcoded Secret**: Should use environment variable or keystore
2. **No Token Refresh**: Users must re-login after 24 hours
3. **No Logout Mechanism**: JWTs remain valid until expiration
4. **No Rate Limiting**: Brute force attacks possible

**JWT Validation** (`JwtTokenProvider.java`, lines 48-64):
```java
public boolean validateJwtToken(String authToken) {
    try {
        Jwts.parserBuilder()
            .setSigningKey(key())
            .build()
            .parseClaimsJws(authToken);
        return true;
    } catch (SignatureException | MalformedJwtException | 
             ExpiredJwtException | UnsupportedJwtException | 
             IllegalArgumentException e) {
        logger.error("JWT validation error: {}", e.getMessage());
        return false;
    }
}
```

**Authorization Model**:
- **Single Role**: All users have `ROLE_USER` (no admin/moderator roles)
- **Endpoint Protection**: Most endpoints require authentication
- **Public Endpoints**: `/api/auth/login`, `/api/auth/register`, `/api/recommendations/trending`

---

## ⭐ Domain 3: Rating System

### Business Rules

**Location**: `backend/controller/RatingController.java` + `backend/entity/Rating.java`

**Rating Constraints**:
```java
@Entity
@Table(name = "ratings", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"user_id", "movie_id"})  // One rating per user-movie pair
})
public class Rating {
    @Column(nullable = false)
    private Double rating;  // Valid range: 0.5 to 5.0
    
    @Column(name = "rated_at")
    private LocalDateTime ratedAt;
    
    @PrePersist
    protected void onCreate() {
        ratedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        ratedAt = LocalDateTime.now();  // Update timestamp on re-rating
    }
}
```

**Business Logic**:
1. **Create or Update Rating**:
   ```java
   @PostMapping
   public ResponseEntity<?> addOrUpdateRating(@RequestBody RatingRequest request) {
       User user = getCurrentUser();
       Movie movie = movieRepository.findById(request.getMovieId())
           .orElseThrow(() -> new RuntimeException("Movie not found"));
       
       // Check if rating exists
       Rating existingRating = ratingRepository.findByUserAndMovie(user, movie);
       
       if (existingRating != null) {
           // Update existing rating
           existingRating.setRating(request.getRating());
           ratingRepository.save(existingRating);
       } else {
           // Create new rating
           Rating newRating = new Rating(user, movie, request.getRating());
           ratingRepository.save(newRating);
       }
       
       return ResponseEntity.ok("Rating saved");
   }
   ```

2. **Validation Rules**:
   - ✅ Rating must be between 0.5 and 5.0
   - ✅ Increment: 0.5 (half-star ratings)
   - ✅ User must be authenticated
   - ✅ Movie must exist in database

3. **Side Effects**:
   - ❌ No automatic AI model retraining (ratings not synced to AI service)
   - ❌ No real-time recommendation updates (pre-trained model only)

---

## 📋 Domain 4: Onboarding Flow

### Purpose
Capture user preferences to enable personalized recommendations for new users (cold start solution).

**Location**: `backend/controller/OnboardingController.java`

**Two-Step Process**:

#### Step 1: Genre Selection
```java
@PostMapping("/genres")
public ResponseEntity<?> saveGenrePreferences(@RequestBody List<String> genres) {
    User user = getCurrentUser();
    
    // Clear existing preferences
    List<UserPreference> existing = userPreferenceRepository.findByUserId(user.getId());
    userPreferenceRepository.deleteAll(existing);
    
    // Save new preferences
    for (String genre : genres) {
        UserPreference pref = new UserPreference();
        pref.setUser(user);
        pref.setGenreName(genre);
        userPreferenceRepository.save(pref);
    }
    
    return ResponseEntity.ok("Genres saved");
}
```

#### Step 2: Rate Sample Movies
```java
@PostMapping("/ratings")
public ResponseEntity<?> saveOnboardingRatings(@RequestBody List<RatingRequest> ratings) {
    User user = getCurrentUser();
    
    // Save onboarding ratings (separate table from regular ratings)
    for (RatingRequest req : ratings) {
        Movie movie = movieRepository.findById(req.getMovieId())
            .orElseThrow(() -> new RuntimeException("Movie not found"));
        
        UserOnboardingRating onboardingRating = new UserOnboardingRating();
        onboardingRating.setUser(user);
        onboardingRating.setMovie(movie);
        onboardingRating.setRating(req.getRating());
        
        userOnboardingRatingRepository.save(onboardingRating);
    }
    
    // Mark onboarding as completed
    user.setOnboardingCompleted(true);
    userRepository.save(user);
    
    return ResponseEntity.ok("Onboarding completed");
}
```

**Business Rules**:
1. **Genre Selection**:
   - User picks 3-5 favorite genres (e.g., Action, Sci-Fi, Drama)
   - Previous selections are overwritten (not appended)

2. **Sample Ratings**:
   - Frontend shows 10-20 popular movies
   - User rates at least 5 movies
   - Ratings stored in `user_onboarding_ratings` table (NOT `ratings` table)

3. **Completion Flag**:
   - `user.onboardingCompleted = true` enables personalized homepage
   - Onboarded users see 3 rows: "Recommended For You", "Top Genres", "Watch Again"
   - Non-onboarded users see only "Trending Movies"

**⚠️ Data Isolation Issue**:
- Onboarding ratings are NOT used for AI recommendations (separate table)
- AI service uses `ratings` table, which is empty for new users
- **Result**: Onboarding has minimal impact on recommendations until user rates more movies

---

## 📊 Domain 5: Watchlist Management

**Location**: `backend/controller/WatchlistController.java`

**Business Logic**:
```java
@PostMapping("/add")
public ResponseEntity<?> addToWatchlist(@RequestBody WatchlistRequest request) {
    User user = getCurrentUser();
    Movie movie = movieRepository.findById(request.getMovieId())
        .orElseThrow(() -> new RuntimeException("Movie not found"));
    
    // Check if already in watchlist
    if (watchlistRepository.findByUserAndMovie(user, movie).isPresent()) {
        return ResponseEntity.status(BAD_REQUEST).body("Already in watchlist");
    }
    
    // Add to watchlist
    Watchlist watchlist = new Watchlist(user, movie);
    watchlistRepository.save(watchlist);
    
    return ResponseEntity.ok("Added to watchlist");
}

@DeleteMapping("/{movieId}")
public ResponseEntity<?> removeFromWatchlist(@PathVariable Long movieId) {
    User user = getCurrentUser();
    Movie movie = movieRepository.findById(movieId)
        .orElseThrow(() -> new RuntimeException("Movie not found"));
    
    Watchlist watchlist = watchlistRepository.findByUserAndMovie(user, movie)
        .orElseThrow(() -> new RuntimeException("Not in watchlist"));
    
    watchlistRepository.delete(watchlist);
    
    return ResponseEntity.ok("Removed from watchlist");
}
```

**Business Rules**:
1. ✅ No duplicates (UNIQUE constraint on user_id + movie_id)
2. ✅ Watchlist used for content-based recommendations (if SVD unavailable)
3. ✅ Sorted by `added_at` DESC (most recent first)
4. ❌ No watchlist size limit
5. ❌ No "watched" status toggle (watchlist vs. watched history)

---

## 🎬 Domain 6: TMDB Poster Integration

**Location**: `backend/service/TMDBService.java` + `backend/controller/AdminPosterController.java`

**Business Logic**:
```java
public void syncPostersOnStartup() {
    if (!posterSyncOnStartup) return;  // Disabled by default in config
    
    // Find movies with tmdbId but missing posterUrl
    List<Movie> moviesNeedingPosters = movieRepository.findAll().stream()
        .filter(m -> m.getTmdbId() != null && m.getPosterUrl() == null)
        .limit(maxMovies)  // Config: poster.sync.max-movies=300
        .toList();
    
    // Fetch posters in batches
    for (int i = 0; i < moviesNeedingPosters.size(); i += fetchBatchSize) {
        List<Movie> batch = moviesNeedingPosters.subList(
            i, 
            Math.min(i + fetchBatchSize, moviesNeedingPosters.size())
        );
        
        for (Movie movie : batch) {
            try {
                String tmdbUrl = "https://api.themoviedb.org/3/movie/" + movie.getTmdbId();
                // ... fetch poster URL from TMDB API
                movie.setPosterUrl(posterPath);
            } catch (Exception e) {
                // Set placeholder if TMDB fails
                movie.setPosterUrl("/placeholder.jpg");
            }
        }
        
        movieRepository.saveAll(batch);
    }
}
```

**Business Rules**:
1. **Trigger**: Application startup (if `poster.sync.on-startup=true`)
2. **Rate Limiting**: Batch size = 100 (config: `poster.sync.fetch-batch-size`)
3. **Failure Handling**: Set placeholder URL if TMDB API fails
4. **Idempotency**: Only fetch for movies with `tmdbId` but missing `posterUrl`

**TMDB API Key** (from `application.properties`):
```properties
tmdb.api.key=871b7b586ad7fb68f09390917a282f49  # ⚠️ HARDCODED - SECURITY RISK
```

---

## 🔍 Validation Rules Summary

| Domain | Field | Validation | Location |
|--------|-------|------------|----------|
| **User** | email | @Column(unique=true) | User.java:15 |
| | password | BCrypt hashed | AuthController.java:82 |
| | fullName | No validation | User.java:20 |
| **Rating** | rating | 0.5 to 5.0 (implied) | Rating.java:25 |
| | user+movie | UNIQUE constraint | Rating.java:7-9 |
| **Watchlist** | user+movie | UNIQUE constraint | Watchlist.java:7-9 |
| **Movie** | title | NOT NULL | Movie.java:12 |
| | genres | TEXT (no limit) | Movie.java:15 |

**⚠️ Missing Validations**:
- No email format validation (regex)
- No password strength requirements (min length, special chars)
- No rating range validation (0.5-5.0 not enforced at DB level)
- No genre whitelist (any string accepted)

---

## 🧮 Complex Calculations

### 1. SVD Rating Prediction
**Complexity**: O(k) where k = n_factors (100)
```
rating = μ + b_u + b_i + Σ(q_i[k] × p_u[k]) for k in [1..100]
```

### 2. Cosine Similarity
**Complexity**: O(d) where d = number of features (1,128 genome tags)
```
similarity = (A · B) / (√(A · A) × √(B · B))
where A, B are 1,128-dimensional vectors
```

### 3. Recommendation Aggregation (Watchlist-Based)
**Complexity**: O(n × m) where n = watchlist size, m = similar movies per item
```
For each movie M in watchlist:
    For each similar movie S:
        aggregated_score[S] = max(aggregated_score[S], similarity(M, S))
```

---

## 🚦 State Machines

### User Onboarding State Machine
```
[New User] 
    → /api/auth/register
    → onboardingCompleted = FALSE
    
[Select Genres]
    → /api/onboarding/genres
    → user_preferences table updated
    
[Rate Sample Movies]
    → /api/onboarding/ratings
    → user_onboarding_ratings table updated
    → onboardingCompleted = TRUE
    
[Onboarded User]
    → Homepage shows personalized rows
    → /api/recommendations/for-you returns AI-based recs
```

### Recommendation Flow State Machine
```
[User Request: /api/recommendations/for-you]
    ↓
[Has Watchlist?]
    YES → POST /recommendations/based-on-movies (Content-Based)
    NO ↓
[AI Service Available?]
    YES → GET /recommendations/{userId} (SVD Collaborative Filtering)
    NO ↓
[Fallback]
    → Return first 10 movies from database (Popular Movies)
```

---

## 📈 Business Metrics (Potential)

**Currently NOT Implemented**:
- Click-through rate (CTR) on recommendations
- Conversion rate (watchlist → rated)
- Average session duration
- Recommendation diversity (genre spread)
- User engagement score

**Recommendation**: Add event tracking for:
- Recommendation impressions
- Recommendation clicks
- Movie detail page views
- Rating submissions
- Watchlist additions/removals

---

**Next Steps**: Proceed to Phase 4 (Fragile Zone Detection) to identify high-risk code areas.
