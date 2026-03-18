'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../lib/authContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-zinc-800 bg-black/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo and Nav Links */}
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold text-red-600">
            CineStream
          </Link>
          <div className="hidden md:flex gap-6">
            <Link href="/" className="text-sm font-medium text-zinc-300 hover:text-white">
              Home
            </Link>
            {user && (
              <>
                <Link href="/watchlist" className="text-sm font-medium text-zinc-300 hover:text-white">
                  My List
                </Link>
                <Link href="/profile" className="text-sm font-medium text-zinc-300 hover:text-white">
                  Profile
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Search and User Section */}
        <div className="flex items-center gap-4">
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="hidden sm:block">
            <div className="relative">
              <input
                type="text"
                placeholder="Search movies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 lg:w-64 rounded-md border-0 bg-zinc-800 py-1.5 pl-3 pr-10 text-sm text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 transition-all"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </form>

          {/* User Section */}
          {user ? (
            <div className="flex items-center gap-3">
              <Link href="/profile" className="text-sm text-zinc-400 hover:text-white hidden sm:block">
                Hi, {user.username || user.fullName}
              </Link>
              <button
                onClick={logout}
                className="rounded-md bg-zinc-800 px-3 py-1.5 text-xs font-semibold text-white hover:bg-zinc-700"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Link href="/login" className="rounded-md px-3 py-1.5 text-sm font-medium text-zinc-300 hover:text-white">
                Login
              </Link>
              <Link href="/register" className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700">
                Sign Up
              </Link>
            </div>
          )}

          {/* Mobile Menu Button */}
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="md:hidden text-zinc-400 hover:text-white"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {showMobileMenu && (
        <div className="md:hidden border-t border-zinc-800 bg-black/95 px-4 py-4">
          <form onSubmit={handleSearch} className="mb-4">
            <input
              type="text"
              placeholder="Search movies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-md border-0 bg-zinc-800 py-2 pl-3 pr-10 text-sm text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600"
            />
          </form>
          <div className="flex flex-col gap-3">
            <Link href="/" className="text-sm font-medium text-zinc-300 hover:text-white" onClick={() => setShowMobileMenu(false)}>
              Home
            </Link>
            {user && (
              <>
                <Link href="/watchlist" className="text-sm font-medium text-zinc-300 hover:text-white" onClick={() => setShowMobileMenu(false)}>
                  My List
                </Link>
                <Link href="/profile" className="text-sm font-medium text-zinc-300 hover:text-white" onClick={() => setShowMobileMenu(false)}>
                  Profile
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
