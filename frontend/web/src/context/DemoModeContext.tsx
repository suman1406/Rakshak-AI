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
    if (!isAuthenticated) { setWorkspace(null); setEnabledState(false); return; }
    setLoading(true);
    try { setWorkspace(await apiClient.getDemoWorkspace()); }
    catch { setWorkspace(null); setEnabledState(false); }
    finally { setLoading(false); }
  };
  useEffect(() => { void refresh(); }, [isAuthenticated]);
  useEffect(() => {
    const requested = window.sessionStorage.getItem(STORAGE_KEY) === 'true';
    setEnabledState(Boolean(requested && workspace?.available));
  }, [workspace?.available]);
  const setEnabled = (next: boolean) => {
    const safeNext = Boolean(next && workspace?.available);
    window.sessionStorage.setItem(STORAGE_KEY, String(safeNext));
    setEnabledState(safeNext);
  };
  return <DemoModeContext.Provider value={{ enabled, available: Boolean(workspace?.available), loading, workspace, setEnabled, refresh }}>{children}</DemoModeContext.Provider>;
};

export const useDemoMode = () => {
  const context = useContext(DemoModeContext);
  if (!context) throw new Error('useDemoMode must be used within DemoModeProvider');
  return context;
};
