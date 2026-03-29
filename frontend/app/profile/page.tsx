'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import { useAuth } from '../lib/authContext';
import api from '../lib/api';

interface RatingItem {
  id: number;
  movieId: number;
  rating: number;
}

interface Movie {
  id: number;
  title: string;
  genres: string;
}

export default function ProfilePage() {
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [ratings, setRatings] = useState<(RatingItem & { movie?: Movie })[]>([]);
  const [watchlistCount, setWatchlistCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      fetchProfileData();
    }
  }, [user, authLoading, router]);

  const fetchProfileData = async () => {
    try {
      // Fetch user ratings
      const ratingsRes = await api.get('/ratings/user');
      const userRatings = ratingsRes.data || [];

      // Fetch movie details for each rating
      const ratingsWithMovies = await Promise.all(
        userRatings.map(async (rating: RatingItem) => {
          try {
            const movieRes = await api.get(`/movies/${rating.movieId}`);
            return { ...rating, movie: movieRes.data };
          } catch {
            return rating;
          }
        })
      );

      setRatings(ratingsWithMovies);

      // Fetch watchlist count
      try {
        const watchlistRes = await api.get('/watchlist');
        setWatchlistCount(watchlistRes.data?.length || 0);
      } catch {
        setWatchlistCount(0);
      }
    } catch (err) {
      console.error('Failed to fetch profile data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateName = async () => {
    if (!newName.trim()) return;

    try {
      await api.put('/users/me', { fullName: newName.trim() });
      setEditingName(false);
      window.location.reload();
    } catch (err) {
      console.error('Failed to update name:', err);
      alert('Failed to update name');
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
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          {/* Profile Header */}
          <div className="bg-zinc-900 rounded-xl p-8 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 rounded-full bg-red-600 flex items-center justify-center text-3xl font-bold">
                  {user?.fullName?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase()}
                </div>
                <div>
                  {editingName ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        placeholder={user?.fullName || 'Enter name'}
                        className="bg-zinc-800 rounded px-3 py-1 text-white"
                        autoFocus
                      />
                      <button
                        onClick={handleUpdateName}
                        className="px-3 py-1 bg-green-600 rounded text-sm"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingName(false)}
                        className="px-3 py-1 bg-zinc-700 rounded text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                      {user?.fullName || 'User'}
                      <button
                        onClick={() => {
                          setNewName(user?.fullName || '');
                          setEditingName(true);
                        }}
                        className="text-zinc-500 hover:text-white"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                    </h1>
                  )}
                  <p className="text-zinc-400">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-md text-sm"
              >
                Sign Out
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mt-8">
              <div className="bg-zinc-800 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-red-500">{ratings.length}</div>
                <div className="text-zinc-400 text-sm">Movies Rated</div>
              </div>
              <Link href="/watchlist" className="bg-zinc-800 hover:bg-zinc-700 rounded-lg p-4 text-center transition-colors">
                <div className="text-3xl font-bold text-red-500">{watchlistCount}</div>
                <div className="text-zinc-400 text-sm">In Watchlist</div>
              </Link>
            </div>
          </div>

          {/* My Ratings */}
          <div className="bg-zinc-900 rounded-xl p-8">
            <h2 className="text-xl font-bold mb-6">My Ratings</h2>

            {loading ? (
              <div className="text-center py-8 text-zinc-500">Loading...</div>
            ) : ratings.length > 0 ? (
              <div className="space-y-4">
                {ratings.map((item) => (
                  <div key={item.id} className="flex items-center justify-between bg-zinc-800 rounded-lg p-4">
                    <Link href={`/movies/${item.movieId}`} className="flex-1 hover:text-red-500 transition-colors">
                      <div className="font-medium">{item.movie?.title || `Movie #${item.movieId}`}</div>
                      {item.movie?.genres && (
                        <div className="text-sm text-zinc-400">{item.movie.genres.replace(/\|/g, ', ')}</div>
                      )}
                    </Link>
                    <div className="flex items-center gap-1 text-yellow-400">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <span key={star} className={star <= item.rating ? 'text-yellow-400' : 'text-zinc-600'}>
                          ★
                        </span>
                      ))}
                      <span className="ml-2 text-white">{item.rating}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-zinc-500">You haven't rated any movies yet</p>
                <button
                  onClick={() => router.push('/')}
                  className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 rounded-md text-sm"
                >
                  Browse Movies
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
