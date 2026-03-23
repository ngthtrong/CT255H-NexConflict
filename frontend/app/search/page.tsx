'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import api from '../lib/api';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';

  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    if (query) {
      searchMovies(query, 0);
    }
  }, [query]);

  const searchMovies = async (searchQuery: string, page: number) => {
    setLoading(true);
    try {
      const res = await api.get(`/movies?title=${encodeURIComponent(searchQuery)}&page=${page}&size=20`);
      setMovies(res.data.content || []);
      setTotalPages(res.data.totalPages || 0);
      setCurrentPage(page);
    } catch (err) {
      console.error('Search failed:', err);
      setMovies([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 0 && newPage < totalPages) {
      searchMovies(query, newPage);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold mb-2">Search Results</h1>
          {query && (
            <p className="text-zinc-400 mb-8">
              Showing results for: <span className="text-white font-medium">"{query}"</span>
            </p>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-xl">Searching...</div>
            </div>
          ) : movies.length > 0 ? (
            <>
              <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:gap-x-8">
                {movies.map((movie) => (
                  <MovieCard key={movie.id} movie={movie} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center gap-4 mt-12">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 0}
                    className="px-4 py-2 bg-zinc-800 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-700"
                  >
                    Previous
                  </button>
                  <span className="text-zinc-400">
                    Page {currentPage + 1} of {totalPages}
                  </span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage >= totalPages - 1}
                    className="px-4 py-2 bg-zinc-800 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-700"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : query ? (
            <div className="text-center py-20">
              <p className="text-zinc-500 text-lg">No movies found for "{query}"</p>
              <p className="text-zinc-600 mt-2">Try a different search term</p>
            </div>
          ) : (
            <div className="text-center py-20">
              <p className="text-zinc-500 text-lg">Enter a search term to find movies</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
