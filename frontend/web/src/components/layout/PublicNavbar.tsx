import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import * as Dialog from '@radix-ui/react-dialog';
import { ArrowRight, Menu, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Brand } from '../ui/brand';
import { Button } from '../ui/button';

export const PublicNavbar: React.FC = () => {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  useEffect(() => setOpen(false), [location.pathname]);
  const home = role === 'farmer' ? '/farmer' : role === 'agronomist' ? '/agronomist/dashboard' : role === 'admin' ? '/admin/dashboard' : '/organization/dashboard';
  const links = [{ name: 'For farmers', path: '/for-farmers' }, { name: 'How it works', path: '/how-it-works' }, { name: 'Pricing', path: '/pricing' }, { name: 'Contact', path: '/contact' }];
  return <header className="public-navigation"><a className="skip-link" href="#main-content">Skip to content</a><Brand /><nav className="public-nav-links" aria-label="Main navigation">{links.map(link => <Link key={link.path} to={link.path} aria-current={location.pathname === link.path ? 'page' : undefined}>{link.name}</Link>)}</nav><div className="public-nav-actions">{isAuthenticated ? <Button asChild size="small"><Link to={home}>Your workspace <ArrowRight size={16} /></Link></Button> : <><Link to="/login">Sign in</Link><Button asChild size="small"><Link to="/apply/organization">Request access <ArrowRight size={16} /></Link></Button></>}</div><Dialog.Root open={open} onOpenChange={setOpen}><Dialog.Trigger asChild><Button variant="ghost" size="icon" className="public-menu-trigger" aria-label="Open navigation"><Menu size={23} /></Button></Dialog.Trigger><Dialog.Portal><Dialog.Overlay className="navigation-overlay" /><Dialog.Content className="navigation-drawer"><Dialog.Title className="text-xl font-semibold">Explore Rakshak</Dialog.Title><Dialog.Description className="sr-only">Choose a page or open your workspace.</Dialog.Description><Dialog.Close asChild><Button variant="ghost" size="icon" className="drawer-close" aria-label="Close navigation"><X /></Button></Dialog.Close><nav aria-label="Mobile navigation">{links.map(link => <Link key={link.path} to={link.path}>{link.name}<ArrowRight size={18} /></Link>)}</nav><Button asChild><Link to={isAuthenticated ? home : '/apply/organization'}>{isAuthenticated ? 'Your workspace' : 'Request access'}</Link></Button>{!isAuthenticated && <Link className="quiet-link" to="/login">Sign in to your account</Link>}</Dialog.Content></Dialog.Portal></Dialog.Root></header>;
};
