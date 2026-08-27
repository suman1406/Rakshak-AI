import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sprout, Menu, X, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const PublicNavbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { isAuthenticated, user, role } = useAuth();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'About', path: '/about' },
    { name: 'How It Works', path: '/how-it-works' },
    { name: 'Pricing', path: '/pricing' },
    { name: 'Contact', path: '/contact' },
  ];

  const getDashboardPath = () => {
    if (role === 'farmer') return '/login';
    if (role === 'agronomist') return '/agronomist/dashboard';
    return '/organization/dashboard';
  };

  return (
    <header className="sticky top-0 z-50 bg-pure-surface/90 backdrop-blur-md border-b border-structural">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-xl shadow-xs group-hover:scale-105 transition">
            <Sprout size={22} className="text-lime-signal" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-field-ink">Rakshak AI</span>
              <span className="text-[10px] font-mono font-semibold bg-lime-signal text-field-ink px-1.5 py-0.2 rounded">
                BETA
              </span>
            </div>
            <p className="text-[10px] font-medium text-muted-leaf">Fasal Rakshak Intelligence</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`text-sm font-medium transition ${
                  isActive ? 'text-field-ink font-semibold' : 'text-muted-leaf hover:text-field-ink'
                }`}
              >
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* Right Action CTAs */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to={getDashboardPath()}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-field-ink text-white text-xs font-semibold rounded-xl hover:bg-opacity-90 transition shadow-xs"
            >
              Go to Dashboard
              <ArrowRight size={14} className="text-lime-signal" />
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 text-xs font-semibold text-field-ink hover:text-muted-leaf transition"
              >
                Sign in
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-lime-signal text-field-ink text-xs font-bold rounded-xl hover:brightness-105 transition shadow-xs"
              >
                Get started
                <Sparkles size={14} />
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg text-field-ink hover:bg-field-canvas"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-pure-surface border-b border-structural px-4 pt-2 pb-6 space-y-3">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-medium text-field-ink hover:text-muted-leaf"
            >
              {link.name}
            </Link>
          ))}
          <div className="pt-3 border-t border-structural flex flex-col gap-2">
            {isAuthenticated ? (
              <Link
                to={getDashboardPath()}
                onClick={() => setMobileMenuOpen(false)}
                className="w-full py-2.5 text-center bg-field-ink text-white font-semibold text-xs rounded-xl"
              >
                Open Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold text-field-ink border border-structural rounded-xl"
                >
                  Sign in
                </Link>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2.5 text-center bg-lime-signal text-field-ink font-bold text-xs rounded-xl"
                >
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
