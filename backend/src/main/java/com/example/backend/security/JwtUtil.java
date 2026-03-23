package com.example.backend.security;

import java.security.Key;
import java.util.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.example.backend.dto.Role;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;

// Using @Component because this class have a Value that using Dependency Injection
@Component
@Slf4j
public class JwtUtil {
    @Value("${myapp.jwt.secret}")
    private String secretKey;
    @Value("${myapp.jwt.expiration}")
    private long expirationTime;

    private Key getSignInKey() {
        byte[] keyBytes = Decoders.BASE64.decode(secretKey);
        return Keys.hmacShaKeyFor(keyBytes);
    }
    
    public String generateToken(String username) {
        return Jwts.builder()
                .setSubject(username) 
                // Ghi tên user vào thẻ
                .setIssuedAt(new Date(System.currentTimeMillis())) 
                // Ngày cấp
                .claim("roles", Role.ROLE_USER)
                .setExpiration(new Date(System.currentTimeMillis() + expirationTime)) 
                // Ngày hết hạn (cộng thêm 24h)
                .signWith(getSignInKey(), SignatureAlgorithm.HS256) 
                // Lấy "chìa khóa" ra đóng mộc HMAC-SHA256
                .compact(); // Đóng gói xuất ra chuỗi Token thật dài (eyABC...)
    }

    private Claims extractClaims(String token){
        return Jwts.parserBuilder()
                   .setSigningKey(getSignInKey()) 
                   .build()
                   .parseClaimsJws(token)
                   .getBody();
    }

    public String extractUsername(String token){
        return this.extractClaims(token).getSubject();
    }

    public Date extractExpiration(String token){
        return this.extractClaims(token).getExpiration();
    }

    public String extractRoles(String token) {
        try {
            // 1. Extract the entire payload
            Claims claims = this.extractClaims(token);
            
            // 2. Best Practice: Pass the expected Class type directly to the .get() method.
            // The JJWT library will safely handle the conversion without risky force-casting.
            // The string "role" MUST exactly match the key you used in .claim("role", ...)
            String role = claims.get("role", String.class);
            
            // 3. Defensive programming: Never trust the client's token to be perfectly formed
            if (role == null || role.trim().isEmpty()) {
                log.warn("Critical: Intercepted a valid token that is missing the 'role' claim.");
                throw new IllegalArgumentException("Invalid token payload: Missing role specification");
            }
            
            return role;
            
        } catch (Exception e) {
            log.error("Failed to extract role from JWT payload. Token might be malformed.", e);
            // Trade-off: Do not leak the exact stack trace to the client. 
            // Throw a generic security exception to be handled by your GlobalExceptionHandler.
            throw new SecurityException("Unauthorized access: Token payload processing failed");
        }
    }
    public boolean validationToken(String token){
        try {
            Jwts.parserBuilder().setSigningKey(getSignInKey())
                                .build().parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

}   