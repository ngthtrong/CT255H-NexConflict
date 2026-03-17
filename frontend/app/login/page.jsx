"use client";

import { useState } from "react";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    console.log("Login credentials:", { email, password });
    // TODO: Thêm logic gọi API Login của SpringBoot ở đây
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative bg-black overflow-hidden font-sans text-white">
      {/* Background simulation (radial gradient to simulate spotlight) */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-800/40 via-black to-black opacity-80 z-0"></div>

      {/* Header / Logo */}
      <div className="z-10 mb-10 text-center flex flex-col items-center">
        <h1 className="text-[2.5rem] font-bold text-white tracking-tight drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">
          CineStream
        </h1>
        <p className="text-[0.65rem] text-zinc-400 tracking-[0.25em] mt-1.5 font-medium uppercase">
          Private Screening Access
        </p>
      </div>

      {/* Login Card */}
      <div className="z-10 w-full max-w-[400px] bg-[#121212] rounded-2xl p-8 shadow-2xl border border-white/5 mx-4">
        <h2 className="text-2xl font-semibold text-white mb-1">Sign In</h2>
        <p className="text-[13px] text-zinc-400 mb-8">Access your curated cinematic library.</p>

        <form onSubmit={handleLogin}>
          {/* Email */}
          <div className="mb-5">
            <label className="block text-[10px] font-bold text-zinc-500 tracking-wider mb-2 uppercase">
              Email Address
            </label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full bg-[#1A1A1A] text-white text-sm rounded-lg px-4 py-3.5 outline-none focus:ring-1 focus:ring-red-600 transition-all placeholder:text-zinc-600 border border-transparent focus:border-red-600/30"
              />
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute right-4 top-3.5 text-zinc-600 w-5 h-5 pointer-events-none">
                <rect width="20" height="16" x="2" y="4" rx="2" />
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
              </svg>
            </div>
          </div>

          {/* Password */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <label className="text-[10px] font-bold text-zinc-500 tracking-wider uppercase">
                Password
              </label>
              <a href="#" className="text-[10px] text-red-500 font-bold hover:text-red-400 transition-colors">
                Forgot Password?
              </a>
            </div>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#1A1A1A] text-white text-sm rounded-lg px-4 py-3.5 outline-none focus:ring-1 focus:ring-red-600 transition-all placeholder:text-zinc-600 tracking-widest border border-transparent focus:border-red-600/30"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-3.5 text-zinc-600 hover:text-zinc-400 focus:outline-none"
              >
                {showPassword ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                    <line x1="2" x2="22" y1="2" y2="22" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button type="submit" className="w-full bg-[#E50914] hover:bg-red-700 text-white text-sm font-semibold py-3.5 rounded-lg flex items-center justify-center gap-2 transition-colors mb-7 shadow-[0_0_15px_rgba(229,9,20,0.25)]">
            Sign In 
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 ml-1">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
              <polyline points="10 17 15 12 10 7" />
              <line x1="15" x2="3" y1="12" y2="12" />
            </svg>
          </button>

          {/* Create Account Link */}
          <p className="text-center text-[12px] text-zinc-400">
            New to CineStream? <a href="#" className="text-white font-semibold hover:underline underline-offset-4 decoration-white/50">Create Account</a>
          </p>
        </form>
      </div>

      {/* Bottom Footer */}
      <div className="absolute bottom-6 flex gap-6 text-[8px] tracking-[0.15em] text-zinc-600 font-bold uppercase z-10 w-full justify-center">
        <a href="#" className="hover:text-zinc-400 transition-colors">Privacy Policy</a>
        <a href="#" className="hover:text-zinc-400 transition-colors">Terms of Service</a>
        <a href="#" className="hover:text-zinc-400 transition-colors">Help Center</a>
      </div>
    </div>
  );
}
