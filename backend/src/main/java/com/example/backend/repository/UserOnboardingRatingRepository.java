package com.example.backend.repository;

import com.example.backend.entity.UserOnboardingRating;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserOnboardingRatingRepository extends JpaRepository<UserOnboardingRating, Long> {
    List<UserOnboardingRating> findByUserId(Long userId);
}
