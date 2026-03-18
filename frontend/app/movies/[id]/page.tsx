'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../../components/Navbar';
import MovieCard from '../../components/MovieCard';
import { useAuth } from '../../lib/authContext';
import api from '../../lib/api';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

interface Rating {
  id: number;
  rating: number;
  userId: number;
  movieId: number;
}

export default function MovieDetailPage() {
  const params = useParams();
  const movieId = params.id;
  const { user } = useAuth();

  const [movie, setMovie] = useState<Movie | null>(null);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [userRating, setUserRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [ratingSubmitting, setRatingSubmitting] = useState(false);

  useEffect(() => {
    const fetchMovieData = async () => {
      try {
        setLoading(true);
        // Fetch movie details
        const movieRes = await api.get(`/movies/${movieId}`);
        setMovie(movieRes.data);

        // Fetch similar movies
        try {
          const similarRes = await api.get(`/recommendations/similar/${movieId}`);
          setSimilarMovies(similarRes.data || []);
        } catch (e) {
          console.error('Failed to fetch similar movies');
        }

        // Fetch user's rating if logged in
        if (user) {
          try {
            const ratingRes = await api.get(`/ratings/movie/${movieId}/user`);
            if (ratingRes.data) {
              setUserRating(ratingRes.data.rating);
            }
          } catch (e) {
            // No rating yet
          }
        }
      } catch (err: any) {
        setError(err.response?.data?.message || 'Movie not found');
      } finally {
        setLoading(false);
      }
    };

    if (movieId) {
      fetchMovieData();
    }
  }, [movieId, user]);

  const handleRating = async (rating: number) => {
    if (!user) {
      alert('Please login to rate movies');
      return;
    }

    setRatingSubmitting(true);
    try {
      await api.post(`/ratings`, {
        movieId: Number(movieId),
        rating: rating
      });
      setUserRating(rating);
    } catch (err: any) {
      console.error('Failed to submit rating:', err);
      alert('Failed to submit rating');
    } finally {
      setRatingSubmitting(false);
    }
  };

  const genreList = movie?.genres?.split('|') || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white">
        <Navbar />
        <div className="flex items-center justify-center pt-32">
          <div className="animate-pulse text-xl">Loading movie...</div>
        </div>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-black text-white">
        <Navbar />
        <div className="flex flex-col items-center justify-center pt-32 gap-4">
          <div className="text-xl text-red-500">{error || 'Movie not found'}</div>
          <Link href="/" className="text-red-600 hover:text-red-500">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="pt-20 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* Movie Header */}
          <div className="flex flex-col md:flex-row gap-8 mt-8">
            {/* Poster */}
            <div className="flex-shrink-0 w-full md:w-80">
              <div className="aspect-[2/3] w-full bg-zinc-800 rounded-lg overflow-hidden">
                {movie.posterUrl ? (
                  <img src={movie.posterUrl} alt={movie.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="flex h-full items-center justify-center text-zinc-500 text-lg">
                    No Poster Available
                  </div>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">{movie.title}</h1>

              {/* Genres */}
              <div className="flex flex-wrap gap-2 mb-6">
                {genreList.map((genre, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-zinc-800 text-zinc-300 rounded-full text-sm"
                  >
                    {genre}
                  </span>
                ))}
              </div>

              {/* Rating Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-3">
                  {user ? 'Your Rating' : 'Rate this movie'}
                </h3>
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      disabled={ratingSubmitting || !user}
                      onClick={() => handleRating(star)}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                      className={`text-3xl transition-colors ${
                        !user ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
                      }`}
                    >
                      <span className={
                        (hoverRating || userRating) >= star
                          ? 'text-yellow-400'
                          : 'text-zinc-600'
                      }>
                        ★
                      </span>
                    </button>
                  ))}
                  {userRating > 0 && (
                    <span className="ml-3 text-zinc-400">
                      {userRating}/5
                    </span>
                  )}
                </div>
                {!user && (
                  <p className="text-sm text-zinc-500 mt-2">
                    <Link href="/login" className="text-red-500 hover:text-red-400">Login</Link> to rate this movie
                  </p>
                )}
              </div>

              {/* Add to Watchlist Button */}
              {user && (
                <button
                  onClick={async () => {
                    try {
                      await api.post('/watchlist', { movieId: movie.id });
                      alert('Added to watchlist!');
                    } catch (err: any) {
                      if (err.response?.status === 409) {
                        alert('Already in watchlist');
                      } else {
                        alert('Failed to add to watchlist');
                      }
                    }
                  }}
                  className="px-6 py-3 bg-red-600 hover:bg-red-500 rounded-md font-semibold transition-colors"
                >
                  + Add to Watchlist
                </button>
              )}
            </div>
          </div>

          {/* Similar Movies */}
          {similarMovies.length > 0 && (
            <div className="mt-16">
              <h2 className="text-2xl font-bold mb-6">Similar Movies</h2>
              <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
                {similarMovies.map((m) => (
                  <MovieCard key={m.id} movie={m} />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
