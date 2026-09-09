import React from 'react';
import { Link } from 'react-router-dom';

/** Custom R monogram: a leaf-shaped aperture connects the name to field care. */
export function BrandSymbol({ className }: { className?: string }) {
  return <svg className={className} viewBox="0 0 48 48" fill="none" aria-hidden="true" focusable="false"><rect width="48" height="48" rx="13" fill="currentColor"/><path d="M12 11H24.5C32.1 11 36 14.8 36 21C36 25.2 33.8 28.1 29.7 29.7L37 39H27.3L19.8 28.9V39H12V11Z" fill="#e1edcd"/><path d="M19.8 18.4V25.2C25.3 25.2 28.7 22.5 28.7 17.7C25.1 17.7 22.4 17.8 19.8 18.4Z" fill="currentColor"/></svg>;
}

export function Brand({ light = false }: { light?: boolean }) {
  return <Link to="/" className={`brand-lockup${light ? ' brand-light' : ''}`} aria-label="Rakshak AI home"><span className="brand-mark"><BrandSymbol/></span><span className="brand-wordmark">Rakshak<span className="brand-ai">AI</span></span></Link>;
}
