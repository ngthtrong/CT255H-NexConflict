package com.example.backend.service;

import com.example.backend.entity.Movie;
import com.example.backend.entity.User;
import com.example.backend.entity.Watchlist;
import com.example.backend.repository.MovieRepository;
import com.example.backend.repository.WatchlistRepository;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class RecommendationService {

    private final MovieRepository movieRepository;
    private final WatchlistRepository watchlistRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final String AI_SERVICE_URL = "http://localhost:8000";

    public RecommendationService(MovieRepository movieRepository, WatchlistRepository watchlistRepository) {
        this.movieRepository = movieRepository;
        this.watchlistRepository = watchlistRepository;
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
                // Call new AI endpoint with watchlist movie IDs
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

        // Fallback: Use SVD-based or popular movies
        try {
            List<?> movieIds = restTemplate.getForObject(AI_SERVICE_URL + "/recommendations/" + user.getId(), List.class);
            if (movieIds != null && !movieIds.isEmpty()) {
                 List<Long> ids = movieIds.stream()
                         .map(id -> Long.valueOf(id.toString()))
                         .collect(Collectors.toList());
                 return movieRepository.findAllById(ids);
            }
        } catch (Exception e) {
            System.err.println("AI Service unavailable: " + e.getMessage());
        }
        // Fallback: Return newest popular movies (first 10, sorted by ID desc for newest)
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
