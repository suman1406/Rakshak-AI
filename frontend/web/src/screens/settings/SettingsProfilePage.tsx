import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { RoleBadge } from '../../components/shared/RoleBadge';
import { Link, useLocation } from 'react-router-dom';
import { User, Building2, Bell, Shield, LogOut, Sparkles, CheckCircle2 } from 'lucide-react';

export const SettingsLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const { user, role, logout } = useAuth();

  const tabs = [
    { name: 'User Profile', path: '/settings/profile', icon: User },
    { name: 'Organization', path: '/settings/organization', icon: Building2 },
    { name: 'Notifications', path: '/settings/notifications', icon: Bell },
    { name: 'Security & Consent', path: '/settings/security', icon: Shield },
  ];

  return (
    <div className="space-y-6 font-sans max-w-4xl mx-auto">
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-2">
        <h1 className="text-2xl font-extrabold text-field-ink">Settings & Preferences</h1>
        <p className="text-xs text-muted-leaf">Manage user profiles, team permissions, and privacy consent</p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-structural pb-1 overflow-x-auto text-xs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = location.pathname === tab.path;
          return (
            <Link
              key={tab.path}
              to={tab.path}
              className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 whitespace-nowrap ${
                isActive
                  ? 'bg-field-ink text-white shadow-xs'
                  : 'text-muted-leaf bg-pure-surface hover:text-field-ink border border-structural'
              }`}
            >
              <Icon size={14} />
              <span>{tab.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="bg-pure-surface border border-structural p-6 sm:p-8 rounded-3xl shadow-xs">
        {children}
      </div>
    </div>
  );
};

export const SettingsProfilePage: React.FC = () => {
  const { user, role, logout } = useAuth();

  return (
    <SettingsLayout>
      <div className="space-y-6 text-xs">
        <div className="flex items-center justify-between pb-4 border-b border-structural">
          <div>
            <h3 className="font-bold text-sm text-field-ink">User Profile</h3>
            <p className="text-muted-leaf">Personal details for active persona</p>
          </div>
          <RoleBadge role={role || 'farmer'} />
        </div>

        <div className="space-y-4">
          <div>
            <label className="block font-semibold mb-1">Full Name</label>
            <input
              type="text"
              readOnly
              value={user?.name || ''}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-medium outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1">Email Address</label>
            <input
              type="text"
              readOnly
              value={user?.email || ''}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-medium outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1">Assigned District Coverage</label>
            <input
              type="text"
              readOnly
              value={user?.district || 'Latur & Amravati'}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-medium outline-none"
            />
          </div>

          <div className="p-4 bg-soft-healthy rounded-2xl border border-emerald-200 flex items-center justify-between text-emerald-950 font-semibold">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={16} />
              <span>Demo Persona Active • LocalStorage Synchronized</span>
            </div>
          </div>

          <button
            onClick={logout}
            className="px-5 py-2.5 bg-red-50 text-alert-red border border-red-200 font-bold rounded-xl hover:bg-red-100 transition flex items-center gap-2"
          >
            <LogOut size={14} />
            <span>Sign Out of Demo Session</span>
          </button>
        </div>
      </div>
    </SettingsLayout>
  );
};
