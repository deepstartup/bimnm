import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

const TOKEN_KEY = 'token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get('/api/auth/me');
      setUser(data);
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (username, password) => {
    const { data } = await api.post('/api/auth/login', { username, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
    await loadUser();
    return data;
  };

  const register = async (username, email, password) => {
    await api.post('/api/auth/register', { username, email, password });
    return login(username, password);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
