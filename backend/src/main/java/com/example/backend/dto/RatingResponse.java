package com.example.backend.dto;

public class RatingResponse {
    private Long id;
    private Long movieId;
    private Double rating;
    private Double averageRating;
    private Long totalRatings;

    public RatingResponse() {
    }

    public RatingResponse(Long id, Long movieId, Double rating) {
        this.id = id;
        this.movieId = movieId;
        this.rating = rating;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getMovieId() {
        return movieId;
    }

    public void setMovieId(Long movieId) {
        this.movieId = movieId;
    }

    public Double getRating() {
        return rating;
    }

    public void setRating(Double rating) {
        this.rating = rating;
    }

    public Double getAverageRating() {
        return averageRating;
    }

    public void setAverageRating(Double averageRating) {
        this.averageRating = averageRating;
    }

    public Long getTotalRatings() {
        return totalRatings;
    }

    public void setTotalRatings(Long totalRatings) {
        this.totalRatings = totalRatings;
    }
}
