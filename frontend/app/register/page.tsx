'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '../lib/api';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await api.post('/auth/register', {
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password
      });
      // Register successful, redirect to login
      router.push('/login?registered=true');
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-zinc-900 p-10 shadow-2xl border border-zinc-800">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-red-600">CineStream</h2>
          <p className="mt-2 text-sm text-zinc-400">Create your account</p>
        </div>

        {error && (
          <div className="rounded-md bg-red-900/50 p-3 text-sm text-red-200 border border-red-800">
            {error}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="fullName" className="sr-only">Full Name</label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                required
                className="relative block w-full rounded-md border-0 bg-zinc-800 py-2.5 text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 sm:text-sm sm:leading-6"
                placeholder="Full Name"
                value={formData.fullName}
                onChange={handleChange}
              />
            </div>
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="relative block w-full rounded-md border-0 bg-zinc-800 py-2.5 text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 sm:text-sm sm:leading-6"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
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
                value={formData.password}
                onChange={handleChange}
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="sr-only">Confirm Password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="relative block w-full rounded-md border-0 bg-zinc-800 py-2.5 text-white placeholder-zinc-500 ring-1 ring-inset ring-zinc-700 focus:ring-2 focus:ring-red-600 sm:text-sm sm:leading-6"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative flex w-full justify-center rounded-md bg-red-600 px-3 py-2.5 text-sm font-semibold text-white hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-zinc-400">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-red-500 hover:text-red-400">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
