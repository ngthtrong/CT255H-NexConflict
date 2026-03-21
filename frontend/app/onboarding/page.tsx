"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/authContext";
import api from "../lib/api";

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl?: string;
}

const ALL_GENRES = [
  "Action", "Adventure", "Animation", "Children", "Comedy",
  "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
  "Horror", "IMAX", "Musical", "Mystery", "Romance",
  "Sci-Fi", "Thriller", "War", "Western"
];

export default function OnboardingPage() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [movieRatings, setMovieRatings] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
    if (!loading && user?.onboardingCompleted) {
      router.push("/");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (step === 2) {
      fetchPopularMovies();
    }
  }, [step]);

  const fetchPopularMovies = async () => {
    try {
      const res = await api.get("/onboarding/popular-movies?limit=50");
      setPopularMovies(res.data);
    } catch (err) {
      console.error("Failed to fetch popular movies:", err);
    }
  };

  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const setRating = (movieId: number, rating: number) => {
    setMovieRatings({ ...movieRatings, [movieId]: rating });
  };

  const getRatedCount = () => Object.keys(movieRatings).length;

  const canProceedStep1 = selectedGenres.length >= 3;
  const canProceedStep2 = getRatedCount() >= 5;

  const handleComplete = async () => {
    if (!canProceedStep2) {
      setError("Please rate at least 5 movies");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const ratings = Object.entries(movieRatings).map(([movieId, rating]) => ({
        movieId: parseInt(movieId),
        rating,
      }));

      await api.post("/onboarding/complete", {
        genres: selectedGenres,
        ratings,
      });

      await refreshUser();
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to complete onboarding");
    } finally {
      setSubmitting(false);
    }
  };

  // Extract year from title like "Toy Story (1995)"
  const extractYear = (title: string) => {
    const match = title.match(/\((\d{4})\)/);
    return match ? match[1] : "";
  };

  const extractTitleWithoutYear = (title: string) => {
    return title.replace(/\s*\(\d{4}\)\s*$/, "");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome to CineStream!
          </h1>
          <p className="text-gray-400">
            Let's personalize your movie recommendations
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 1 ? "bg-red-600 text-white" : "bg-gray-700 text-gray-400"
              }`}
            >
              1
            </div>
            <div className="ml-2 mr-4">
              <span className={step >= 1 ? "text-white" : "text-gray-500"}>
                Choose Genres
              </span>
            </div>
          </div>
          <div className="w-16 h-1 bg-gray-700 mx-2">
            <div
              className={`h-full ${step >= 2 ? "bg-red-600" : "bg-gray-700"}`}
              style={{ width: step >= 2 ? "100%" : "0%" }}
            />
          </div>
          <div className="flex items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 2 ? "bg-red-600 text-white" : "bg-gray-700 text-gray-400"
              }`}
            >
              2
            </div>
            <div className="ml-2">
              <span className={step >= 2 ? "text-white" : "text-gray-500"}>
                Rate Movies
              </span>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-500 px-4 py-2 rounded mb-4 text-center">
            {error}
          </div>
        )}

        {/* Step 1: Choose Genres */}
        {step === 1 && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-2">
              Step 1: Choose your favorite genres
            </h2>
            <p className="text-gray-400 mb-6">
              Select at least 3 genres you enjoy watching
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mb-6">
              {ALL_GENRES.map((genre) => (
                <button
                  key={genre}
                  onClick={() => toggleGenre(genre)}
                  className={`px-4 py-3 rounded-lg font-medium transition-all ${
                    selectedGenres.includes(genre)
                      ? "bg-red-600 text-white border-2 border-red-500"
                      : "bg-gray-700 text-gray-300 border-2 border-gray-600 hover:border-gray-500"
                  }`}
                >
                  {genre}
                </button>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-400">
                Selected: {selectedGenres.length} / 3 minimum
              </span>
              <button
                onClick={() => setStep(2)}
                disabled={!canProceedStep1}
                className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                  canProceedStep1
                    ? "bg-red-600 text-white hover:bg-red-700"
                    : "bg-gray-600 text-gray-400 cursor-not-allowed"
                }`}
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Rate Movies */}
        {step === 2 && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-2">
              Step 2: Rate some movies you've watched
            </h2>
            <p className="text-gray-400 mb-6">
              Rate at least 5 movies to help us understand your taste
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-6 max-h-[500px] overflow-y-auto">
              {popularMovies.map((movie) => (
                <div
                  key={movie.id}
                  className={`bg-gray-700 rounded-lg overflow-hidden transition-all ${
                    movieRatings[movie.id] ? "ring-2 ring-red-500" : ""
                  }`}
                >
                  {/* Poster or placeholder */}
                  <div className="aspect-[2/3] bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center p-2">
                    {movie.posterUrl ? (
                      <img
                        src={movie.posterUrl}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-center">
                        <div className="text-white text-sm font-medium line-clamp-3">
                          {extractTitleWithoutYear(movie.title)}
                        </div>
                        <div className="text-gray-400 text-xs mt-1">
                          {extractYear(movie.title)}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Title */}
                  <div className="p-2">
                    <h3 className="text-white text-xs font-medium line-clamp-2 mb-2">
                      {movie.title}
                    </h3>

                    {/* Star Rating */}
                    <div className="flex justify-center gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => setRating(movie.id, star)}
                          className={`text-lg ${
                            movieRatings[movie.id] >= star
                              ? "text-yellow-400"
                              : "text-gray-500"
                          }`}
                        >
                          ★
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setStep(1)}
                  className="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600"
                >
                  Back
                </button>
                <span className="text-gray-400">
                  Rated: {getRatedCount()} / 5 minimum
                </span>
              </div>
              <button
                onClick={handleComplete}
                disabled={!canProceedStep2 || submitting}
                className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                  canProceedStep2 && !submitting
                    ? "bg-red-600 text-white hover:bg-red-700"
                    : "bg-gray-600 text-gray-400 cursor-not-allowed"
                }`}
              >
                {submitting ? "Saving..." : "Complete Setup"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
