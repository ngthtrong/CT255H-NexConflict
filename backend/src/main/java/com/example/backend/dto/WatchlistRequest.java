package com.example.backend.dto;

public class WatchlistRequest {
    private Long movieId;

    public WatchlistRequest() {
    }

    public WatchlistRequest(Long movieId) {
        this.movieId = movieId;
    }

    public Long getMovieId() {
        return movieId;
    }

    public void setMovieId(Long movieId) {
        this.movieId = movieId;
    }
}
