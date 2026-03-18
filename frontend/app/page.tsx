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
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);

  const [errorDetails, setErrorDetails] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log("Page: Fetching movies...");
        // Fetch popular movies (or just all movies for now)
        const moviesRes = await api.get('/movies?page=0&size=20');
        console.log("Page: Movies fetched:", moviesRes.data);
        // Backend returns Page<Movie>, so content is in moviesRes.data.content
        setPopularMovies(moviesRes.data.content || []);

        if (user) {
          try {
            console.log("Page: Fetching recommendations for user:", user);
            const recRes = await api.get('/recommendations/for-you');
            console.log("Page: Recommendations received:", recRes.data);
            setRecommendations(recRes.data || []);
          } catch (recError) {
            console.error('Failed to fetch recommendations', recError);
          }
        } else {
          console.log("Page: No user, skipping recommendations");
        }
      } catch (error: any) {
        console.error('Failed to fetch movies', error);
        setErrorDetails(error.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading) {
      fetchData();
    } else {
        console.log("Page: Waiting for auth...");
    }
  }, [user, authLoading]);

  // Loading state
  if (authLoading || (loading && popularMovies.length === 0)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-white flex-col gap-4">
        <h2 className="text-xl font-bold animate-pulse">Loading CineStream...</h2>
        <div className="text-sm text-zinc-400 flex flex-col items-center gap-1">
          <span>Auth Status: <span className={authLoading ? "text-yellow-500" : "text-green-500"}>{authLoading ? 'Checking...' : 'Ready'}</span></span>
          <span>Movie Data: <span className={loading ? "text-yellow-500" : "text-green-500"}>{loading ? 'Fetching...' : 'Ready'}</span></span>
          <span>Items Loaded: {popularMovies.length}</span>
        </div>
        {errorDetails && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded text-red-200 max-w-md text-center">
            <p className="font-bold">Error Loading Data</p>
            <p className="text-xs mt-1 font-mono">{errorDetails}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-500 rounded text-sm font-semibold"
            >
              Retry
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white selection:bg-red-500 selection:text-white">
      <Navbar />

      <main>
        {/* Hero Section */}
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
                  <Link href="/register" className="rounded-md bg-red-600 px-8 py-3.5 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600">
                    Get Started
                  </Link>
                </div>
             </div>
          </div>
        )}

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-20">
          
          {/* Recommendations Section - Only if logged in and has recommendations */}
          {user && recommendations.length > 0 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-white mb-6">Recommended for You</h2>
              <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 sm:gap-x-6 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
                {recommendations.map((movie) => (
                  <MovieCard key={movie.id} movie={movie} />
                ))}
              </div>
            </div>
          )}

          {/* Popular / All Movies Section */}
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-white mb-6">
              {user ? 'Popular Movies' : 'Trending Now'}
            </h2>
             {popularMovies.length > 0 ? (
                <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 sm:gap-x-6 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
                  {popularMovies.map((movie) => (
                    <MovieCard key={movie.id} movie={movie} />
                  ))}
                </div>
             ) : (
                <p className="text-zinc-500">No movies found.</p>
             )}
          </div>

        </div>
      </main>
    </div>
  );
}
