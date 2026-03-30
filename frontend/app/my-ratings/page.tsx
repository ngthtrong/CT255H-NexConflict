'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import { useAuth } from '../lib/authContext';
import api from '../lib/api';

interface RatingWithMovie {
  id: number;
  movieId: number;
  rating: number;
  movie?: {
    id: number;
    title: string;
    genres: string;
    posterUrl: string | null;
  };
}

export default function MyRatingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [ratings, setRatings] = useState<RatingWithMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [showConfirm, setShowConfirm] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      fetchRatings();
    }
  }, [user, authLoading, router]);

  const fetchRatings = async () => {
    try {
      // Get user ratings
      const ratingsRes = await api.get('/ratings/user');
      const ratingsData = ratingsRes.data || [];

      // Fetch movie details for each rating
      const ratingsWithMovies = await Promise.all(
        ratingsData.map(async (r: RatingWithMovie) => {
          try {
            const movieRes = await api.get(`/movies/${r.movieId}`);
            return { ...r, movie: movieRes.data };
          } catch {
            return r;
          }
        })
      );

      setRatings(ratingsWithMovies);
    } catch (err) {
      console.error('Failed to fetch ratings:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteRating = async (ratingId: number) => {
    setDeletingId(ratingId);
    try {
      await api.delete(`/ratings/${ratingId}`);
      setRatings(ratings.filter(r => r.id !== ratingId));
      setShowConfirm(null);
    } catch (err) {
      console.error('Failed to delete rating:', err);
      alert('Không thể xóa đánh giá. Vui lòng thử lại.');
    } finally {
      setDeletingId(null);
    }
  };

  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    const stars = [];

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={`full-${i}`} className="text-yellow-400">★</span>);
    }
    if (hasHalf) {
      stars.push(<span key="half" className="text-yellow-400">½</span>);
    }
    for (let i = stars.length; i < 5; i++) {
      stars.push(<span key={`empty-${i}`} className="text-zinc-600">★</span>);
    }

    return stars;
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
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold">Đánh giá của tôi</h1>
            <span className="text-zinc-400">{ratings.length} đánh giá</span>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-xl">Đang tải đánh giá...</div>
            </div>
          ) : ratings.length > 0 ? (
            <div className="space-y-4">
              {ratings.map((item) => (
                <div
                  key={item.id}
                  className="bg-zinc-900 rounded-lg p-4 flex items-center gap-4 hover:bg-zinc-800 transition-colors"
                >
                  {/* Poster */}
                  <Link href={`/movies/${item.movieId}`} className="flex-shrink-0">
                    {item.movie?.posterUrl ? (
                      <img
                        src={item.movie.posterUrl}
                        alt={item.movie?.title || 'Movie'}
                        className="w-16 h-24 object-cover rounded"
                      />
                    ) : (
                      <div className="w-16 h-24 bg-gradient-to-br from-red-600 to-purple-600 rounded flex items-center justify-center">
                        <span className="text-2xl">🎬</span>
                      </div>
                    )}
                  </Link>

                  {/* Movie Info */}
                  <div className="flex-grow min-w-0">
                    <Link href={`/movies/${item.movieId}`} className="hover:text-red-500 transition-colors">
                      <h3 className="font-semibold text-lg truncate">
                        {item.movie?.title || `Movie #${item.movieId}`}
                      </h3>
                    </Link>
                    {item.movie?.genres && (
                      <p className="text-zinc-400 text-sm truncate mt-1">
                        {item.movie.genres.split('|').join(' • ')}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-lg">{renderStars(item.rating)}</span>
                      <span className="text-zinc-400 text-sm">({item.rating.toFixed(1)})</span>
                    </div>
                  </div>

                  {/* Delete Button */}
                  <div className="flex-shrink-0">
                    {showConfirm === item.id ? (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => deleteRating(item.id)}
                          disabled={deletingId === item.id}
                          className="px-3 py-1.5 bg-red-600 hover:bg-red-500 disabled:bg-red-800 text-white text-sm rounded transition-colors"
                        >
                          {deletingId === item.id ? '...' : 'Xóa'}
                        </button>
                        <button
                          onClick={() => setShowConfirm(null)}
                          className="px-3 py-1.5 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded transition-colors"
                        >
                          Hủy
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setShowConfirm(item.id)}
                        className="p-2 text-zinc-400 hover:text-red-500 hover:bg-zinc-700 rounded transition-colors"
                        title="Xóa đánh giá"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">⭐</div>
              <p className="text-zinc-500 text-lg">Bạn chưa đánh giá phim nào</p>
              <p className="text-zinc-600 mt-2">Xem phim và đánh giá để nhận gợi ý tốt hơn</p>
              <button
                onClick={() => router.push('/')}
                className="mt-6 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-md font-semibold"
              >
                Khám phá phim
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
