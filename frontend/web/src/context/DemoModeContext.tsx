import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, DemoWorkspace } from '../services/apiClient';
import { useAuth } from './AuthContext';

type DemoModeContextValue = {
  enabled: boolean; available: boolean; loading: boolean; workspace: DemoWorkspace | null;
  setEnabled: (enabled: boolean) => void; refresh: () => Promise<void>;
};
const DemoModeContext = createContext<DemoModeContextValue | undefined>(undefined);
const STORAGE_KEY = 'rakshak_ai_development_demo_mode';

export const DemoModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [workspace, setWorkspace] = useState<DemoWorkspace | null>(null);
  const [loading, setLoading] = useState(false);
  const [enabled, setEnabledState] = useState(false);

  const refresh = async () => {
    if (!isAuthenticated) {
      setWorkspace(null);
      setEnabledState(false);
      if (typeof window !== 'undefined') {
        window.sessionStorage.removeItem(STORAGE_KEY);
      }
      return;
    }
    setLoading(true);
    try {
      const data = await apiClient.getDemoWorkspace();
      setWorkspace(data);
    } catch {
      setWorkspace(null);
      setEnabledState(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, [isAuthenticated]);

  useEffect(() => {
    if (!workspace?.available || !isAuthenticated) {
      setEnabledState(false);
      return;
    }
    const saved = window.sessionStorage.getItem(STORAGE_KEY);
    if (saved === 'false') {
      setEnabledState(false);
    } else {
      // Default to ON if available and user hasn't explicitly chosen 'false'
      setEnabledState(true);
      if (saved !== 'true') {
        window.sessionStorage.setItem(STORAGE_KEY, 'true');
      }
    }
  }, [workspace?.available, isAuthenticated]);

  const setEnabled = (next: boolean) => {
    const safeNext = Boolean(next && workspace?.available);
    if (typeof window !== 'undefined') {
      window.sessionStorage.setItem(STORAGE_KEY, String(safeNext));
    }
    setEnabledState(safeNext);
  };

  return <DemoModeContext.Provider value={{ enabled, available: Boolean(workspace?.available), loading, workspace, setEnabled, refresh }}>{children}</DemoModeContext.Provider>;
};

export const useDemoMode = () => {
  const context = useContext(DemoModeContext);
  if (!context) throw new Error('useDemoMode must be used within DemoModeProvider');
  return context;
};
