package com.example.backend.repository;

import com.example.backend.entity.WatchHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface WatchHistoryRepository extends JpaRepository<WatchHistory, Long> {
    List<WatchHistory> findByUserIdOrderByViewedAtDesc(Long userId);
    boolean existsByUserIdAndMovieId(Long userId, Long movieId);
}
