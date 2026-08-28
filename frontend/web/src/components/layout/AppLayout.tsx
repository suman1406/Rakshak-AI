import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { RoleBadge } from '../shared/RoleBadge';
import {
  Sprout,
  LayoutDashboard,
  ClipboardList,
  Building2,
  FileBarChart,
  User,
  Settings,
  LogOut,
  Bell,
  Shield,
  Menu,
  X,
} from 'lucide-react';

export const AppLayout: React.FC = () => {
  const { user, role, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const navItems = role === 'agronomist'
      ? [
          { name: 'Review Queue', path: '/agronomist/dashboard', icon: ClipboardList },
          { name: 'Agronomist Reports', path: '/agronomist/reports', icon: FileBarChart },
          { name: 'Profile & Settings', path: '/settings/profile', icon: User },
        ]
      : [
          { name: 'Organization Overview', path: '/organization/dashboard', icon: LayoutDashboard },
          { name: 'Disease Reports', path: '/organization/reports', icon: FileBarChart },
          { name: 'Organization Profile', path: '/settings/organization', icon: Building2 },
          { name: 'Account & Security', path: '/settings/security', icon: Settings },
        ];

  return (
    <div className="min-h-screen bg-field-canvas flex flex-col md:flex-row">
      {/* Mobile Top Navbar */}
      <div className="md:hidden bg-field-ink text-white p-4 flex items-center justify-between border-b border-field-ink/20 sticky top-0 z-40">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-lime-signal text-field-ink flex items-center justify-center font-bold">
            <Sprout size={18} />
          </div>
          <span className="font-extrabold text-base tracking-tight">Rakshak AI</span>
        </Link>
        <button type="button" aria-label={sidebarOpen ? 'Close workspace navigation' : 'Open workspace navigation'} aria-expanded={sidebarOpen} onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 rounded-lg hover:bg-white/10">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {sidebarOpen && <button type="button" aria-label="Close workspace navigation" onClick={() => setSidebarOpen(false)} className="fixed inset-0 z-20 bg-field-ink/40 md:hidden" />}

      {/* Sidebar Navigation */}
      <aside
        className={`fixed md:sticky top-0 z-30 h-screen w-64 bg-field-ink text-white flex flex-col justify-between p-4 transition-transform duration-200 border-r border-field-ink/20 shrink-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="space-y-6">
          {/* Logo & Platform Info */}
          <div className="hidden md:flex items-center gap-2.5 pb-4 border-b border-white/10">
            <div className="w-9 h-9 rounded-xl bg-lime-signal text-field-ink flex items-center justify-center font-bold">
              <Sprout size={20} />
            </div>
            <div>
              <span className="font-extrabold text-base tracking-tight block leading-tight">Rakshak AI</span>
              <span className="text-[10px] text-slate-300">Fasal Field Intelligence</span>
            </div>
          </div>

          {/* Current Role Context Card */}
          <div className="bg-white/5 border border-white/10 p-3 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-300 uppercase tracking-wider">Workspace</span>
            </div>
            <div className="flex items-center gap-2">
              <RoleBadge role={role || 'farmer'} />
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Workspace Menu
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition ${
                    isActive
                      ? 'bg-lime-signal text-field-ink font-bold shadow-xs'
                      : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer & User Card */}
        <div className="pt-4 border-t border-white/10 space-y-3">
          <div className="flex items-center justify-between px-2 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-lime-signal/20 text-lime-signal font-bold flex items-center justify-center text-xs">
                {user?.name ? user.name[0] : 'U'}
              </div>
              <div className="overflow-hidden">
                <p className="font-semibold text-white truncate text-xs">{user?.name || 'Workspace member'}</p>
                <p className="text-[10px] text-slate-400 truncate">{user?.organization || 'Fasal Rakshak'}</p>
              </div>
            </div>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-2 w-full px-3 py-2 text-xs font-medium text-slate-300 hover:text-red-400 hover:bg-white/5 rounded-xl transition"
          >
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="bg-pure-surface border-b border-structural px-6 py-3 flex items-center justify-between gap-4 sticky top-0 z-20 shadow-2xs">
          <div className="hidden sm:block text-xs text-muted-leaf">Evidence-led field intelligence</div>

          {/* Top Actions: fixed workspace context & notifications */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex items-center gap-2 px-3 py-1.5 bg-field-canvas border border-structural rounded-xl text-xs font-semibold text-field-ink capitalize">
              <Shield size={14} className="text-muted-leaf" /> {role?.replace('_', ' ')} workspace
            </span>

            {/* Notifications Button */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="p-2 rounded-xl bg-field-canvas hover:bg-gray-200/70 border border-structural text-field-ink relative transition"
              >
                <Bell size={18} />
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-alert-red"></span>
              </button>

              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-pure-surface border border-structural rounded-2xl shadow-xl p-4 z-50 space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-structural">
                    <span className="font-bold text-xs text-field-ink">Field Alerts</span>
                    <span className="text-[10px] bg-alert-red text-white px-1.5 py-0.5 rounded-full font-mono">
                      2 Unread
                    </span>
                  </div>
                  <div className="space-y-2 max-h-60 overflow-y-auto text-xs">
                    <div className="p-2.5 bg-amber-50 border border-amber-200 rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-amber-900 font-semibold">
                        <span>High Risk Signal</span>
                        <span className="text-[10px] text-amber-700">10m ago</span>
                      </div>
                      <p className="text-[11px] text-amber-800">
                        Soybean rust signal detected in North Plot (Patil Farm). Case #FASAL-10482 awaiting review.
                      </p>
                    </div>
                    <div className="p-2.5 bg-field-canvas border border-structural rounded-xl space-y-1">
                      <div className="flex items-center justify-between font-semibold text-field-ink">
                        <span>Agronomist Verified</span>
                        <span className="text-[10px] text-muted-leaf">2h ago</span>
                      </div>
                      <p className="text-[11px] text-muted-leaf">
                        Dr. Anita Deshmukh verified Case #FASAL-10450 as Cercospora Leaf Blight.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Dynamic Page Outlet */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
