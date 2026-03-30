'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import { useAuth } from '../lib/authContext';
import api from '../lib/api';

const ALL_GENRES = [
  'Action', 'Adventure', 'Animation', 'Children', 'Comedy',
  'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
  'Horror', 'IMAX', 'Musical', 'Mystery', 'Romance',
  'Sci-Fi', 'Thriller', 'War', 'Western'
];

export default function SettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [originalGenres, setOriginalGenres] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      fetchPreferences();
    }
  }, [user, authLoading, router]);

  const fetchPreferences = async () => {
    try {
      const res = await api.get('/onboarding/my-preferences');
      const genres = res.data.genres || [];
      setSelectedGenres(genres);
      setOriginalGenres(genres);
    } catch (err) {
      console.error('Failed to fetch preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
    setMessage(null);
  };

  const hasChanges = () => {
    if (selectedGenres.length !== originalGenres.length) return true;
    return selectedGenres.some(g => !originalGenres.includes(g));
  };

  const saveGenres = async () => {
    if (selectedGenres.length < 3) {
      setMessage({ type: 'error', text: 'Vui lòng chọn ít nhất 3 thể loại' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      await api.put('/onboarding/update-genres', { genres: selectedGenres });
      setOriginalGenres([...selectedGenres]);
      setMessage({ type: 'success', text: 'Đã cập nhật thể loại yêu thích!' });
    } catch (err: any) {
      console.error('Failed to save genres:', err);
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Không thể cập nhật. Vui lòng thử lại.' 
      });
    } finally {
      setSaving(false);
    }
  };

  const resetGenres = () => {
    setSelectedGenres([...originalGenres]);
    setMessage(null);
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
          <div className="mb-8">
            <h1 className="text-3xl font-bold">Cài đặt</h1>
            <p className="text-zinc-400 mt-2">Quản lý tùy chọn cá nhân của bạn</p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-xl">Đang tải...</div>
            </div>
          ) : (
            <div className="bg-zinc-900 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold">Thể loại yêu thích</h2>
                  <p className="text-zinc-400 text-sm mt-1">
                    Chọn ít nhất 3 thể loại để nhận gợi ý phim phù hợp hơn
                  </p>
                </div>
                <span className="text-sm text-zinc-400">
                  Đã chọn: <span className={selectedGenres.length >= 3 ? 'text-green-400' : 'text-red-400'}>{selectedGenres.length}</span>/19
                </span>
              </div>

              {/* Genre Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mb-6">
                {ALL_GENRES.map((genre) => {
                  const isSelected = selectedGenres.includes(genre);
                  return (
                    <button
                      key={genre}
                      onClick={() => toggleGenre(genre)}
                      className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                        isSelected
                          ? 'bg-red-600 text-white ring-2 ring-red-400'
                          : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                      }`}
                    >
                      {genre}
                      {isSelected && <span className="ml-2">✓</span>}
                    </button>
                  );
                })}
              </div>

              {/* Message */}
              {message && (
                <div className={`p-4 rounded-lg mb-6 ${
                  message.type === 'success' 
                    ? 'bg-green-900/50 border border-green-700 text-green-200' 
                    : 'bg-red-900/50 border border-red-700 text-red-200'
                }`}>
                  {message.text}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
                <div className="flex gap-3">
                  <button
                    onClick={saveGenres}
                    disabled={saving || !hasChanges() || selectedGenres.length < 3}
                    className="px-6 py-2.5 bg-red-600 hover:bg-red-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-lg font-medium transition-colors"
                  >
                    {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
                  </button>
                  {hasChanges() && (
                    <button
                      onClick={resetGenres}
                      className="px-6 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-medium transition-colors"
                    >
                      Hoàn tác
                    </button>
                  )}
                </div>
                <Link
                  href="/my-ratings"
                  className="text-zinc-400 hover:text-white text-sm transition-colors"
                >
                  Xem đánh giá của tôi →
                </Link>
              </div>
            </div>
          )}

          {/* Quick Links */}
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              href="/my-ratings"
              className="bg-zinc-900 rounded-xl p-6 hover:bg-zinc-800 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <span className="text-3xl">⭐</span>
                <div>
                  <h3 className="font-semibold group-hover:text-red-500 transition-colors">Đánh giá của tôi</h3>
                  <p className="text-zinc-400 text-sm">Xem và quản lý các đánh giá phim</p>
                </div>
              </div>
            </Link>
            <Link
              href="/watchlist"
              className="bg-zinc-900 rounded-xl p-6 hover:bg-zinc-800 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <span className="text-3xl">📋</span>
                <div>
                  <h3 className="font-semibold group-hover:text-red-500 transition-colors">Danh sách xem sau</h3>
                  <p className="text-zinc-400 text-sm">Phim bạn muốn xem sau</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
