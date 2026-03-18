package com.example.backend.service;

import com.example.backend.entity.Movie;
import com.example.backend.repository.MovieRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class MovieService {
    private final MovieRepository movieRepository;

    public MovieService(MovieRepository movieRepository) {
        this.movieRepository = movieRepository;
    }

    public Page<Movie> getAllMovies(String title, Pageable pageable) {
        if (title != null && !title.isEmpty()) {
            return movieRepository.findByTitleContainingIgnoreCase(title, pageable);
        }
        return movieRepository.findAll(pageable);
    }

    public Optional<Movie> getMovieById(Long id) {
        return movieRepository.findById(id);
    }

    public List<Movie> getPopularMovies() {
        // Placeholder: Return first 20 movies
        return movieRepository.findAll(Pageable.ofSize(20)).getContent();
    }
}

