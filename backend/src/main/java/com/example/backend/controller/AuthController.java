package com.example.backend.controller;

import com.example.backend.dto.JwtAuthenticationResponse;
import com.example.backend.dto.LoginRequest;
import com.example.backend.dto.RegisterRequest;
import com.example.backend.entity.User;
import com.example.backend.repository.UserRepository;
import com.example.backend.security.JwtTokenProvider;
import com.example.backend.service.AuthService;
import com.example.backend.dto.Role;
import lombok.RequiredArgsConstructor;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    // private final AuthenticationManager authenticationManager;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;
    private final AuthService authService;

    // Spring login best practice
    // @PostMapping("/login")
    // public ResponseEntity<?> authenticateUser(@RequestBody LoginRequest loginRequest) {
    //     Authentication authentication = authenticationManager.authenticate(
    //             new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getPassword()));

    //     SecurityContextHolder.getContext().setAuthentication(authentication);
    //     String jwt = tokenProvider.generateToken(authentication);
    //     return ResponseEntity.ok(new JwtAuthenticationResponse(jwt));
    // }


    // This is manual login
    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@RequestBody LoginRequest loginRequest) {
        try{
            boolean isValid = authService.authUser(loginRequest.getEmail(), loginRequest.getPassword());

            if(!isValid){
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid email or password");
            }

            Authentication authentication = 
                    new UsernamePasswordAuthenticationToken(
                        loginRequest.getEmail(), 
                        null,
                        List.of(new SimpleGrantedAuthority(Role.ROLE_USER.name()))
                    );

            SecurityContextHolder.getContext().setAuthentication(authentication);
            String jwt = tokenProvider.generateToken(authentication);
            return ResponseEntity.ok(new JwtAuthenticationResponse(jwt));
        } catch (Exception ex){
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid email or password");
        }
    }
    

    @PostMapping("/register")
    public ResponseEntity<?> registerUser(@RequestBody RegisterRequest signUpRequest) {
        if (userRepository.existsByEmail(signUpRequest.getEmail())) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error: Email is already in use!");
        }

        // Creating user's account
        User user = new User(signUpRequest.getEmail(),
                passwordEncoder.encode(signUpRequest.getPassword()),
                signUpRequest.getFullName(),
                "ROLE_USER");

        userRepository.save(user);

        return ResponseEntity.ok("User registered successfully!");
    }
}


