import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/apiClient';
import { Button } from '../../components/ui/button';
type Inquiry = {id: string; name: string; email: string; message: string; status: string; created_at: string};
export function InquiriesPage() {
  const [items,setItems] = useState<Inquiry[]>([]); const [error,setError] = useState(''); const [busy,setBusy] = useState(false);
  async function load() { setBusy(true); setError(''); try { setItems(await apiClient.listInquiries()); } catch(e) { setError(e instanceof Error ? e.message : 'Could not load requests'); } finally { setBusy(false); } }
  useEffect(() => { void load(); }, []);
  async function close(id: string) { setBusy(true); try { await apiClient.closeInquiry(id); await load(); } catch(e) { setError(e instanceof Error ? e.message : 'Could not close request'); } finally { setBusy(false); } }
  return <div className="farmer-workspace"><header className="workspace-heading"><div><h1>Contact inbox</h1><p>Latest 200 website requests. Closing a request records its status and does not send a message.</p></div><Button variant="secondary" disabled={busy} onClick={() => void load()}>Refresh</Button></header>{error && <p className="message error" role="alert">{error}</p>}{busy && <p aria-live="polite">Updating inbox…</p>}{!busy && !items.length && <p>No requests yet.</p>}{items.map(item => <article className="workspace-panel" key={item.id}><div className="section-heading"><h2>{item.name}</h2><span className="status-label">{item.status}</span></div><p>{item.email} · {new Date(item.created_at).toLocaleString()}</p><p className="inquiry-message">{item.message}</p><p className="helper-copy">Reference: {item.id}</p>{item.status === 'open' && <Button variant="secondary" disabled={busy} onClick={() => void close(item.id)}>Mark closed</Button>}</article>)}</div>;
}
