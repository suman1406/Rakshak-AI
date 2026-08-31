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
    <header className="sticky top-0 z-50 bg-pure-surface/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-[5.25rem] flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-xl shadow-[0_10px_26px_rgba(20,35,29,.14)] group-hover:scale-105 transition">
            <Sprout size={22} className="text-lime-signal" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-field-ink">Rakshak AI</span>
            </div>
            <p className="text-[10px] font-medium text-muted-leaf">Field intelligence console</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-7">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                aria-current={isActive ? 'page' : undefined}
                className={`relative py-2 text-[13px] font-medium transition ${
                  isActive ? 'text-field-ink font-semibold after:absolute after:left-0 after:right-0 after:-bottom-1 after:h-0.5 after:bg-lime-signal after:content-[""]' : 'text-muted-leaf hover:text-field-ink'
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
          type="button"
          aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={mobileMenuOpen}
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
              aria-current={location.pathname === link.path ? 'page' : undefined}
              className={`block py-2 text-sm font-medium ${location.pathname === link.path ? 'text-field-ink font-bold' : 'text-muted-leaf hover:text-field-ink'}`}
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
