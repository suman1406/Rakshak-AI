import { useLayoutEffect } from 'react';
import { useLocation } from 'react-router-dom';

/** New pages start at their heading; explicit section links retain their target. */
export function RouteViewport() {
  const { pathname, hash } = useLocation();
  useLayoutEffect(() => {
    const previous = window.history.scrollRestoration;
    window.history.scrollRestoration = 'manual';
    return () => { window.history.scrollRestoration = previous; };
  }, []);
  useLayoutEffect(() => {
    const position = () => {
      let target: HTMLElement | null = null;
      if (hash) {
        try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
        catch { /* An invalid URL fragment has no matching section. */ }
      }
      if (target) target.scrollIntoView({ block: 'start', behavior: 'instant' });
      else window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    };
    position();
    // Run after the route commit too, including a closed mobile navigation dialog.
    const frame = requestAnimationFrame(position);
    return () => cancelAnimationFrame(frame);
  }, [pathname, hash]);
  return null;
}
