// Navbar - Top Navigation

'use client';

import Link from 'next/link';
import { useAuth } from '../lib/authContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-zinc-800 bg-black/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold text-red-600">
            CineStream
          </Link>
          <div className="hidden md:flex gap-6">
            <Link href="/" className="text-sm font-medium text-zinc-300 hover:text-white">
              Home
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-zinc-400">Hi, {user.username}</span>
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
        </div>
      </div>
    </nav>
  );
}
