package com.example.backend.controller;

import com.example.backend.dto.WatchlistRequest;
import com.example.backend.entity.Movie;
import com.example.backend.entity.User;
import com.example.backend.entity.Watchlist;
import com.example.backend.repository.MovieRepository;
import com.example.backend.repository.UserRepository;
import com.example.backend.repository.WatchlistRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/watchlist")
public class WatchlistController {

    private final WatchlistRepository watchlistRepository;
    private final UserRepository userRepository;
    private final MovieRepository movieRepository;

    public WatchlistController(WatchlistRepository watchlistRepository, UserRepository userRepository, MovieRepository movieRepository) {
        this.watchlistRepository = watchlistRepository;
        this.userRepository = userRepository;
        this.movieRepository = movieRepository;
    }

    private User getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String email = auth.getName();
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @GetMapping
    public ResponseEntity<List<Movie>> getWatchlist() {
        User user = getCurrentUser();
        List<Watchlist> watchlist = watchlistRepository.findByUserOrderByAddedAtDesc(user);

        List<Movie> movies = watchlist.stream()
                .map(Watchlist::getMovie)
                .collect(Collectors.toList());

        return ResponseEntity.ok(movies);
    }

    @PostMapping
    public ResponseEntity<?> addToWatchlist(@RequestBody WatchlistRequest request) {
        User user = getCurrentUser();
        Movie movie = movieRepository.findById(request.getMovieId())
                .orElseThrow(() -> new RuntimeException("Movie not found"));

        // Check if already in watchlist
        if (watchlistRepository.existsByUserAndMovie(user, movie)) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body("Movie already in watchlist");
        }

        Watchlist watchlist = new Watchlist(user, movie);
        watchlistRepository.save(watchlist);

        return ResponseEntity.ok("Added to watchlist");
    }

    @DeleteMapping("/{movieId}")
    @Transactional
    public ResponseEntity<?> removeFromWatchlist(@PathVariable Long movieId) {
        User user = getCurrentUser();
        Movie movie = movieRepository.findById(movieId)
                .orElseThrow(() -> new RuntimeException("Movie not found"));

        if (!watchlistRepository.existsByUserAndMovie(user, movie)) {
            return ResponseEntity.notFound().build();
        }

        watchlistRepository.deleteByUserAndMovie(user, movie);
        return ResponseEntity.ok("Removed from watchlist");
    }

    @GetMapping("/check/{movieId}")
    public ResponseEntity<Boolean> checkInWatchlist(@PathVariable Long movieId) {
        User user = getCurrentUser();
        Movie movie = movieRepository.findById(movieId)
                .orElseThrow(() -> new RuntimeException("Movie not found"));

        boolean inWatchlist = watchlistRepository.existsByUserAndMovie(user, movie);
        return ResponseEntity.ok(inWatchlist);
    }
}
