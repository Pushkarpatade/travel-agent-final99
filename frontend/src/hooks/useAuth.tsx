import React, { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User } from '../types';
import { authService } from '../services/api';
import { signInWithGoogle } from '../services/firebase';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  sendOtp: (email: string) => Promise<any>;
  verifyOtp: (email: string, otp: string, fullName?: string, password?: string) => Promise<void>;
  firebaseLogin: (email: string, fullName: string) => Promise<void>;
  googleSignIn: () => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('tp_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('tp_auth_token'));
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Auto-authentication on load: verify active token with backend
  useEffect(() => {
    const restoreSession = async () => {
      const savedToken = localStorage.getItem('tp_auth_token');
      if (savedToken) {
        try {
          const freshUser = await authService.getMe();
          setUser(freshUser);
          localStorage.setItem('tp_user', JSON.stringify(freshUser));
        } catch {
          // Token expired or invalid
          logout();
        }
      }
    };
    restoreSession();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('tp_auth_token', data.access_token);
      localStorage.setItem('tp_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    setIsLoading(true);
    try {
      const data = await authService.register(email, password, fullName);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('tp_auth_token', data.access_token);
      localStorage.setItem('tp_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const sendOtp = async (email: string) => {
    return await authService.sendOtp(email);
  };

  const verifyOtp = async (email: string, otp: string, fullName?: string, password?: string) => {
    setIsLoading(true);
    try {
      const data = await authService.verifyOtp(email, otp, fullName, password);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('tp_auth_token', data.access_token);
      localStorage.setItem('tp_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const firebaseLogin = async (email: string, fullName: string) => {
    setIsLoading(true);
    try {
      const data = await authService.firebaseLogin(email, fullName);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('tp_auth_token', data.access_token);
      localStorage.setItem('tp_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const googleSignIn = async () => {
    setIsLoading(true);
    try {
      const result = await signInWithGoogle();
      setToken(result.token);
      setUser(result.user);
      localStorage.setItem('tp_auth_token', result.token);
      localStorage.setItem('tp_user', JSON.stringify(result.user));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('tp_auth_token');
    localStorage.removeItem('tp_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, sendOtp, verifyOtp, firebaseLogin, googleSignIn, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
