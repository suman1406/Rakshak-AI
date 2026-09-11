import React from 'react';
import { PublicNavbar } from '../layout/PublicNavbar';
export function AuthShell({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return <div className="auth-page"><PublicNavbar /><main id="main-content" className="auth-layout"><aside className="auth-story"><img src="/soybean-field.png" alt="Illustrative soybean field in morning light" /><div><p>One field. One visit at a time.</p><h2>A closer look<br />starts here.</h2><span>Private records. Clear evidence. Human judgment.</span></div></aside><section className="auth-form-panel"><h1>{title}</h1><p className="auth-description">{description}</p>{children}</section></main></div>;
}
