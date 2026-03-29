package com.example.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "movie_popularity")
public class MoviePopularity {

    @Id
    private Long movieId;

    @Column(nullable = false)
    private Long ratingCount;

    @Column
    private Double averageRating;

    public MoviePopularity() {
    }

    public MoviePopularity(Long movieId, Long ratingCount, Double averageRating) {
        this.movieId = movieId;
        this.ratingCount = ratingCount;
        this.averageRating = averageRating;
    }

    public Long getMovieId() {
        return movieId;
    }

    public void setMovieId(Long movieId) {
        this.movieId = movieId;
    }

    public Long getRatingCount() {
        return ratingCount;
    }

    public void setRatingCount(Long ratingCount) {
        this.ratingCount = ratingCount;
    }

    public Double getAverageRating() {
        return averageRating;
    }

    public void setAverageRating(Double averageRating) {
        this.averageRating = averageRating;
    }
}
