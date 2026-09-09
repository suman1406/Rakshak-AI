import React from 'react';
import { Sprout } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Brand({ light = false }: { light?: boolean }) {
  return <Link to="/" className={`brand-lockup${light ? ' brand-light' : ''}`} aria-label="Rakshak AI home"><span className="brand-mark"><Sprout size={24} strokeWidth={1.7} /></span><span>rakshak<span className="brand-ai">ai</span></span></Link>;
}
