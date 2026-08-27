import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { DEMO_USERS } from '../data/mockData';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isDemoMode: boolean;
  login: (roleChoice: UserRole, customEmail?: string) => void;
  logout: () => void;
  switchRole: (newRole: UserRole) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const LOCAL_STORAGE_KEY_ROLE = 'rakshak_ai_demo_role';
const LOCAL_STORAGE_KEY_USER = 'rakshak_ai_demo_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    /*
     * FUTURE FASTAPI INTEGRATION:
     * Check valid JWT access token from localStorage or cookie.
     * Fetch GET /api/v1/auth/me to populate current user profile & role permissions.
     */
    const savedUser = localStorage.getItem(LOCAL_STORAGE_KEY_USER);
    const savedRole = localStorage.getItem(LOCAL_STORAGE_KEY_ROLE) as UserRole | null;
    if (savedUser && savedRole) {
      try {
        return JSON.parse(savedUser);
      } catch {
        return DEMO_USERS[savedRole] || DEMO_USERS.farmer;
      }
    }
    return null;
  });

  const [role, setRole] = useState<UserRole | null>(() => {
    return (localStorage.getItem(LOCAL_STORAGE_KEY_ROLE) as UserRole) || (user?.role ?? null);
  });

  useEffect(() => {
    if (user && role) {
      localStorage.setItem(LOCAL_STORAGE_KEY_USER, JSON.stringify(user));
      localStorage.setItem(LOCAL_STORAGE_KEY_ROLE, role);
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY_USER);
      localStorage.removeItem(LOCAL_STORAGE_KEY_ROLE);
    }
  }, [user, role]);

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * Login handler will post credentials to POST /api/v1/auth/login
   * Returns JWT Token -> Authorization: Bearer <token>
   */
  const login = (roleChoice: UserRole, customEmail?: string) => {
    const baseUser = DEMO_USERS[roleChoice] || DEMO_USERS.farmer;
    const loggedInUser: User = {
      ...baseUser,
      email: customEmail && customEmail.trim() ? customEmail : baseUser.email,
      role: roleChoice,
    };
    setUser(loggedInUser);
    setRole(roleChoice);
  };

  const switchRole = (newRole: UserRole) => {
    login(newRole);
  };

  const logout = () => {
    /*
     * FUTURE FASTAPI INTEGRATION POINT:
     * Call POST /api/v1/auth/logout to invalidate refreshToken and clear session cookies.
     */
    setUser(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        isDemoMode: true, // Always true for this prototype
        login,
        logout,
        switchRole,
      }}
    >
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
