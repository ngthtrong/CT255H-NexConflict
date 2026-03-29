package com.example.backend.config;

import com.example.backend.entity.Movie;
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
    private final TMDBService tmdbService;

    @Value("${poster.sync.on-startup:true}")
    private boolean syncPostersOnStartup;

    @Value("${poster.sync.fetch-batch-size:100}")
    private int posterSyncFetchBatchSize;

    @Value("${poster.sync.save-batch-size:100}")
    private int posterSyncSaveBatchSize;

    @Value("${poster.sync.max-movies:300}")
    private int posterSyncMaxMovies;

    public DataLoader(MovieRepository movieRepository, TMDBService tmdbService) {
        this.movieRepository = movieRepository;
        this.tmdbService = tmdbService;
    }

    @Override
    public void run(String... args) throws Exception {
        loadMovies();
        loadMovieLinks();
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

                        // Limit to 1000 movies for quick dev startup
                        if (count >= 1000) {
                            break;
                        }

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
                            movie.setTmdbId(Long.parseLong(tmdbIdStr));
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
