'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../lib/authContext';
import api from '../lib/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data && response.data.accessToken) {
        const success = await login(response.data.accessToken);
        if (success) {
          // Check onboarding status and redirect accordingly
          try {
            const statusRes = await api.get('/onboarding/status');
            if (!statusRes.data.onboardingCompleted) {
              router.push('/onboarding');
            } else {
              router.push('/');
            }
          } catch {
            router.push('/');
          }
        } else {
          setError('Login failed: Could not fetch user profile');
        }
      } else {
        setError('Login failed: No token received');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.message || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-zinc-900 p-10 shadow-2xl border border-zinc-800">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-red-600">CineStream</h2>
          <p className="mt-2 text-sm text-zinc-400">Sign in to your account</p>
        </div>

        {error && (
          <div className="rounded-md bg-red-900/50 p-3 text-sm text-red-200 border border-red-800">
            {error}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="sr-only">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="relative block w-full rounded-md border-0 bg-zinc-800 py-2.5 text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 sm:text-sm sm:leading-6"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="relative block w-full rounded-md border-0 bg-zinc-800 py-2.5 text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 sm:text-sm sm:leading-6"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative flex w-full justify-center rounded-md bg-red-600 px-3 py-2.5 text-sm font-semibold text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-zinc-400">
          Not a member?{' '}
          <Link href="/register" className="font-semibold text-red-500 hover:text-red-400">
            Start a 14 day free trial
          </Link>
        </p>
      </div>
    </div>
  );
}
