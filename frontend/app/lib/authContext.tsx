// authContext.tsx
"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from './api';

interface User {
  id: number;
  email: string;
  fullName: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    console.log("AuthContext: Mounting...");
    // Check local storage for token on mount
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    if (token) {
      console.log("AuthContext: Token found, fetching profile...");
      fetchUserProfile();
    } else {
      console.log("AuthContext: No token, loading false.");
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      // If we had a /users/me endpoint:
      // const res = await api.get('/users/me');
      // setUser(res.data);
      setUser({ id: 1, email: 'user@example.com', fullName: 'User' }); // Mock
    } catch (err) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = (token: string) => {
    localStorage.setItem('token', token);
    fetchUserProfile();
    router.push('/');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
