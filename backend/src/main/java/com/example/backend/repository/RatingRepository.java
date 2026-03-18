package com.example.backend.repository;

import com.example.backend.entity.Rating;
import com.example.backend.entity.User;
import com.example.backend.entity.Movie;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RatingRepository extends JpaRepository<Rating, Long> {

    Optional<Rating> findByUserAndMovie(User user, Movie movie);

    List<Rating> findByUser(User user);

    List<Rating> findByMovie(Movie movie);

    @Query("SELECT AVG(r.rating) FROM Rating r WHERE r.movie.id = :movieId")
    Double findAverageRatingByMovieId(Long movieId);

    @Query("SELECT COUNT(r) FROM Rating r WHERE r.movie.id = :movieId")
    Long countByMovieId(Long movieId);

    boolean existsByUserAndMovie(User user, Movie movie);
}
