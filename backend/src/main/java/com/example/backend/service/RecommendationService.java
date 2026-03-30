package com.example.backend.service;

import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class RecommendationService {

    private final MovieRepository movieRepository;
    private final WatchlistRepository watchlistRepository;
    private final UserPreferenceRepository userPreferenceRepository;
    private final RatingRepository ratingRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final String AI_SERVICE_URL = "http://localhost:8000";

    public RecommendationService(
            MovieRepository movieRepository, 
            WatchlistRepository watchlistRepository,
            UserPreferenceRepository userPreferenceRepository,
            RatingRepository ratingRepository
    ) {
        this.movieRepository = movieRepository;
        this.watchlistRepository = watchlistRepository;
        this.userPreferenceRepository = userPreferenceRepository;
        this.ratingRepository = ratingRepository;
    }

    public List<Movie> getRecommendationsForUser(User user) {
        // Get user's watchlist movie IDs
        List<Watchlist> watchlist = watchlistRepository.findByUserOrderByAddedAtDesc(user);

        if (!watchlist.isEmpty()) {
            // User has watchlist - use content-based recommendations
            List<Long> watchlistMovieIds = watchlist.stream()
                    .map(w -> w.getMovie().getId())
                    .collect(Collectors.toList());

            System.out.println("Getting recommendations based on watchlist: " + watchlistMovieIds);

            try {
                // Call AI endpoint with watchlist movie IDs
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                HttpEntity<List<Long>> request = new HttpEntity<>(watchlistMovieIds, headers);

                List<?> movieIds = restTemplate.postForObject(
                        AI_SERVICE_URL + "/recommendations/based-on-movies?limit=10",
                        request,
                        List.class
                );

                if (movieIds != null && !movieIds.isEmpty()) {
                    List<Long> ids = movieIds.stream()
                            .map(id -> Long.valueOf(id.toString()))
                            .collect(Collectors.toList());
                    System.out.println("AI recommended movies: " + ids);
                    return movieRepository.findAllById(ids);
                }
            } catch (Exception e) {
                System.err.println("AI Service unavailable for watchlist-based: " + e.getMessage());
            }
        }

        // No watchlist - Use personalized recommendations based on user preferences and ratings
        return getPersonalizedRecommendations(user);
    }

    /**
     * Get personalized recommendations based on user's preferred genres and rated movies.
     * This is used for new users who are not in the pre-trained collaborative filtering models.
     */
    private List<Movie> getPersonalizedRecommendations(User user) {
        try {
            // Get user's preferred genres from onboarding
            List<UserPreference> preferences = userPreferenceRepository.findByUserId(user.getId());
            List<String> preferredGenres = preferences.stream()
                    .map(UserPreference::getGenreName)
                    .collect(Collectors.toList());

            // Get user's rated movies
            List<Rating> ratings = ratingRepository.findByUser(user);
            List<Map<String, Object>> ratedMovies = ratings.stream()
                    .map(r -> {
                        Map<String, Object> map = new HashMap<>();
                        map.put("movieId", r.getMovie().getId());
                        map.put("rating", r.getRating());
                        return map;
                    })
                    .collect(Collectors.toList());

            System.out.println("Getting personalized recommendations for user " + user.getId());
            System.out.println("Preferred genres: " + preferredGenres);
            System.out.println("Rated movies count: " + ratedMovies.size());

            // Build request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("preferredGenres", preferredGenres);
            requestBody.put("ratedMovies", ratedMovies);
            requestBody.put("limit", 10);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);

            List<?> movieIds = restTemplate.postForObject(
                    AI_SERVICE_URL + "/recommendations/personalized",
                    request,
                    List.class
            );

            if (movieIds != null && !movieIds.isEmpty()) {
                List<Long> ids = movieIds.stream()
                        .map(id -> Long.valueOf(id.toString()))
                        .collect(Collectors.toList());
                System.out.println("Personalized recommendations: " + ids);
                return movieRepository.findAllById(ids);
            }
        } catch (Exception e) {
            System.err.println("Personalized recommendations failed: " + e.getMessage());
            e.printStackTrace();
        }

        // Final fallback: Return newest popular movies
        System.out.println("Falling back to newest movies");
        return movieRepository.findAllByOrderByIdDesc().stream().limit(10).collect(Collectors.toList());
    }

    public List<Movie> getSimilarMovies(Long movieId) {
        try {
             List<?> movieIds = restTemplate.getForObject(AI_SERVICE_URL + "/similar/" + movieId, List.class);
             if (movieIds != null && !movieIds.isEmpty()) {
                 List<Long> ids = movieIds.stream()
                         .map(id -> Long.valueOf(id.toString()))
                         .collect(Collectors.toList());
                 return movieRepository.findAllById(ids);
            }
        } catch (Exception e) {
             System.err.println("AI Service unavailable: " + e.getMessage());
        }
        return new ArrayList<>();
    }
}
