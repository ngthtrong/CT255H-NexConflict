package com.example.backend.service;

import com.example.backend.entity.Movie;
import com.example.backend.repository.MovieRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class TMDBService {

    private final MovieRepository movieRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    // TMDB API Key - set in application.properties or environment variable
    @Value("${tmdb.api.key:#{null}}")
    private String apiKey;

    private static final String TMDB_API_URL = "https://api.themoviedb.org/3";
    private static final String TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500";

    public TMDBService(MovieRepository movieRepository) {
        this.movieRepository = movieRepository;
    }

    public String getPosterUrl(Long tmdbId) {
        if (tmdbId == null) {
            return null;
        }

        // If no API key, return a placeholder based on tmdbId
        if (apiKey == null || apiKey.isEmpty()) {
            // Return a placeholder poster URL
            return "https://via.placeholder.com/500x750/1a1a1a/ff0000?text=Movie+" + tmdbId;
        }

        try {
            String url = TMDB_API_URL + "/movie/" + tmdbId + "?api_key=" + apiKey;
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            if (response != null && response.get("poster_path") != null) {
                return TMDB_IMAGE_URL + response.get("poster_path");
            }
        } catch (Exception e) {
            System.err.println("Failed to fetch poster from TMDB: " + e.getMessage());
        }

        return null;
    }

    public void updateMoviePoster(Long movieId) {
        Movie movie = movieRepository.findById(movieId).orElse(null);
        if (movie != null && movie.getTmdbId() != null && movie.getPosterUrl() == null) {
            String posterUrl = getPosterUrl(movie.getTmdbId());
            if (posterUrl != null) {
                movie.setPosterUrl(posterUrl);
                movieRepository.save(movie);
            }
        }
    }
}
