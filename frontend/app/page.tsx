'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Navbar from './components/Navbar';
import MovieCard from './components/MovieCard';
import { useAuth } from './lib/authContext';
import api from './lib/api';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

export default function Home() {
  const { user, loading: authLoading } = useAuth();

  // State for different movie sections
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([]);
  const [topGenresMovies, setTopGenresMovies] = useState<Movie[]>([]);
  const [watchAgainMovies, setWatchAgainMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorDetails, setErrorDetails] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Check if user is logged in and onboarding completed
        const isOnboarded = user && user.onboardingCompleted;

        if (isOnboarded) {
          // Fetch personalized content for onboarded users
          const [recRes, genresRes, watchAgainRes] = await Promise.all([
            api.get('/recommendations/for-you').catch(() => ({ data: [] })),
            api.get('/recommendations/top-genres').catch(() => ({ data: [] })),
            api.get('/recommendations/watch-again').catch(() => ({ data: [] }))
          ]);

          setRecommendedMovies(recRes.data || []);
          setTopGenresMovies(genresRes.data || []);
          setWatchAgainMovies(watchAgainRes.data || []);
        } else {
          // Fetch trending movies for guests or non-onboarded users
          const trendingRes = await api.get('/recommendations/trending?limit=20');
          setTrendingMovies(trendingRes.data || []);
        }

      } catch (error: any) {
        console.error('Failed to fetch movies', error);
        setErrorDetails(error.message || 'Unknown error');

        // Fallback: try to get any movies
        try {
          const fallbackRes = await api.get('/movies?page=0&size=20');
          setTrendingMovies(fallbackRes.data.content || []);
        } catch {
          // ignore
        }
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading) {
      fetchData();
    }
  }, [user, authLoading]);

  // Determine if user should see personalized content
  const showPersonalized = user && user.onboardingCompleted;

  // Loading state
  if (authLoading || (loading && trendingMovies.length === 0 && recommendedMovies.length === 0)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-white flex-col gap-4">
        <h2 className="text-xl font-bold animate-pulse">Loading CineStream...</h2>
        {errorDetails && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded text-red-200 max-w-md text-center">
            <p className="font-bold">Error Loading Data</p>
            <p className="text-xs mt-1 font-mono">{errorDetails}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white selection:bg-red-500 selection:text-white">
      <Navbar />

      <main>
        {/* Hero Section - Only for guests */}
        {!user && (
          <div className="relative isolate overflow-hidden pt-14 text-center sm:pt-20 lg:pt-32 pb-16 sm:pb-24">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
                Unlimited movies, TV shows, and more
              </h1>
              <p className="mt-6 text-lg leading-8 text-zinc-300 max-w-2xl mx-auto">
                Watch anywhere. Cancel anytime. Ready to watch? Enter your email to create or restart your membership.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link href="/register" className="rounded-md bg-red-600 px-8 py-3.5 text-sm font-semibold text-white shadow-sm hover:bg-red-500">
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        )}

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-20">

          {/* === FOR GUESTS / NON-ONBOARDED: Show Trending === */}
          {!showPersonalized && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-red-500">🔥</span> Top Trending
              </h2>
              {trendingMovies.length > 0 ? (
                <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                  {trendingMovies.map((movie) => (
                    <MovieCard key={movie.id} movie={movie} />
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500">No movies found.</p>
              )}
            </div>
          )}

          {/* === FOR ONBOARDED USERS: Show 3 Personalized Rows === */}
          {showPersonalized && (
            <>
              {/* Row 1: Recommended For You (SVD / AI based) */}
              {recommendedMovies.length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-red-500">⭐</span> Recommended For You
                  </h2>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {recommendedMovies.map((movie) => (
                      <MovieCard key={movie.id} movie={movie} />
                    ))}
                  </div>
                </div>
              )}

              {/* Row 2: Top Genres (based on user's favorite genres from onboarding) */}
              {topGenresMovies.length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-red-500">🎬</span> From Your Favorite Genres
                  </h2>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {topGenresMovies.map((movie) => (
                      <MovieCard key={movie.id} movie={movie} />
                    ))}
                  </div>
                </div>
              )}

              {/* Row 3: Watch Again (movies user has rated) */}
              {watchAgainMovies.length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-red-500">🔄</span> Watch Again
                  </h2>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {watchAgainMovies.map((movie) => (
                      <MovieCard key={movie.id} movie={movie} />
                    ))}
                  </div>
                </div>
              )}

              {/* Fallback if no personalized content */}
              {recommendedMovies.length === 0 && topGenresMovies.length === 0 && watchAgainMovies.length === 0 && (
                <div className="mt-12 text-center py-12">
                  <p className="text-zinc-400 mb-4">
                    Start rating movies to get personalized recommendations!
                  </p>
                  <Link
                    href="/search"
                    className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-500"
                  >
                    Browse Movies
                  </Link>
                </div>
              )}
            </>
          )}

        </div>
      </main>
    </div>
  );
}
