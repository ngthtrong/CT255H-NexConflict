'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import { useAuth } from '../lib/authContext';
import api from '../lib/api';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

export default function WatchlistPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      fetchWatchlist();
    }
  }, [user, authLoading, router]);

  const fetchWatchlist = async () => {
    try {
      const res = await api.get('/watchlist');
      setMovies(res.data || []);
    } catch (err) {
      console.error('Failed to fetch watchlist:', err);
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchlist = async (movieId: number) => {
    try {
      await api.delete(`/watchlist/${movieId}`);
      setMovies(movies.filter(m => m.id !== movieId));
    } catch (err) {
      console.error('Failed to remove from watchlist:', err);
    }
  };

  if (authLoading || (!user && !authLoading)) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold mb-8">My Watchlist</h1>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-xl">Loading your watchlist...</div>
            </div>
          ) : movies.length > 0 ? (
            <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
              {movies.map((movie) => (
                <div key={movie.id} className="relative group">
                  <MovieCard movie={movie} />
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      removeFromWatchlist(movie.id);
                    }}
                    className="absolute top-2 right-2 p-2 bg-black/70 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                    title="Remove from watchlist"
                  >
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📋</div>
              <p className="text-zinc-500 text-lg">Your watchlist is empty</p>
              <p className="text-zinc-600 mt-2">Browse movies and add them to your list</p>
              <button
                onClick={() => router.push('/')}
                className="mt-6 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-md font-semibold"
              >
                Browse Movies
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
