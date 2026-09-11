import React from 'react';
import { PublicNavbar } from '../layout/PublicNavbar';
import { PublicFooter } from '../layout/PublicFooter';
export function PublicPage({ title, intro, children }: { title: string; intro: string; children: React.ReactNode }) {
  return <div className="brand-page"><PublicNavbar /><main id="main-content" className="public-content"><header><h1>{title}</h1><p>{intro}</p></header>{children}</main><PublicFooter /></div>;
}
