package com.example.backend.repository;

import com.example.backend.entity.MoviePopularity;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MoviePopularityRepository extends JpaRepository<MoviePopularity, Long> {
    
    // Get movies sorted by rating count (most popular first)
    List<MoviePopularity> findAllByOrderByRatingCountDesc(Pageable pageable);
    
    // Get top N most popular movie IDs that exist in the movie table
    @Query("SELECT mp.movieId FROM MoviePopularity mp " +
           "WHERE EXISTS (SELECT 1 FROM Movie m WHERE m.id = mp.movieId) " +
           "ORDER BY mp.ratingCount DESC")
    List<Long> findTopMovieIds(Pageable pageable);
}
