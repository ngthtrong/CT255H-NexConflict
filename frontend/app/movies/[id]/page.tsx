'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../../components/Navbar';
import MovieCard from '../../components/MovieCard';
import api from '../../lib/api';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

export default function MovieDetailPage() {
  const params = useParams();
  const movieId = params?.id;

  const [movie, setMovie] = useState<Movie | null>(null);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!movieId) return;

    const fetchMovie = async () => {
      try {
        setLoading(true);
        const [movieRes, similarRes] = await Promise.all([
          api.get(`/movies/${movieId}`),
          api.get(`/recommendations/similar/${movieId}`).catch(() => ({ data: [] })),
        ]);
        setMovie(movieRes.data);
        setSimilarMovies(similarRes.data || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load movie');
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [movieId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-white">
        <p className="animate-pulse text-xl">Loading...</p>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-black text-white gap-4">
        <p className="text-red-400 text-lg">{error || 'Movie not found'}</p>
        <Link href="/" className="rounded-md bg-zinc-800 px-4 py-2 text-sm hover:bg-zinc-700">
          Back to Home
        </Link>
      </div>
    );
  }

  const genreList = movie.genres ? movie.genres.split('|') : [];

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 pt-24 pb-20 sm:px-6 lg:px-8">
        {/* Movie Header */}
        <div className="flex flex-col gap-8 sm:flex-row">
          {/* Poster */}
          <div className="w-full shrink-0 sm:w-56 lg:w-64">
            <div className="aspect-[2/3] overflow-hidden rounded-lg bg-zinc-800">
              {movie.posterUrl ? (
                <img
                  src={movie.posterUrl}
                  alt={movie.title}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-zinc-500 text-sm">
                  No Poster
                </div>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="flex flex-col justify-center gap-4">
            <h1 className="text-3xl font-bold text-white sm:text-4xl">{movie.title}</h1>

            {genreList.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {genreList.map((genre) => (
                  <span
                    key={genre}
                    className="rounded-full bg-zinc-800 px-3 py-1 text-xs font-medium text-zinc-300"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            <Link
              href="/"
              className="mt-4 inline-flex w-fit items-center gap-2 rounded-md bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-300 hover:bg-zinc-700 hover:text-white"
            >
              ← Back to Home
            </Link>
          </div>
        </div>

        {/* Similar Movies */}
        {similarMovies.length > 0 && (
          <div className="mt-16">
            <h2 className="mb-6 text-2xl font-bold text-white">Similar Movies</h2>
            <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 sm:gap-x-6 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
              {similarMovies.map((m) => (
                <MovieCard key={m.id} movie={m} />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
