package com.example.backend.controller;

import com.example.backend.entity.Movie;
import com.example.backend.entity.Rating;
import com.example.backend.entity.User;
import com.example.backend.entity.UserPreference;
import com.example.backend.repository.MovieRepository;
import com.example.backend.repository.RatingRepository;
import com.example.backend.repository.UserPreferenceRepository;
import com.example.backend.repository.UserRepository;
import com.example.backend.service.RecommendationService;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

    private final RecommendationService recommendationService;
    private final UserRepository userRepository;
    private final UserPreferenceRepository userPreferenceRepository;
    private final RatingRepository ratingRepository;
    private final MovieRepository movieRepository;

    public RecommendationController(
            RecommendationService recommendationService,
            UserRepository userRepository,
            UserPreferenceRepository userPreferenceRepository,
            RatingRepository ratingRepository,
            MovieRepository movieRepository
    ) {
        this.recommendationService = recommendationService;
        this.userRepository = userRepository;
        this.userPreferenceRepository = userPreferenceRepository;
        this.ratingRepository = ratingRepository;
        this.movieRepository = movieRepository;
    }

    @GetMapping("/for-you")
    public List<Movie> getRecommendationsForUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        User user = userRepository.findByEmail(email).orElseThrow(() -> new RuntimeException("User not found"));

        return recommendationService.getRecommendationsForUser(user);
    }

    @GetMapping("/similar/{movieId}")
    public List<Movie> getSimilarMovies(@PathVariable Long movieId) {
        return recommendationService.getSimilarMovies(movieId);
    }

    /**
     * Get movies from user's preferred genres (Top Genres row on homepage)
     */
    @GetMapping("/top-genres")
    public List<Movie> getTopGenresMovies() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        User user = userRepository.findByEmail(email).orElseThrow(() -> new RuntimeException("User not found"));

        // Get user's preferred genres from onboarding
        List<UserPreference> prefs = userPreferenceRepository.findByUserId(user.getId());

        if (prefs.isEmpty()) {
            // No preferences, return empty or popular movies
            return movieRepository.findAll().stream().limit(10).collect(Collectors.toList());
        }

        List<String> favoriteGenres = prefs.stream()
                .map(UserPreference::getGenreName)
                .collect(Collectors.toList());

        // Find movies that match any of the user's favorite genres
        List<Movie> allMovies = movieRepository.findAll();
        List<Movie> matchingMovies = new ArrayList<>();

        for (Movie movie : allMovies) {
            if (movie.getGenres() != null) {
                for (String genre : favoriteGenres) {
                    if (movie.getGenres().contains(genre)) {
                        matchingMovies.add(movie);
                        break;
                    }
                }
            }
            if (matchingMovies.size() >= 20) break;
        }

        return matchingMovies;
    }

    /**
     * Get movies the user has rated (Watch Again row on homepage)
     */
    @GetMapping("/watch-again")
    public List<Movie> getWatchAgainMovies() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        User user = userRepository.findByEmail(email).orElseThrow(() -> new RuntimeException("User not found"));

        // Get movies the user has rated
        List<Rating> ratings = ratingRepository.findByUser(user);

        return ratings.stream()
                .map(Rating::getMovie)
                .limit(10)
                .collect(Collectors.toList());
    }

    /**
     * Get top trending/popular movies (for guests and non-onboarded users)
     * No authentication required
     */
    @GetMapping("/trending")
    public List<Movie> getTrendingMovies(@RequestParam(defaultValue = "20") int limit) {
        // Return first N movies (MovieLens sorts by popularity)
        return movieRepository.findAll().stream()
                .limit(limit)
                .collect(Collectors.toList());
    }
}

