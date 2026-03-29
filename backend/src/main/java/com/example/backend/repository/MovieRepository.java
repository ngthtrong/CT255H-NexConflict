package com.example.backend.repository;

import com.example.backend.entity.Movie;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MovieRepository extends JpaRepository<Movie, Long> {
    Page<Movie> findByTitleContainingIgnoreCase(String title, Pageable pageable);
    List<Movie> findByGenresContainingIgnoreCase(String genre);
    Page<Movie> findByTmdbIdIsNotNullAndPosterUrlIsNull(Pageable pageable);
    long countByTmdbIdIsNotNullAndPosterUrlIsNull();
    
    // Get newest movies first (higher ID = newer movie in MovieLens dataset)
    List<Movie> findAllByOrderByIdDesc();
    
    // Get movies sorted by number of ratings (most popular first)
    @Query("SELECT m FROM Movie m LEFT JOIN Rating r ON m.id = r.movie.id " +
           "GROUP BY m.id ORDER BY COUNT(r) DESC")
    List<Movie> findMostPopularMovies(Pageable pageable);
    
    // Find all movies ordered by ID desc with pagination
    Page<Movie> findAllByOrderByIdDesc(Pageable pageable);
}

