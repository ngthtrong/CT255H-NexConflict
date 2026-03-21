package com.example.backend.service;

import java.util.Optional;

import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.example.backend.repository.UserRepository;
import com.example.backend.entity.User;
import com.example.backend.config.SecurityConfig;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService{
    private final UserRepository repository;

    private final PasswordEncoder passwordEncoder;

    public boolean authUser(String email, String password){
        User user = repository.findByEmail(email)
            .orElseThrow(() -> new UsernameNotFoundException("User not found with email" + email));

        return passwordEncoder.matches(password, user.getPassword());
    }
}
