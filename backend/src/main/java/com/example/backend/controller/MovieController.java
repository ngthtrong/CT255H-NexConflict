package com.example.backend.controller;

import com.example.backend.entity.Movie;
import com.example.backend.service.MovieService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/movies")
public class MovieController {

    private final MovieService movieService;

    public MovieController(MovieService movieService) {
        this.movieService = movieService;
    }

    @GetMapping
    public Page<Movie> getAllMovies(@RequestParam(required = false) String title, Pageable pageable) {
        return movieService.getAllMovies(title, pageable);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Movie> getMovieById(@PathVariable Long id) {
        return movieService.getMovieById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/popular")
    public List<Movie> getPopularMovies() {
        return movieService.getPopularMovies();
    }
}

