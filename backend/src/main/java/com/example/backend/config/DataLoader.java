package com.example.backend.config;

import com.example.backend.entity.Movie;
import com.example.backend.entity.MoviePopularity;
import com.example.backend.repository.MoviePopularityRepository;
import com.example.backend.repository.MovieRepository;
import com.example.backend.service.TMDBService;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Component
public class DataLoader implements CommandLineRunner {

    private final MovieRepository movieRepository;
    private final MoviePopularityRepository moviePopularityRepository;
    private final TMDBService tmdbService;

    @Value("${poster.sync.on-startup:true}")
    private boolean syncPostersOnStartup;

    @Value("${poster.sync.fetch-batch-size:100}")
    private int posterSyncFetchBatchSize;

    @Value("${poster.sync.save-batch-size:100}")
    private int posterSyncSaveBatchSize;

    @Value("${poster.sync.max-movies:300}")
    private int posterSyncMaxMovies;

    public DataLoader(MovieRepository movieRepository, MoviePopularityRepository moviePopularityRepository, TMDBService tmdbService) {
        this.movieRepository = movieRepository;
        this.moviePopularityRepository = moviePopularityRepository;
        this.tmdbService = tmdbService;
    }

    @Override
    public void run(String... args) throws Exception {
        loadMovies();
        loadMovieLinks();
        loadMoviePopularity();
        syncMissingPosters();
    }

    private void syncMissingPosters() {
        if (!syncPostersOnStartup) {
            System.out.println("DataLoader: Startup poster sync disabled.");
            return;
        }

        Integer maxMovies = posterSyncMaxMovies > 0 ? posterSyncMaxMovies : null;
        System.out.println("DataLoader: Starting poster sync (fetchBatchSize=" + posterSyncFetchBatchSize
                + ", saveBatchSize=" + posterSyncSaveBatchSize + ", maxMovies=" + maxMovies + ")");

        Map<String, Object> stats = tmdbService.syncMissingPosters(
                posterSyncFetchBatchSize,
                posterSyncSaveBatchSize,
                maxMovies
        );
        System.out.println("DataLoader: Poster sync completed: " + stats);
    }

    private void loadMovies() {
        if (movieRepository.count() == 0) {
            Path path = findFile("movies.csv");
            if (path == null) {
                System.out.println("DataLoader: movies.csv not found");
                return;
            }

            System.out.println("DataLoader: Loading movies from " + path.toAbsolutePath());

            try (Reader reader = new FileReader(path.toFile(), StandardCharsets.UTF_8);
                 CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader().withIgnoreHeaderCase().withTrim())) {

                List<Movie> movies = new ArrayList<>();
                int count = 0;
                for (CSVRecord csvRecord : csvParser) {
                    try {
                        Movie movie = new Movie();
                        movie.setId(Long.parseLong(csvRecord.get("movieId")));
                        movie.setTitle(csvRecord.get("title"));
                        movie.setGenres(csvRecord.get("genres"));
                        movies.add(movie);
                        count++;

                        // Save in batches
                        if (movies.size() >= 500) {
                            movieRepository.saveAll(movies);
                            movies.clear();
                        }
                    } catch (NumberFormatException e) {
                        System.err.println("Skipping invalid record: " + csvRecord);
                    }
                }

                if (!movies.isEmpty()) {
                    movieRepository.saveAll(movies);
                }

                System.out.println("DataLoader: Successfully loaded " + movieRepository.count() + " movies.");
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("DataLoader: Movies already loaded (" + movieRepository.count() + " records).");
        }
    }

    private void loadMovieLinks() {
        Path path = findFile("links.csv");
        if (path == null) {
            System.out.println("DataLoader: links.csv not found, skipping link loading");
            return;
        }

        // Check if we need to update - look for movies without tmdbId
        List<Movie> moviesWithoutTmdb = movieRepository.findAll().stream()
                .filter(m -> m.getTmdbId() == null)
                .toList();

        if (moviesWithoutTmdb.isEmpty()) {
            System.out.println("DataLoader: Movie links already loaded.");
            return;
        }

        System.out.println("DataLoader: Loading movie links from " + path.toAbsolutePath());

        try (Reader reader = new FileReader(path.toFile(), StandardCharsets.UTF_8);
             CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader().withIgnoreHeaderCase().withTrim())) {

            // Create a map of movieId -> Movie for quick lookup
            Map<Long, Movie> movieMap = new HashMap<>();
            for (Movie movie : movieRepository.findAll()) {
                movieMap.put(movie.getId(), movie);
            }

            List<Movie> moviesToUpdate = new ArrayList<>();
            for (CSVRecord csvRecord : csvParser) {
                try {
                    Long movieId = Long.parseLong(csvRecord.get("movieId"));
                    Movie movie = movieMap.get(movieId);

                    if (movie != null) {
                        String tmdbIdStr = csvRecord.get("tmdbId");
                        String imdbIdStr = csvRecord.get("imdbId");

                        if (tmdbIdStr != null && !tmdbIdStr.isEmpty()) {
                            // Parse as double first to handle decimal format (e.g., "19457.0")
                            movie.setTmdbId(Double.valueOf(tmdbIdStr).longValue());
                        }
                        if (imdbIdStr != null && !imdbIdStr.isEmpty()) {
                            movie.setImdbId(imdbIdStr);
                        }

                        moviesToUpdate.add(movie);

                        // Save in batches
                        if (moviesToUpdate.size() >= 500) {
                            movieRepository.saveAll(moviesToUpdate);
                            moviesToUpdate.clear();
                        }
                    }
                } catch (NumberFormatException e) {
                    // Skip invalid records
                }
            }

            if (!moviesToUpdate.isEmpty()) {
                movieRepository.saveAll(moviesToUpdate);
            }

            System.out.println("DataLoader: Movie links loaded successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void loadMoviePopularity() {
        if (moviePopularityRepository.count() > 0) {
            System.out.println("DataLoader: Movie popularity already loaded (" + moviePopularityRepository.count() + " records).");
            return;
        }

        Path path = findFile("ratings.csv");
        if (path == null) {
            System.out.println("DataLoader: ratings.csv not found, skipping popularity loading");
            return;
        }

        System.out.println("DataLoader: Calculating movie popularity from " + path.toAbsolutePath());
        System.out.println("DataLoader: This may take a few minutes for large files...");

        try (Reader reader = new FileReader(path.toFile(), StandardCharsets.UTF_8);
             CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader().withIgnoreHeaderCase().withTrim())) {

            // Count ratings and sum for each movie
            Map<Long, Long> ratingCounts = new HashMap<>();
            Map<Long, Double> ratingSums = new HashMap<>();

            int recordCount = 0;
            for (CSVRecord csvRecord : csvParser) {
                try {
                    Long movieId = Long.parseLong(csvRecord.get("movieId"));
                    Double rating = Double.parseDouble(csvRecord.get("rating"));

                    ratingCounts.merge(movieId, 1L, Long::sum);
                    ratingSums.merge(movieId, rating, Double::sum);

                    recordCount++;
                    if (recordCount % 1000000 == 0) {
                        System.out.println("DataLoader: Processed " + recordCount + " ratings...");
                    }
                } catch (NumberFormatException e) {
                    // Skip invalid records
                }
            }

            System.out.println("DataLoader: Processed " + recordCount + " total ratings for " + ratingCounts.size() + " movies");

            // Save popularity data in batches
            List<MoviePopularity> popularityList = new ArrayList<>();
            for (Map.Entry<Long, Long> entry : ratingCounts.entrySet()) {
                Long movieId = entry.getKey();
                Long count = entry.getValue();
                Double avgRating = ratingSums.get(movieId) / count;

                popularityList.add(new MoviePopularity(movieId, count, avgRating));

                if (popularityList.size() >= 500) {
                    moviePopularityRepository.saveAll(popularityList);
                    popularityList.clear();
                }
            }

            if (!popularityList.isEmpty()) {
                moviePopularityRepository.saveAll(popularityList);
            }

            System.out.println("DataLoader: Movie popularity loaded successfully (" + moviePopularityRepository.count() + " records).");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private Path findFile(String filename) {
        String[] possiblePaths = {
            "../data/" + filename,
            "data/" + filename,
            "../../data/" + filename,
            "D:/CT255H - BI/Project/CT255H-NexConflict/data/" + filename
        };

        for (String p : possiblePaths) {
            Path path = Paths.get(p);
            if (Files.exists(path)) {
                return path;
            }
        }
        return null;
    }
}
