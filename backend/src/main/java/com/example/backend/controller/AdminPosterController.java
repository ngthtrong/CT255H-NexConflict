package com.example.backend.controller;

import com.example.backend.service.TMDBService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/posters")
public class AdminPosterController {

    private final TMDBService tmdbService;

    public AdminPosterController(TMDBService tmdbService) {
        this.tmdbService = tmdbService;
    }

    @PostMapping("/sync")
    public ResponseEntity<Map<String, Object>> syncPosters(
            @RequestParam(defaultValue = "100") int fetchBatchSize,
            @RequestParam(defaultValue = "100") int saveBatchSize,
            @RequestParam(required = false) Integer maxMovies
    ) {
        if (fetchBatchSize <= 0 || saveBatchSize <= 0) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "fetchBatchSize and saveBatchSize must be greater than 0"
            ));
        }

        if (maxMovies != null && maxMovies <= 0) {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "maxMovies must be greater than 0 when provided"
            ));
        }

        Map<String, Object> result = tmdbService.syncMissingPosters(fetchBatchSize, saveBatchSize, maxMovies);
        return ResponseEntity.ok(result);
    }
}
