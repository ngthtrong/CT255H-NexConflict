package com.example.backend.controller;

import com.example.backend.entity.Movie;
import com.example.backend.entity.User;
import com.example.backend.repository.UserRepository;
import com.example.backend.service.RecommendationService;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

    private final RecommendationService recommendationService;
    private final UserRepository userRepository;

    public RecommendationController(RecommendationService recommendationService, UserRepository userRepository) {
        this.recommendationService = recommendationService;
        this.userRepository = userRepository;
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
}

