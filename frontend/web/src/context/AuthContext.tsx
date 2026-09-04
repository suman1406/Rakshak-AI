import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, UserRole } from '../types';
import { apiClient } from '../services/apiClient';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (emailOrPhone: string, password: string) => Promise<UserRole>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const WEB_ROLES: UserRole[] = ['agronomist', 'org_admin', 'admin', 'enterprise'];
const TOKEN_KEY = 'rakshak_ai_access_token';
const isWebRole = (value: string): value is UserRole => WEB_ROLES.includes(value as UserRole);

const toUser = (account: { id: string; email?: string; phone?: string; role: UserRole; org_id?: string; display_name?: string }): User => ({
  id: account.id,
  name: account.display_name || account.email || account.phone || 'Workspace member',
  email: account.email || account.phone || '',
  role: account.role,
  // The API currently returns an organization identifier for authorization;
  // it is not a human-facing organization name and must never be rendered.
  organization: account.org_id ? 'Organization workspace' : undefined,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_KEY);
    if (!token || !apiClient.isConfigured()) {
      setIsLoading(false);
      return;
    }
    apiClient.getCurrentUser()
      .then((account) => {
        if (isWebRole(account.role)) setUser(toUser(account));
        else apiClient.logout();
      })
      .catch(() => {
        apiClient.logout();
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (emailOrPhone: string, password: string): Promise<UserRole> => {
    if (!apiClient.isConfigured()) throw new Error('Authentication service is not configured. Set NEXT_PUBLIC_API_URL and try again.');
    const session = await apiClient.login(emailOrPhone.trim(), password);
    if (!isWebRole(session.role)) {
      apiClient.logout();
      throw new Error('This account is assigned to the farmer mobile app.');
    }
    const account = await apiClient.getCurrentUser();
    if (!isWebRole(account.role)) {
      apiClient.logout();
      throw new Error('This account is not authorized for the web workspace.');
    }
    setUser(toUser(account));
    return account.role;
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, role: user?.role || null, isAuthenticated: !!user, isLoading, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
