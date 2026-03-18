package com.example.backend.config;

import com.example.backend.entity.Movie;
import com.example.backend.repository.MovieRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Component
public class DataLoader implements CommandLineRunner {

    private final MovieRepository movieRepository;

    public DataLoader(MovieRepository movieRepository) {
        this.movieRepository = movieRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        loadMovies();
    }

    private void loadMovies() {
        if (movieRepository.count() == 0) {
            // Try to locate the file relative to project root or backend folder
            Path path = Paths.get("../data/movies.csv");
            if (!Files.exists(path)) {
                // Fallback for different working directory scenarios
                path = Paths.get("data/movies.csv");
            }

            if (!Files.exists(path)) {
                System.out.println("DataLoader: movies.csv not found at " + path.toAbsolutePath());
                return;
            }

            System.out.println("DataLoader: Loading movies from " + path.toAbsolutePath());

            try (Reader reader = new FileReader(path.toFile(), StandardCharsets.UTF_8);
                 CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader().withIgnoreHeaderCase().withTrim())) {

                List<Movie> movies = new ArrayList<>();
                for (CSVRecord csvRecord : csvParser) {
                    try {
                        Movie movie = new Movie();
                        movie.setId(Long.parseLong(csvRecord.get("movieId"))); // Case-sensitive header matching
                        movie.setTitle(csvRecord.get("title"));
                        movie.setGenres(csvRecord.get("genres"));
                        movies.add(movie);
                        
                        // Limit to 500 movies for quick dev startup
                        if (movieRepository.count() + movies.size() >= 500) {
                            break;
                        }
                        
                        // Save in batches to avoid memory issues with large datasets
                        if (movies.size() >= 1000) {
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
}
