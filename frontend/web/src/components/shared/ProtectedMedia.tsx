import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';

export function ProtectedMedia({ path, alt, video = false }: { path: string; alt: string; video?: boolean }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  useEffect(() => {
    let disposed = false;
    let objectUrl = '';
    setUrl(''); setError('');
    apiClient.mediaBlob(path).then(blob => {
      if (disposed) return;
      objectUrl = URL.createObjectURL(blob); setUrl(objectUrl);
    }).catch(() => { if (!disposed) setError('Evidence unavailable. Please reload or try again later.'); });
    return () => { disposed = true; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [path]);
  if (error) return <p role="alert" className="p-6">{error}</p>;
  if (!url) return <p role="status" className="p-6">Loading evidence…</p>;
  return video ? <video src={url} controls preload="metadata" aria-label={alt} className="w-full max-h-[560px]" /> : <img src={url} alt={alt} className="w-full max-h-[560px] object-contain" />;
}
