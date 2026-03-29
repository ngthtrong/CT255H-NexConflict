package com.example.backend.controller;

import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/onboarding")
public class OnboardingController {

    private final UserRepository userRepository;
    private final MovieRepository movieRepository;
    private final UserPreferenceRepository userPreferenceRepository;
    private final UserOnboardingRatingRepository userOnboardingRatingRepository;
    private final RatingRepository ratingRepository;
    private final MoviePopularityRepository moviePopularityRepository;

    // All genres from MovieLens dataset
    private static final List<String> ALL_GENRES = Arrays.asList(
            "Action", "Adventure", "Animation", "Children", "Comedy",
            "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
            "Horror", "IMAX", "Musical", "Mystery", "Romance",
            "Sci-Fi", "Thriller", "War", "Western"
    );

    public OnboardingController(
            UserRepository userRepository,
            MovieRepository movieRepository,
            UserPreferenceRepository userPreferenceRepository,
            UserOnboardingRatingRepository userOnboardingRatingRepository,
            RatingRepository ratingRepository,
            MoviePopularityRepository moviePopularityRepository
    ) {
        this.userRepository = userRepository;
        this.movieRepository = movieRepository;
        this.userPreferenceRepository = userPreferenceRepository;
        this.userOnboardingRatingRepository = userOnboardingRatingRepository;
        this.ratingRepository = ratingRepository;
        this.moviePopularityRepository = moviePopularityRepository;
    }

    /**
     * Get onboarding status for current user
     */
    @GetMapping("/status")
    public ResponseEntity<?> getOnboardingStatus() {
        User user = getCurrentUser();
        Map<String, Object> response = new HashMap<>();
        response.put("onboardingCompleted", user.getOnboardingCompleted() != null && user.getOnboardingCompleted());
        return ResponseEntity.ok(response);
    }

    /**
     * Step 1: Get all available genres for user to select
     */
    @GetMapping("/genres")
    public ResponseEntity<?> getGenres() {
        return ResponseEntity.ok(ALL_GENRES);
    }

    /**
     * Step 2: Get popular movies for user to rate
     * Returns top N movies sorted by number of ratings (most popular first)
     * This ensures users see well-known movies they're likely to have watched
     */
    @GetMapping("/popular-movies")
    public ResponseEntity<?> getPopularMovies(@RequestParam(defaultValue = "50") int limit) {
        // Get top movie IDs from pre-calculated popularity data (from ratings.csv)
        List<Long> topMovieIds = moviePopularityRepository.findTopMovieIds(PageRequest.of(0, limit));
        
        if (topMovieIds.isEmpty()) {
            // Fallback to newest movies if popularity data not available
            return ResponseEntity.ok(movieRepository.findAllByOrderByIdDesc().stream()
                    .limit(limit)
                    .collect(Collectors.toList()));
        }
        
        // Fetch movie details and maintain popularity order
        List<Movie> movies = movieRepository.findAllById(topMovieIds);
        Map<Long, Movie> movieMap = movies.stream()
                .collect(Collectors.toMap(Movie::getId, m -> m));
        
        List<Movie> sortedMovies = topMovieIds.stream()
                .map(movieMap::get)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());

        return ResponseEntity.ok(sortedMovies);
    }

    /**
     * Complete onboarding with selected genres and rated movies
     */
    @PostMapping("/complete")
    public ResponseEntity<?> completeOnboarding(@RequestBody OnboardingRequest request) {
        User user = getCurrentUser();

        // Validate request
        if (request.getGenres() == null || request.getGenres().size() < 3) {
            return ResponseEntity.badRequest().body(Map.of("error", "Please select at least 3 genres"));
        }
        if (request.getRatings() == null || request.getRatings().size() < 5) {
            return ResponseEntity.badRequest().body(Map.of("error", "Please rate at least 5 movies"));
        }

        // Clear existing preferences for this user
        List<UserPreference> existingPrefs = userPreferenceRepository.findByUserId(user.getId());
        userPreferenceRepository.deleteAll(existingPrefs);

        // Save selected genres
        for (String genre : request.getGenres()) {
            if (ALL_GENRES.contains(genre)) {
                UserPreference pref = new UserPreference(user, genre);
                userPreferenceRepository.save(pref);
            }
        }

        // Clear existing onboarding ratings
        List<UserOnboardingRating> existingRatings = userOnboardingRatingRepository.findByUserId(user.getId());
        userOnboardingRatingRepository.deleteAll(existingRatings);

        // Save movie ratings
        for (MovieRatingDto rating : request.getRatings()) {
            Movie movie = movieRepository.findById(rating.getMovieId()).orElse(null);
            if (movie != null && rating.getRating() != null && rating.getRating() >= 0.5 && rating.getRating() <= 5.0) {
                // Save to onboarding ratings
                UserOnboardingRating onboardingRating = new UserOnboardingRating(user, movie, rating.getRating());
                userOnboardingRatingRepository.save(onboardingRating);

                // Also save to regular ratings table for SVD
                Rating regularRating = ratingRepository.findByUserAndMovie(user, movie).orElse(null);
                if (regularRating == null) {
                    regularRating = new Rating();
                    regularRating.setUser(user);
                    regularRating.setMovie(movie);
                }
                regularRating.setRating(rating.getRating());
                ratingRepository.save(regularRating);
            }
        }

        // Mark onboarding as completed
        user.setOnboardingCompleted(true);
        userRepository.save(user);

        return ResponseEntity.ok(Map.of(
                "message", "Onboarding completed successfully",
                "onboardingCompleted", true
        ));
    }

    /**
     * Get current user's preferences (for debugging/testing)
     */
    @GetMapping("/my-preferences")
    public ResponseEntity<?> getMyPreferences() {
        User user = getCurrentUser();

        List<UserPreference> prefs = userPreferenceRepository.findByUserId(user.getId());
        List<String> genres = prefs.stream()
                .map(UserPreference::getGenreName)
                .collect(Collectors.toList());

        List<UserOnboardingRating> ratings = userOnboardingRatingRepository.findByUserId(user.getId());
        List<Map<String, Object>> ratedMovies = ratings.stream()
                .map(r -> {
                    Map<String, Object> map = new HashMap<>();
                    map.put("movieId", r.getMovie().getId());
                    map.put("title", r.getMovie().getTitle());
                    map.put("rating", r.getRating());
                    return map;
                })
                .collect(Collectors.toList());

        return ResponseEntity.ok(Map.of(
                "genres", genres,
                "ratedMovies", ratedMovies,
                "onboardingCompleted", user.getOnboardingCompleted() != null && user.getOnboardingCompleted()
        ));
    }

    private User getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    // DTO classes
    public static class OnboardingRequest {
        private List<String> genres;
        private List<MovieRatingDto> ratings;

        public List<String> getGenres() {
            return genres;
        }

        public void setGenres(List<String> genres) {
            this.genres = genres;
        }

        public List<MovieRatingDto> getRatings() {
            return ratings;
        }

        public void setRatings(List<MovieRatingDto> ratings) {
            this.ratings = ratings;
        }
    }

    public static class MovieRatingDto {
        private Long movieId;
        private Double rating;

        public Long getMovieId() {
            return movieId;
        }

        public void setMovieId(Long movieId) {
            this.movieId = movieId;
        }

        public Double getRating() {
            return rating;
        }

        public void setRating(Double rating) {
            this.rating = rating;
        }
    }
}
