package com.example.backend.service;

import com.example.backend.entity.*;
import com.example.backend.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class RecommendationService {

    private static final int DEFAULT_RECOMMEND_LIMIT = 10;
    private static final int COLLABORATIVE_CANDIDATE_LIMIT = 30;
    private static final int MIN_RATINGS_FOR_SVD = 5;
    private static final double LIKED_RATING_THRESHOLD = 3.5;

    private final MovieRepository movieRepository;
    private final WatchlistRepository watchlistRepository;
    private final UserPreferenceRepository userPreferenceRepository;
    private final RatingRepository ratingRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    
    @Value("${ai.service.url:http://localhost:8000}")
    private String AI_SERVICE_URL;

    public RecommendationService(
            MovieRepository movieRepository, 
            WatchlistRepository watchlistRepository,
            UserPreferenceRepository userPreferenceRepository,
            RatingRepository ratingRepository
    ) {
        this.movieRepository = movieRepository;
        this.watchlistRepository = watchlistRepository;
        this.userPreferenceRepository = userPreferenceRepository;
        this.ratingRepository = ratingRepository;
    }

    public List<Movie> getRecommendationsForUser(User user) {
        return getRecommendationsForUser(user, false);
    }

    public List<Movie> getRecommendationsForUser(User user, boolean refresh) {
        return getRecommendationsForUserWithTrace(user, refresh).movies();
    }

    public RecommendationTraceResult getRecommendationsForUserWithTrace(User user, boolean refresh) {
        List<Rating> ratings = ratingRepository.findByUser(user);

        // Không bao giờ đề xuất lại phim user đã đánh giá (đặc biệt các phim điểm thấp)
        Set<Long> alreadyRatedMovieIds = ratings.stream()
                .map(r -> r.getMovie().getId())
                .collect(Collectors.toSet());

        // Tín hiệu sở thích để rerank danh sách collaborative cho sát profile user hơn
        Set<String> preferredGenres = buildPreferredGenres(user, ratings);

        // 1) Ưu tiên SVD cho user có đủ dữ liệu rating (collaborative filtering)
        if (ratings.size() >= MIN_RATINGS_FOR_SVD) {
            List<Movie> collaborative = getCollaborativeRecommendations(user, refresh, alreadyRatedMovieIds, preferredGenres);
            if (!collaborative.isEmpty()) {
                return new RecommendationTraceResult(collaborative, "FOR_YOU_COLLABORATIVE", "SVD");
            }
        }

        // 2) Nếu có watchlist thì dùng content-based theo watchlist
        List<Movie> watchlistBased = getWatchlistBasedRecommendations(user, refresh, alreadyRatedMovieIds);
        if (!watchlistBased.isEmpty()) {
            return new RecommendationTraceResult(watchlistBased, "FOR_YOU_WATCHLIST", "CONTENT_BASED");
        }

        // 3) Cuối cùng fallback sang personalized content-based (onboarding + ratings)
        List<Movie> personalized = getPersonalizedRecommendations(user, refresh, alreadyRatedMovieIds);
        if (!personalized.isEmpty()) {
            return new RecommendationTraceResult(personalized, "FOR_YOU_PERSONALIZED", "CONTENT_BASED");
        }

        return new RecommendationTraceResult(new ArrayList<>(), "FOR_YOU_EMPTY", "NONE");
    }

    public record RecommendationTraceResult(List<Movie> movies, String flow, String model) {}

    private List<Movie> getCollaborativeRecommendations(
            User user,
            boolean refresh,
            Set<Long> excludedMovieIds,
            Set<String> preferredGenres
    ) {
        try {
            // Không dùng strict mode ở đây vì strict kiểm tra lịch sử theo ratings_df của model (MovieLens),
            // không phản ánh đầy đủ lịch sử rating của user trong database ứng dụng.
            int requestLimit = refresh ? COLLABORATIVE_CANDIDATE_LIMIT : DEFAULT_RECOMMEND_LIMIT;
            String endpoint = AI_SERVICE_URL + "/recommendations/" + user.getId() + "?limit="
                + requestLimit;
            List<?> movieIds = restTemplate.getForObject(endpoint, List.class);

            if (movieIds != null && !movieIds.isEmpty()) {
                List<Long> ids = movieIds.stream()
                        .map(id -> Long.valueOf(id.toString()))
                        .collect(Collectors.toList());

                if (refresh && ids.size() > DEFAULT_RECOMMEND_LIMIT) {
                    List<Long> diversifyPool = new ArrayList<>(ids.subList(0, Math.min(ids.size(), COLLABORATIVE_CANDIDATE_LIMIT)));
                    Collections.shuffle(diversifyPool, new Random());
                    ids = new ArrayList<>(diversifyPool.subList(0, DEFAULT_RECOMMEND_LIMIT));
                } else if (ids.size() > DEFAULT_RECOMMEND_LIMIT) {
                    ids = new ArrayList<>(ids.subList(0, DEFAULT_RECOMMEND_LIMIT));
                }

                List<Movie> movies = movieRepository.findAllById(ids);
                Map<Long, Movie> movieById = movies.stream().collect(Collectors.toMap(Movie::getId, m -> m));
                List<Movie> ordered = ids.stream()
                        .map(movieById::get)
                        .filter(Objects::nonNull)
                        .filter(movie -> !excludedMovieIds.contains(movie.getId()))
                        .collect(Collectors.toList());

                List<Movie> reranked = rerankByGenreAffinity(ordered, preferredGenres, refresh);
                if (reranked.size() > DEFAULT_RECOMMEND_LIMIT) {
                    reranked = reranked.subList(0, DEFAULT_RECOMMEND_LIMIT);
                }

                System.out.println("[SVD] Recommendations for user " + user.getId()
                        + " (refresh=" + refresh + ", excluded=" + excludedMovieIds.size() + "): "
                        + reranked.stream().map(Movie::getId).collect(Collectors.toList()));
                return reranked;
            }
        } catch (Exception e) {
            System.err.println("Collaborative recommendations failed: " + e.getMessage());
        }

        return new ArrayList<>();
    }

    private List<Movie> getWatchlistBasedRecommendations(User user, boolean refresh, Set<Long> excludedMovieIds) {
        List<Watchlist> watchlist = watchlistRepository.findByUserOrderByAddedAtDesc(user);
        if (watchlist.isEmpty()) {
            return new ArrayList<>();
        }

        List<Long> watchlistMovieIds = watchlist.stream()
                .map(w -> w.getMovie().getId())
                .collect(Collectors.toList());

        System.out.println("Getting recommendations based on watchlist: " + watchlistMovieIds);

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<List<Long>> request = new HttpEntity<>(watchlistMovieIds, headers);

            List<?> movieIds = restTemplate.postForObject(
                    AI_SERVICE_URL + "/recommendations/based-on-movies?limit=" + DEFAULT_RECOMMEND_LIMIT + "&refresh=" + refresh,
                    request,
                    List.class
            );

            if (movieIds != null && !movieIds.isEmpty()) {
                List<Long> ids = movieIds.stream()
                        .map(id -> Long.valueOf(id.toString()))
                        .collect(Collectors.toList());
                System.out.println("[Content-Watchlist] AI recommended movies: " + ids);
                return movieRepository.findAllById(ids).stream()
                        .filter(movie -> !excludedMovieIds.contains(movie.getId()))
                        .collect(Collectors.toList());
            }
        } catch (Exception e) {
            System.err.println("AI Service unavailable for watchlist-based: " + e.getMessage());
        }

        return new ArrayList<>();
    }

    /**
     * Get personalized recommendations based on user's preferred genres and rated movies.
     * This is used for new users who are not in the pre-trained collaborative filtering models.
     */
    private List<Movie> getPersonalizedRecommendations(User user) {
        return getPersonalizedRecommendations(user, false, Collections.emptySet());
    }

    private List<Movie> getPersonalizedRecommendations(User user, boolean refresh, Set<Long> excludedMovieIds) {
        try {
            // Get user's preferred genres from onboarding
            List<UserPreference> preferences = userPreferenceRepository.findByUserId(user.getId());
            List<String> preferredGenres = preferences.stream()
                    .map(UserPreference::getGenreName)
                    .collect(Collectors.toList());

            // Get user's rated movies
            List<Rating> ratings = ratingRepository.findByUser(user);
            List<Map<String, Object>> ratedMovies = ratings.stream()
                    .map(r -> {
                        Map<String, Object> map = new HashMap<>();
                        map.put("movieId", r.getMovie().getId());
                        map.put("rating", r.getRating());
                        return map;
                    })
                    .collect(Collectors.toList());

            System.out.println("Getting personalized recommendations for user " + user.getId() + " (refresh=" + refresh + ")");
            System.out.println("Preferred genres: " + preferredGenres);
            System.out.println("Rated movies count: " + ratedMovies.size());

            // Build request body
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("preferredGenres", preferredGenres);
            requestBody.put("ratedMovies", ratedMovies);
            requestBody.put("limit", DEFAULT_RECOMMEND_LIMIT);
            requestBody.put("userId", user.getId());  // Add userId for user-specific results
            requestBody.put("refresh", refresh);  // Add refresh flag for new recommendations

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);

            List<?> movieIds = restTemplate.postForObject(
                    AI_SERVICE_URL + "/recommendations/personalized",
                    request,
                    List.class
            );

            if (movieIds != null && !movieIds.isEmpty()) {
                List<Long> ids = movieIds.stream()
                        .map(id -> Long.valueOf(id.toString()))
                        .collect(Collectors.toList());
                System.out.println("Personalized recommendations: " + ids);
                return movieRepository.findAllById(ids).stream()
                        .filter(movie -> !excludedMovieIds.contains(movie.getId()))
                        .collect(Collectors.toList());
            }
        } catch (Exception e) {
            System.err.println("Personalized recommendations failed: " + e.getMessage());
            e.printStackTrace();
        }

        // Final fallback: Return newest popular movies
        System.out.println("Falling back to newest movies");
        return movieRepository.findAllByOrderByIdDesc().stream()
                .filter(movie -> !excludedMovieIds.contains(movie.getId()))
                .limit(DEFAULT_RECOMMEND_LIMIT)
                .collect(Collectors.toList());
    }

    private Set<String> buildPreferredGenres(User user, List<Rating> ratings) {
        Set<String> preferredGenres = new HashSet<>();

        List<UserPreference> onboardingPrefs = userPreferenceRepository.findByUserId(user.getId());
        preferredGenres.addAll(onboardingPrefs.stream()
                .map(UserPreference::getGenreName)
                .filter(Objects::nonNull)
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toSet()));

        ratings.stream()
                .filter(r -> r.getRating() != null && r.getRating() >= LIKED_RATING_THRESHOLD)
                .map(r -> r.getMovie().getGenres())
                .filter(Objects::nonNull)
                .forEach(genres -> {
                    for (String genre : genres.split("\\|")) {
                        String normalized = genre.trim();
                        if (!normalized.isEmpty()) {
                            preferredGenres.add(normalized);
                        }
                    }
                });

        return preferredGenres;
    }

    private List<Movie> rerankByGenreAffinity(List<Movie> movies, Set<String> preferredGenres, boolean refresh) {
        if (movies.isEmpty() || preferredGenres.isEmpty()) {
            return movies;
        }

        List<Movie> reranked = new ArrayList<>(movies);
        Map<Long, Integer> baseOrder = new HashMap<>();
        Map<Long, Integer> randomTieBreaker = new HashMap<>();
        Random random = refresh ? new Random() : null;
        for (int i = 0; i < movies.size(); i++) {
            baseOrder.put(movies.get(i).getId(), i);
            if (refresh) {
                randomTieBreaker.put(movies.get(i).getId(), random.nextInt(1000000));
            }
        }

        reranked.sort((a, b) -> {
            int scoreA = countGenreMatches(a.getGenres(), preferredGenres);
            int scoreB = countGenreMatches(b.getGenres(), preferredGenres);
            if (scoreA != scoreB) {
                return Integer.compare(scoreB, scoreA);
            }

            if (refresh) {
                return Integer.compare(
                        randomTieBreaker.getOrDefault(a.getId(), 0),
                        randomTieBreaker.getOrDefault(b.getId(), 0)
                );
            }

            return Integer.compare(baseOrder.getOrDefault(a.getId(), Integer.MAX_VALUE),
                    baseOrder.getOrDefault(b.getId(), Integer.MAX_VALUE));
        });

        return reranked;
    }

    private int countGenreMatches(String genres, Set<String> preferredGenres) {
        if (genres == null || genres.isBlank()) {
            return 0;
        }

        int matches = 0;
        for (String genre : genres.split("\\|")) {
            if (preferredGenres.contains(genre.trim())) {
                matches++;
            }
        }
        return matches;
    }

    public List<Movie> getSimilarMovies(Long movieId) {
        try {
             List<?> movieIds = restTemplate.getForObject(AI_SERVICE_URL + "/similar/" + movieId, List.class);
             if (movieIds != null && !movieIds.isEmpty()) {
                 List<Long> ids = movieIds.stream()
                         .map(id -> Long.valueOf(id.toString()))
                         .collect(Collectors.toList());
                 return movieRepository.findAllById(ids);
            }
        } catch (Exception e) {
             System.err.println("AI Service unavailable: " + e.getMessage());
        }
        return new ArrayList<>();
    }
}
