# Phase 6: API Surface Documentation

## 📡 Complete REST API Reference

This document catalogs all REST endpoints across **Backend** (Spring Boot) and **AI Service** (FastAPI).

---

## 🔧 Backend API (Spring Boot - Port 8080)

**Base URL**: `http://localhost:8080/api`

### Authentication Endpoints

#### POST /api/auth/login
**Description**: Authenticate user and receive JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors**:
- `401 UNAUTHORIZED`: Invalid credentials
- `400 BAD REQUEST`: Missing email/password

**Security**: Public endpoint (no authentication required)

---

#### POST /api/auth/register
**Description**: Create new user account

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "fullName": "John Doe"
}
```

**Response** (200 OK):
```json
{
  "message": "User registered successfully!"
}
```

**Errors**:
- `400 BAD REQUEST`: Email already in use
- `400 BAD REQUEST`: Missing required fields

**Security**: Public endpoint

---

### User Management Endpoints

#### GET /api/users/me
**Description**: Get current authenticated user's profile

**Request**: None (JWT in Authorization header)

**Response** (200 OK):
```json
{
  "id": 123,
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "ROLE_USER",
  "createdAt": "2024-01-15T10:30:00",
  "onboardingCompleted": true
}
```

**Errors**:
- `401 UNAUTHORIZED`: Missing/invalid JWT token
- `404 NOT FOUND`: User not found (shouldn't happen)

**Security**: Requires JWT authentication

---

#### PUT /api/users/me
**Description**: Update current user's profile

**Request**:
```json
{
  "fullName": "Jane Doe"
}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "email": "user@example.com",
  "fullName": "Jane Doe",
  "role": "ROLE_USER"
}
```

**Errors**:
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

---

### Movie Endpoints

#### GET /api/movies
**Description**: Get paginated list of movies with optional title filter

**Query Parameters**:
- `title` (optional): Filter by movie title (substring match)
- `page` (optional, default: 0): Page number (0-indexed)
- `size` (optional, default: 20): Page size

**Request Example**:
```
GET /api/movies?title=Matrix&page=0&size=10
```

**Response** (200 OK):
```json
{
  "content": [
    {
      "id": 2571,
      "title": "The Matrix (1999)",
      "genres": "Action|Sci-Fi|Thriller",
      "posterUrl": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
      "tmdbId": 603,
      "imdbId": "tt0133093"
    }
  ],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 10
  },
  "totalElements": 1,
  "totalPages": 1,
  "last": true
}
```

**Errors**: None (returns empty list if no matches)

**Security**: Public endpoint

---

#### GET /api/movies/{id}
**Description**: Get movie details by ID

**Request Example**:
```
GET /api/movies/1
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Toy Story (1995)",
  "genres": "Adventure|Animation|Children|Comedy|Fantasy",
  "posterUrl": "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  "tmdbId": 862,
  "imdbId": "tt0114709"
}
```

**Errors**:
- `404 NOT FOUND`: Movie ID does not exist

**Security**: Public endpoint

---

#### GET /api/movies/popular
**Description**: Get popular movies (first 20 movies in database)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Toy Story (1995)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Security**: Public endpoint

---

### Rating Endpoints

#### POST /api/ratings
**Description**: Add or update a movie rating

**Request**:
```json
{
  "movieId": 1,
  "rating": 4.5
}
```

**Response** (200 OK):
```json
{
  "id": 456,
  "movieId": 1,
  "rating": 4.5,
  "averageRating": 4.2,
  "totalRatings": 1523
}
```

**Errors**:
- `400 BAD REQUEST`: Rating not between 0.5 and 5.0
- `404 NOT FOUND`: Movie not found
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

**Business Rules**:
- Rating must be in range [0.5, 5.0]
- If user already rated this movie → update existing rating
- If first time rating → create new rating
- Returns updated aggregate statistics (avg rating, total count)

---

#### GET /api/ratings/movie/{movieId}/user
**Description**: Get current user's rating for a specific movie

**Request Example**:
```
GET /api/ratings/movie/1/user
```

**Response** (200 OK):
```json
{
  "id": 456,
  "movieId": 1,
  "rating": 4.5
}
```

**Errors**:
- `404 NOT FOUND`: User hasn't rated this movie
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

---

#### GET /api/ratings/movie/{movieId}
**Description**: Get aggregate rating statistics for a movie

**Request Example**:
```
GET /api/ratings/movie/1
```

**Response** (200 OK):
```json
{
  "movieId": 1,
  "averageRating": 4.2,
  "totalRatings": 1523
}
```

**Security**: Public endpoint

---

#### GET /api/ratings/user
**Description**: Get all ratings by current user

**Response** (200 OK):
```json
[
  {
    "id": 456,
    "movieId": 1,
    "rating": 4.5
  },
  {
    "id": 457,
    "movieId": 2,
    "rating": 3.0
  }
]
```

**Security**: Requires JWT authentication

---

#### DELETE /api/ratings/{ratingId}
**Description**: Delete a rating

**Request Example**:
```
DELETE /api/ratings/456
```

**Response** (200 OK):
```json
{
  "message": "Rating deleted"
}
```

**Errors**:
- `404 NOT FOUND`: Rating not found
- `403 FORBIDDEN`: Cannot delete other user's rating
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

---

### Watchlist Endpoints

#### GET /api/watchlist
**Description**: Get current user's watchlist

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Toy Story (1995)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Security**: Requires JWT authentication

**Sorting**: Movies ordered by `addedAt DESC` (most recent first)

---

#### POST /api/watchlist
**Description**: Add movie to watchlist

**Request**:
```json
{
  "movieId": 1
}
```

**Response** (200 OK):
```json
{
  "message": "Added to watchlist"
}
```

**Errors**:
- `409 CONFLICT`: Movie already in watchlist
- `404 NOT FOUND`: Movie not found
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

---

#### DELETE /api/watchlist/{movieId}
**Description**: Remove movie from watchlist

**Request Example**:
```
DELETE /api/watchlist/1
```

**Response** (200 OK):
```json
{
  "message": "Removed from watchlist"
}
```

**Errors**:
- `404 NOT FOUND`: Movie not in watchlist
- `401 UNAUTHORIZED`: Not authenticated

**Security**: Requires JWT authentication

---

#### GET /api/watchlist/check/{movieId}
**Description**: Check if movie is in user's watchlist

**Request Example**:
```
GET /api/watchlist/check/1
```

**Response** (200 OK):
```json
true
```

**Security**: Requires JWT authentication

---

### Recommendation Endpoints

#### GET /api/recommendations/for-you
**Description**: Get personalized recommendations for authenticated user

**Algorithm**:
1. If user has watchlist → Use watchlist-based content filtering (AI service)
2. Else → Use SVD collaborative filtering (AI service)
3. If AI service down → Return first 10 popular movies

**Response** (200 OK):
```json
[
  {
    "id": 318,
    "title": "The Shawshank Redemption (1994)",
    "genres": "Crime|Drama",
    "posterUrl": "..."
  },
  ...
]
```

**Security**: Requires JWT authentication

---

#### GET /api/recommendations/similar/{movieId}
**Description**: Get movies similar to a given movie (content-based filtering)

**Request Example**:
```
GET /api/recommendations/similar/1
```

**Response** (200 OK):
```json
[
  {
    "id": 3114,
    "title": "Toy Story 2 (1999)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Algorithm**: Uses AI service cosine similarity (genome scores or TF-IDF genres)

**Security**: Public endpoint

---

#### GET /api/recommendations/top-genres
**Description**: Get movies matching user's favorite genres (from onboarding)

**Response** (200 OK):
```json
[
  {
    "id": 260,
    "title": "Star Wars: Episode IV - A New Hope (1977)",
    "genres": "Action|Adventure|Sci-Fi",
    "posterUrl": "..."
  },
  ...
]
```

**Algorithm**:
1. Get user's preferred genres from `user_preferences` table
2. Scan all movies, filter by genre match
3. Return first 20 matches

**Performance Warning**: Full table scan! (see Fragile Zone FZ-M04)

**Security**: Requires JWT authentication

---

#### GET /api/recommendations/watch-again
**Description**: Get movies the user has already rated (rewatch suggestions)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Toy Story (1995)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Limit**: First 10 rated movies

**Security**: Requires JWT authentication

---

#### GET /api/recommendations/trending
**Description**: Get trending/popular movies (for guests and non-onboarded users)

**Query Parameters**:
- `limit` (optional, default: 20): Number of movies to return

**Request Example**:
```
GET /api/recommendations/trending?limit=50
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Toy Story (1995)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Algorithm**: Returns first N movies from database (MovieLens dataset is pre-sorted by popularity)

**Security**: Public endpoint

---

### Onboarding Endpoints

#### GET /api/onboarding/status
**Description**: Check if user has completed onboarding

**Response** (200 OK):
```json
{
  "onboardingCompleted": true
}
```

**Security**: Requires JWT authentication

---

#### GET /api/onboarding/genres
**Description**: Get list of all available genres for selection

**Response** (200 OK):
```json
[
  "Action", "Adventure", "Animation", "Children", "Comedy",
  "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
  "Horror", "IMAX", "Musical", "Mystery", "Romance",
  "Sci-Fi", "Thriller", "War", "Western"
]
```

**Security**: Requires JWT authentication

---

#### GET /api/onboarding/popular-movies
**Description**: Get popular movies for user to rate during onboarding

**Query Parameters**:
- `limit` (optional, default: 50): Number of movies to return

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Toy Story (1995)",
    "genres": "Adventure|Animation|Children|Comedy|Fantasy",
    "posterUrl": "..."
  },
  ...
]
```

**Security**: Requires JWT authentication

---

#### POST /api/onboarding/complete
**Description**: Complete onboarding by submitting genre preferences and movie ratings

**Request**:
```json
{
  "genres": ["Sci-Fi", "Action", "Thriller"],
  "ratings": [
    {"movieId": 1, "rating": 4.5},
    {"movieId": 2, "rating": 3.0},
    {"movieId": 260, "rating": 5.0},
    {"movieId": 318, "rating": 4.5},
    {"movieId": 527, "rating": 3.5}
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Onboarding completed successfully",
  "onboardingCompleted": true
}
```

**Errors**:
- `400 BAD REQUEST`: Less than 3 genres selected
- `400 BAD REQUEST`: Less than 5 movies rated
- `400 BAD REQUEST`: Invalid rating value (not in 0.5-5.0 range)

**Business Logic**:
1. Validates genre count (≥3) and rating count (≥5)
2. Saves genre preferences to `user_preferences` table
3. Saves ratings to both `user_onboarding_ratings` AND `ratings` tables
4. Sets `user.onboardingCompleted = true`

**Security**: Requires JWT authentication

---

#### GET /api/onboarding/my-preferences
**Description**: Get user's saved onboarding data (debugging endpoint)

**Response** (200 OK):
```json
{
  "genres": ["Sci-Fi", "Action", "Thriller"],
  "ratedMovies": [
    {
      "movieId": 1,
      "title": "Toy Story (1995)",
      "rating": 4.5
    },
    ...
  ],
  "onboardingCompleted": true
}
```

**Security**: Requires JWT authentication

---

### Admin Endpoints

#### POST /api/admin/posters/sync
**Description**: Manually trigger TMDB poster sync (fetch missing posters)

**Request**: None

**Response** (200 OK):
```json
{
  "message": "Syncing 300 posters in background..."
}
```

**Business Logic**: Fetches posters from TMDB API for movies with `tmdbId` but missing `posterUrl`

**Security**: Should require ADMIN role (currently open to all authenticated users - SECURITY ISSUE)

---

## 🤖 AI Service API (FastAPI - Port 8000)

**Base URL**: `http://localhost:8000`

### Health Check

#### GET /
**Description**: Service health check and model status

**Response** (200 OK):
```json
{
  "status": "AI Service Running",
  "models": {
    "svd": true,
    "content_based": true,
    "movies_loaded": 62423
  }
}
```

**Security**: Public endpoint

---

#### GET /health
**Description**: Model availability check

**Response** (200 OK):
```json
{
  "status": "healthy",
  "svd_model": true,
  "content_model": true
}
```

**Security**: Public endpoint

---

### Recommendation Endpoints

#### GET /recommendations/{user_id}
**Description**: Get personalized recommendations for a user (collaborative filtering)

**Path Parameters**:
- `user_id` (integer): User ID from backend database

**Query Parameters**:
- `limit` (optional, default: 10): Number of recommendations

**Request Example**:
```
GET /recommendations/123?limit=5
```

**Response** (200 OK):
```json
[318, 858, 50, 527, 2571]
```
*(Returns list of movie IDs)*

**Algorithm**:
1. If SVD model loaded and user has ratings:
   - Predict ratings for all unrated movies (first 1000)
   - Sort by predicted rating
   - Return top N movie IDs
2. Else (fallback):
   - Shuffle popular movies (deterministic based on user_id seed)
   - Return shuffled list

**Security**: Public endpoint (no authentication)

---

#### GET /similar/{movie_id}
**Description**: Get similar movies using content-based filtering

**Path Parameters**:
- `movie_id` (integer): Movie ID

**Query Parameters**:
- `limit` (optional, default: 5): Number of similar movies

**Request Example**:
```
GET /similar/1?limit=10
```

**Response** (200 OK):
```json
[3114, 2355, 588, 595, 364, 2294, 2321, 2683, 3754, 4886]
```
*(Returns list of similar movie IDs)*

**Algorithm**:
1. Get movie index from `movie_id_to_index` mapping
2. Look up pre-computed cosine similarity scores
3. Sort by similarity (descending)
4. Return top N movie IDs (excluding the query movie itself)

**Fallback**: If movie not found or matrix unavailable → Return `[movie_id+1, movie_id+2, ...]`

**Security**: Public endpoint

---

#### POST /recommendations/based-on-movies
**Description**: Get recommendations based on a list of movies (e.g., watchlist)

**Request Body**:
```json
[1, 2, 260, 318, 527]
```
*(JSON array of movie IDs)*

**Query Parameters**:
- `limit` (optional, default: 10): Number of recommendations

**Response** (200 OK):
```json
[2571, 858, 50, 296, 589, 2959, 2028, 4993, 4973, 7153]
```
*(Returns list of recommended movie IDs)*

**Algorithm**:
1. For each input movie, get its similar movies (using cosine similarity)
2. Aggregate similarity scores across all input movies (using MAX operator)
3. Exclude input movies from results
4. Sort by aggregated similarity score
5. Return top N movie IDs

**Use Case**: User has watchlist but no ratings (cold start problem)

**Security**: Public endpoint

---

## 🗄️ Database Schema (Reference)

### Tables and Relationships

```sql
-- users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- movies table
CREATE TABLE movie (
    id BIGINT PRIMARY KEY,  -- from MovieLens dataset
    title VARCHAR(500) NOT NULL,
    genres TEXT,
    poster_url VARCHAR(1000),
    tmdb_id BIGINT,
    imdb_id VARCHAR(50)
);

-- ratings table
CREATE TABLE ratings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    movie_id BIGINT NOT NULL,
    rating DOUBLE NOT NULL,  -- 0.5 to 5.0
    rated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    UNIQUE (user_id, movie_id)
);

-- watchlist table
CREATE TABLE watchlist (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    movie_id BIGINT NOT NULL,
    added_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    UNIQUE (user_id, movie_id)
);

-- user_preferences table (onboarding)
CREATE TABLE user_preference (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    genre_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- user_onboarding_ratings table
CREATE TABLE user_onboarding_rating (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    movie_id BIGINT NOT NULL,
    rating DOUBLE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movie(id)
);

-- watch_history table (currently unused)
CREATE TABLE watch_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    movie_id BIGINT NOT NULL,
    watched_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movie(id)
);
```

### Indexes

**Existing Indexes** (Auto-generated by JPA):
- `PRIMARY KEY` on all `id` columns
- `UNIQUE` index on `users.email`
- `UNIQUE` composite index on `ratings(user_id, movie_id)`
- `UNIQUE` composite index on `watchlist(user_id, movie_id)`

**Missing Indexes** (Performance Optimization):
```sql
-- Recommended indexes for query performance
CREATE INDEX idx_movie_genres ON movie(genres(100));  -- Full-text search
CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
CREATE INDEX idx_watchlist_user ON watchlist(user_id);
CREATE INDEX idx_user_pref_user ON user_preference(user_id);
CREATE INDEX idx_movie_tmdb ON movie(tmdb_id);  -- Poster sync queries
```

---

## 🔐 Security Summary

### Authentication
- **Method**: JWT (JSON Web Token)
- **Algorithm**: HMAC-SHA256 (HS256)
- **Token Location**: `Authorization: Bearer <token>` header
- **Expiration**: 24 hours
- **Secret**: Hardcoded in `application.properties` (🔴 CRITICAL ISSUE)

### Authorization
- **Role Model**: Single role (`ROLE_USER`) - no RBAC
- **Protected Endpoints**: Require `Authorization` header with valid JWT
- **Public Endpoints**:
  - `/api/auth/login`
  - `/api/auth/register`
  - `/api/movies/*` (all movie endpoints)
  - `/api/recommendations/trending`
  - `/api/recommendations/similar/{movieId}`
  - All AI service endpoints

### CORS
- **Backend**: Not explicitly configured (uses Spring Security defaults)
- **AI Service**: Allows all origins (`allow_origins=["*"]`) 🔴 SECURITY RISK

---

## 📊 API Usage Statistics

### Most Frequently Called Endpoints (Expected)
1. `GET /api/movies` - Movie browsing
2. `GET /api/recommendations/for-you` - Homepage personalized recs
3. `POST /api/ratings` - User engagement (rating movies)
4. `GET /api/watchlist` - Watchlist management
5. `GET /recommendations/{user_id}` - AI service (via backend proxy)

### Slowest Endpoints (Performance Bottlenecks)
1. `GET /api/recommendations/top-genres` - Full table scan (🟡 see FZ-M04)
2. `GET /recommendations/{user_id}` - Predicts 1000+ movies on-the-fly
3. `POST /api/onboarding/complete` - Multiple database writes
4. `POST /api/admin/posters/sync` - External API calls (TMDB)

---

## ⚠️ Deprecated/Unused Endpoints

**None identified** - All implemented endpoints appear to be in use.

---

## 🔄 Recommended Improvements

1. **API Versioning**: Add `/api/v1/` prefix for future compatibility
2. **Rate Limiting**: Implement request throttling (100 req/min per user)
3. **Pagination**: Add pagination to `/api/watchlist`, `/api/ratings/user`
4. **Caching**: Cache recommendation results (Redis, TTL: 1 hour)
5. **Error Standardization**: Consistent error response format
   ```json
   {
     "error": "MovieNotFound",
     "message": "Movie with ID 999 does not exist",
     "timestamp": "2024-01-15T10:30:00Z"
   }
   ```
6. **OpenAPI Documentation**: Add Swagger/OpenAPI spec generation

---

**Next Steps**: Proceed to Phase 7 (Documentation Drift Detection) to compare README claims with actual implementation.
