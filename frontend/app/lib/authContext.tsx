// authContext.tsx
"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from './api';

interface User {
  id: number;
  email: string;
  fullName: string;
  username?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => false,
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    console.log("AuthContext: Mounting...");
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    if (token) {
      console.log("AuthContext: Token found, fetching profile...");
      fetchUserProfile();
    } else {
      console.log("AuthContext: No token, loading false.");
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (): Promise<boolean> => {
    try {
      const res = await api.get('/users/me');
      const userData = res.data;
      console.log("AuthContext: User profile fetched:", userData);
      setUser({
        id: userData.id,
        email: userData.email,
        fullName: userData.fullName,
        username: userData.fullName || userData.email.split('@')[0]
      });
      return true;
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      localStorage.removeItem('token');
      setUser(null);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const login = async (token: string): Promise<boolean> => {
    console.log("AuthContext: Login called, saving token...");
    localStorage.setItem('token', token);
    setLoading(true);
    const success = await fetchUserProfile();
    console.log("AuthContext: Login result:", success);
    return success;
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
