package com.example.backend.service;

import com.example.backend.entity.Movie;
import com.example.backend.repository.MovieRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
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

    public Map<String, Object> syncMissingPosters(int fetchBatchSize, int saveBatchSize, Integer maxMovies) {
        Instant startedAt = Instant.now();

        long totalCandidates = movieRepository.countByTmdbIdIsNotNullAndPosterUrlIsNull();
        long attempted = 0;
        long updated = 0;
        long failed = 0;
        long skippedNoPoster = 0;
        boolean hasTmdbApiKey = apiKey != null && !apiKey.isBlank();

        if (!hasTmdbApiKey) {
            Map<String, Object> stats = new LinkedHashMap<>();
            stats.put("startedAt", startedAt.toString());
            stats.put("durationMs", 0);
            stats.put("totalCandidates", totalCandidates);
            stats.put("attempted", 0);
            stats.put("updated", 0);
            stats.put("failed", 0);
            stats.put("skippedNoPoster", 0);
            stats.put("skippedNoApiKey", totalCandidates);
            stats.put("remaining", totalCandidates);
            stats.put("tmdbApiKeyConfigured", false);
            return stats;
        }

        List<Movie> moviesToSave = new ArrayList<>();

        while (true) {
            if (maxMovies != null && attempted >= maxMovies) {
                break;
            }

            Page<Movie> page = movieRepository.findByTmdbIdIsNotNullAndPosterUrlIsNull(PageRequest.of(0, fetchBatchSize));
            if (page.isEmpty()) {
                break;
            }

            for (Movie movie : page.getContent()) {
                if (maxMovies != null && attempted >= maxMovies) {
                    break;
                }

                attempted++;
                try {
                    String posterUrl = getPosterUrl(movie.getTmdbId());
                    if (posterUrl != null && !posterUrl.isBlank()) {
                        movie.setPosterUrl(posterUrl);
                        moviesToSave.add(movie);
                        updated++;

                        if (moviesToSave.size() >= saveBatchSize) {
                            movieRepository.saveAll(moviesToSave);
                            moviesToSave.clear();
                        }
                    } else {
                        skippedNoPoster++;
                    }
                } catch (Exception ex) {
                    failed++;
                    System.err.println("Failed to sync poster for movieId=" + movie.getId() + ": " + ex.getMessage());
                }
            }
        }

        if (!moviesToSave.isEmpty()) {
            movieRepository.saveAll(moviesToSave);
        }

        long durationMs = java.time.Duration.between(startedAt, Instant.now()).toMillis();

        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("startedAt", startedAt.toString());
        stats.put("durationMs", durationMs);
        stats.put("totalCandidates", totalCandidates);
        stats.put("attempted", attempted);
        stats.put("updated", updated);
        stats.put("failed", failed);
        stats.put("skippedNoPoster", skippedNoPoster);
        stats.put("skippedNoApiKey", 0);
        stats.put("remaining", movieRepository.countByTmdbIdIsNotNullAndPosterUrlIsNull());
        stats.put("tmdbApiKeyConfigured", true);

        return stats;
    }
}
