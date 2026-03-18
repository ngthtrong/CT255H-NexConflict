package com.example.backend.service;

import com.example.backend.entity.Movie;
import com.example.backend.repository.MovieRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class RecommendationService {

    private final MovieRepository movieRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final String AI_SERVICE_URL = "http://localhost:8000";

    public RecommendationService(MovieRepository movieRepository) {
        this.movieRepository = movieRepository;
    }

    public List<Movie> getRecommendationsForUser(Long userId) {
        try {
            // Call AI Service: GET /ai-service/recommendations/{userId}
            List<?> movieIds = restTemplate.getForObject(AI_SERVICE_URL + "/recommendations/" + userId, List.class);
            if (movieIds != null && !movieIds.isEmpty()) {
                 List<Long> ids = movieIds.stream()
                         .map(id -> Long.valueOf(id.toString()))
                         .collect(Collectors.toList());
                 return movieRepository.findAllById(ids);
            }
        } catch (Exception e) {
            System.err.println("AI Service unavailable: " + e.getMessage());
        }
        // Fallback: Return popular movies (first 10)
        return movieRepository.findAll().stream().limit(10).collect(Collectors.toList());
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
