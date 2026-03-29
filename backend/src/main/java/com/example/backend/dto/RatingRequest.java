package com.example.backend.dto;

public class RatingRequest {
    private Long movieId;
    private Double rating;

    public RatingRequest() {
    }

    public RatingRequest(Long movieId, Double rating) {
        this.movieId = movieId;
        this.rating = rating;
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
}
