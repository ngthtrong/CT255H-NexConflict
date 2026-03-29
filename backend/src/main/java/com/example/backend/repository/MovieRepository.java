package com.example.backend.repository;

import com.example.backend.entity.Movie;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MovieRepository extends JpaRepository<Movie, Long> {
    Page<Movie> findByTitleContainingIgnoreCase(String title, Pageable pageable);
    List<Movie> findByGenresContainingIgnoreCase(String genre);
    Page<Movie> findByTmdbIdIsNotNullAndPosterUrlIsNull(Pageable pageable);
    long countByTmdbIdIsNotNullAndPosterUrlIsNull();
}

