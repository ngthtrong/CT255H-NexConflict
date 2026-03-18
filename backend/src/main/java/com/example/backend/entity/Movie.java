package com.example.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "movies")
public class Movie {

    @Id
    private Long id; // Provided by dataset

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String genres;

    private String posterUrl;

    public Movie() {
    }

    public Movie(Long id, String title, String genres, String posterUrl) {
        this.id = id;
        this.title = title;
        this.genres = genres;
        this.posterUrl = posterUrl;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getGenres() {
        return genres;
    }

    public void setGenres(String genres) {
        this.genres = genres;
    }

    public String getPosterUrl() {
        return posterUrl;
    }

    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }
}