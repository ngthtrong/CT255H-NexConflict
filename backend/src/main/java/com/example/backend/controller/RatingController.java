package com.example.backend.controller;

import com.example.backend.dto.RatingRequest;
import com.example.backend.dto.RatingResponse;
import com.example.backend.entity.Movie;
import com.example.backend.entity.Rating;
import com.example.backend.entity.User;
import com.example.backend.repository.MovieRepository;
import com.example.backend.repository.RatingRepository;
import com.example.backend.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/ratings")
public class RatingController {

    private final RatingRepository ratingRepository;
    private final UserRepository userRepository;
    private final MovieRepository movieRepository;

    public RatingController(RatingRepository ratingRepository, UserRepository userRepository, MovieRepository movieRepository) {
        this.ratingRepository = ratingRepository;
        this.userRepository = userRepository;
        this.movieRepository = movieRepository;
    }

    private User getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @PostMapping
    public ResponseEntity<?> rateMovie(@RequestBody RatingRequest request) {
        User user = getCurrentUser();
        Movie movie = movieRepository.findById(request.getMovieId())
                .orElseThrow(() -> new RuntimeException("Movie not found"));

        // Validate rating value
        if (request.getRating() < 0.5 || request.getRating() > 5.0) {
            return ResponseEntity.badRequest().body("Rating must be between 0.5 and 5.0");
        }

        // Check if user already rated this movie
        Rating rating = ratingRepository.findByUserAndMovie(user, movie)
                .orElse(new Rating(user, movie, request.getRating()));

        rating.setRating(request.getRating());
        Rating saved = ratingRepository.save(rating);

        RatingResponse response = new RatingResponse(saved.getId(), movie.getId(), saved.getRating());
        response.setAverageRating(ratingRepository.findAverageRatingByMovieId(movie.getId()));
        response.setTotalRatings(ratingRepository.countByMovieId(movie.getId()));

        return ResponseEntity.ok(response);
    }

    @GetMapping("/movie/{movieId}/user")
    public ResponseEntity<?> getUserRatingForMovie(@PathVariable Long movieId) {
        User user = getCurrentUser();
        Movie movie = movieRepository.findById(movieId)
                .orElseThrow(() -> new RuntimeException("Movie not found"));

        return ratingRepository.findByUserAndMovie(user, movie)
                .map(rating -> {
                    RatingResponse response = new RatingResponse(rating.getId(), movieId, rating.getRating());
                    return ResponseEntity.ok(response);
                })
                // Không xem là lỗi khi user chưa rating phim này; trả về rating = 0 để frontend hiển thị trạng thái chưa đánh giá.
                .orElse(ResponseEntity.ok(new RatingResponse(null, movieId, 0.0)));
    }

    @GetMapping("/movie/{movieId}")
    public ResponseEntity<?> getMovieRatings(@PathVariable Long movieId) {
        Double avgRating = ratingRepository.findAverageRatingByMovieId(movieId);
        Long totalRatings = ratingRepository.countByMovieId(movieId);

        RatingResponse response = new RatingResponse();
        response.setMovieId(movieId);
        response.setAverageRating(avgRating != null ? avgRating : 0.0);
        response.setTotalRatings(totalRatings != null ? totalRatings : 0L);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/user")
    public ResponseEntity<List<RatingResponse>> getUserRatings() {
        User user = getCurrentUser();
        List<Rating> ratings = ratingRepository.findByUser(user);

        List<RatingResponse> responses = ratings.stream()
                .map(r -> new RatingResponse(r.getId(), r.getMovie().getId(), r.getRating()))
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @DeleteMapping("/{ratingId}")
    public ResponseEntity<?> deleteRating(@PathVariable Long ratingId) {
        User user = getCurrentUser();
        Rating rating = ratingRepository.findById(ratingId)
                .orElseThrow(() -> new RuntimeException("Rating not found"));

        if (!rating.getUser().getId().equals(user.getId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Cannot delete other user's rating");
        }

        ratingRepository.delete(rating);
        return ResponseEntity.ok("Rating deleted");
    }
}
