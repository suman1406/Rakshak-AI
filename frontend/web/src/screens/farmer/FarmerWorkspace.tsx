import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Sprout, Plus, Camera, ArrowRight, RefreshCw, Database } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { useAuth } from '../../context/AuthContext';
import { useDemoMode } from '../../context/DemoModeContext';
import { demoWorkspaceToFarms } from '../../services/demoWorkspaceAdapters';
import { EvidenceViewer } from '../../components/shared/EvidenceViewer';
import { EvidenceFrame } from '../../types';

type Field = { id: string; farm_id: string; name: string; farm_name?: string; district?: string; area_hectares?: number };
type Farm = { id: string; name: string; district?: string };
type Scan = { video_id: string; field_id: string; status: string; created_at: string };
const terminal = ['ready', 'failed', 'insufficient_evidence'];
const readable = (value: string) => value.replaceAll('_', ' ');
const errorMessage = (error: unknown) => error instanceof Error ? error.message : 'Please try again.';

export function FarmerWorkspace({ basePath = '/farmer' }: { basePath?: string }) {
  const { user } = useAuth();
  const { enabled: isDemoMode, workspace, setEnabled: setDemoMode } = useDemoMode();
  const [params, setParams] = useSearchParams();
  const videoId = params.get('scan');
  const [fields, setFields] = useState<Field[]>([]);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [adding, setAdding] = useState(false);
  const [farmId, setFarmId] = useState('');
  const [farmName, setFarmName] = useState('');
  const [fieldName, setFieldName] = useState('');
  const [area, setArea] = useState('');
  const [fieldId, setFieldId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [evidence, setEvidence] = useState<EvidenceFrame[]>([]);
  const [note, setNote] = useState('');
  const [reviewRequested, setReviewRequested] = useState(false);
  const [pollRevision, setPollRevision] = useState(0);

  async function load() {
    if (isDemoMode && workspace) {
      const demoFarms = demoWorkspaceToFarms(workspace);
      const extractedFields: Field[] = demoFarms.flatMap(f => f.fields.map(field => ({
        id: field.id,
        farm_id: f.id,
        farm_name: f.name,
        district: f.district,
        name: field.name,
        area_hectares: field.areaAcres ? Number((field.areaAcres / 2.47105).toFixed(2)) : undefined,
      })));
      setFarms(demoFarms.map(f => ({ id: f.id, name: f.name, district: f.district })));
      setFields(extractedFields);
      setScans([]);
      setFieldId(current => current || extractedFields[0]?.id || '');
      setFarmId(current => current || demoFarms[0]?.id || '');
      setLoading(false);
      return;
    }

    setError('');
    try {
      const [f, a, s] = await Promise.all([apiClient.listFields(), apiClient.listFarms(), apiClient.listVideos()]);
      setFields(f); setFarms(a); setScans(s);
      setFieldId(current => current || f[0]?.id || '');
      setFarmId(current => current || a[0]?.id || '');
    } catch (e) { setError(errorMessage(e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { void load(); }, [isDemoMode, workspace]);

  useEffect(() => {
    setAnalysis(null); setEvidence([]); setStatus(''); setReviewRequested(false); setNotice('');
    if (!videoId || isDemoMode) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const result = await apiClient.getVideoStatus(videoId);
        if (cancelled) return;
        setStatus(result.status);
        if (terminal.includes(result.status)) {
          const report = await apiClient.getVideoAnalysis(videoId);
          if (!cancelled) setAnalysis(report);
          const frames = await apiClient.getVideoFrames(videoId);
          if (!cancelled) setEvidence(frames.map((frame: any) => ({ frameNumber: frame.sequence_index, thumbnailUrl: frame.evidence_url, notes: frame.is_selected ? 'Included in analysis' : 'Not included in analysis' })));
        } else timer = setTimeout(poll, 4000);
      } catch (e) {
        if (!cancelled) { setError(errorMessage(e)); timer = setTimeout(poll, 10000); }
      }
    };
    void poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [videoId, pollRevision, isDemoMode]);

  async function retryScan() {
    if (!videoId || isDemoMode) return;
    setBusy(true); setError('');
    try {
      await apiClient.retryVideo(videoId);
      setPollRevision(value => value + 1);
    } catch (e) { setError(errorMessage(e)); }
    finally { setBusy(false); }
  }

  async function addField(event: React.FormEvent) {
    event.preventDefault();
    if (isDemoMode) return;
    setBusy(true); setError('');
    try {
      let target = farmId;
      if (!target) {
        const farm = await apiClient.createFarm(farmName.trim());
        target = farm.id; setFarmId(target); setFarms(current => [...current, farm]);
      }
      const field = await apiClient.createField(target, { name: fieldName.trim(), ...(area ? { area_hectares: Number(area) } : {}) });
      setFieldId(field.id); setAdding(false); setFieldName(''); setArea(''); await load();
      setNotice('Field saved. You can now record your first scan.');
    } catch (e) { setError(errorMessage(e)); } finally { setBusy(false); }
  }

  async function upload(event: React.FormEvent) {
    event.preventDefault();
    if (isDemoMode || !file || !fieldId || !consent) return;
    if (file.size > 100 * 1024 * 1024) { setError('Choose a video smaller than 100 MB.'); return; }
    setBusy(true); setError('');
    try {
      const scan = await apiClient.uploadVideo(fieldId, file, consent);
      setParams({ scan: scan.video_id }); await load();
    } catch (e) { setError(errorMessage(e)); } finally { setBusy(false); }
  }

  async function reportAction(kind: 'review' | 'feedback') {
    if (isDemoMode) return;
    setBusy(true); setError('');
    try {
      if (kind === 'review') { await apiClient.requestReview(analysis.diagnosis_id); setReviewRequested(true); setNotice('Your review request has been saved.'); }
      else { await apiClient.submitFeedback(analysis.diagnosis_id, note.trim()); setNotice('Your feedback has been saved.'); setNote(''); }
    } catch (e) { setError(errorMessage(e)); } finally { setBusy(false); }
  }

  return <div className="farmer-workspace">
    <header className="workspace-heading">
      <div>
        <p className="eyebrow">SOYBEAN FIELD CARE</p>
        <h1>{videoId ? 'Your crop assessment' : `Your fields, ${user?.name.split(' ')[0] || 'farmer'}`}</h1>
        <p>{videoId ? 'Review the observations and decide your next step.' : 'Record a short walk through your crop. Keep each assessment with its field.'}</p>
      </div>
      {videoId ? <Link className="action secondary" to={basePath}>Back to fields</Link> : isDemoMode ? null : <button className="action" onClick={() => setAdding(!adding)}><Plus size={18} />Add a field</button>}
    </header>

    {isDemoMode && (
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-900 font-semibold">
          <Database size={17} className="shrink-0 text-amber-800" />
          <span>Demo workspace is read-only. Switch to Live workspace to add your own fields or upload evidence.</span>
        </div>
        <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
          Switch to Live workspace
        </button>
      </section>
    )}

    {error && <div className="message error" role="alert">{error}<button onClick={() => { void load(); }}>Try again</button></div>}
    {notice && <div className="message" role="status">{notice}</div>}
    {loading ? <div aria-busy="true" className="workspace-loading">Loading your fields and scans…</div> : videoId ? <>
      {!analysis ? <section className="workspace-panel" aria-live="polite"><RefreshCw size={28} /><h2>{status ? readable(status) : 'Checking your scan'}</h2><p>You can leave this page and return from your scan history. Your upload is saved.</p></section> : <section className="workspace-panel report-sheet">
        <p className="eyebrow">SOYBEAN · {readable(analysis.result_state)}</p>
        <h2>{analysis.result_state === 'healthy' ? 'No clear disease symptoms detected' : analysis.result_state === 'ready' ? `Possible ${readable(analysis.diagnosis?.disease || 'disease')}` : analysis.result_state === 'failed' ? 'This scan could not be processed' : 'We need clearer evidence'}</h2>
        <p>{analysis.explanation}</p>
        {analysis.expert_review && <section className="message"><h3>Agronomist review</h3>{analysis.expert_review.status === 'completed' ? <><p><strong>{analysis.expert_review.disease}</strong></p><p>{analysis.expert_review.notes || 'No additional notes recorded.'}</p><p>{analysis.expert_review.reviewer} · {new Date(analysis.expert_review.reviewed_at).toLocaleString()}</p></> : <p>{readable(analysis.expert_review.status)}. Your request is saved.</p>}</section>}
        <p className="safety-copy">Pilot baseline: crop identity is not verified by the model. Confidence and visual severity have not been validated on field conditions.</p>
        {analysis.retake_guidance && <p className="message">{analysis.retake_guidance}</p>}
        {analysis.diagnosis && analysis.result_state !== 'unknown' && <dl className="report-facts"><div><dt>Confidence</dt><dd>{Math.round(analysis.diagnosis.confidence * 100)}% · {analysis.diagnosis.confidence_band}</dd></div><div><dt>Visual severity estimate</dt><dd>{analysis.diagnosis.severity}</dd></div><div><dt>Supporting observations</dt><dd>{analysis.evidence.supporting_frames} of {analysis.evidence.frames_analyzed} analyzed frames</dd></div></dl>}
        <h3>What to do next</h3><div className="report-actions-text">{analysis.action_items}</div>
        <p className="safety-copy">This is an AI indication, not a confirmed diagnosis. A short video does not measure disease across an entire farm.</p>
        <div className="workspace-actions"><Link className="action" to={basePath}><Camera size={18} />Scan another area</Link>{analysis.result_state === 'failed' && <button className="action secondary" disabled={busy} onClick={retryScan}><RefreshCw size={18} />{busy ? 'Requesting retry…' : 'Retry saved scan'}</button>}{analysis.diagnosis_id && <button className="action secondary" disabled={busy || reviewRequested || Boolean(analysis.expert_review)} onClick={() => reportAction('review')}>{analysis.expert_review?.status === 'completed' ? 'Review completed' : reviewRequested || analysis.expert_review ? 'Review requested' : 'Request agronomist review'}</button>}</div>
        {analysis.diagnosis_id && <form onSubmit={e => { e.preventDefault(); void reportAction('feedback'); }} className="workspace-form"><label>Your observations<textarea required maxLength={2000} value={note} onChange={e => setNote(e.target.value)} placeholder="Tell us whether this matches what you see in the field." /></label><button className="action secondary" disabled={busy || !note.trim()}>Save feedback</button></form>}
      </section>}
      {analysis && <EvidenceViewer evidenceFrames={evidence} aiIndication={analysis.diagnosis?.disease || ''} confidence={analysis.diagnosis?.confidence || 0} videoUrl={`/api/v1/videos/${videoId}/content`} />}
    </> : <>
      {(!isDemoMode && (adding || !fields.length)) && <section className="workspace-panel"><h2>{fields.length ? 'Add a field' : 'Start with your first field'}</h2><p>Give it a name you will recognize when you return.</p><form className="workspace-form" onSubmit={addField}>{farms.length > 0 && <label>Farm<select value={farmId} onChange={e => setFarmId(e.target.value)}>{farms.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}<option value="">Create a new farm</option></select></label>}{!farmId && <label>Farm name<input required maxLength={255} value={farmName} onChange={e => setFarmName(e.target.value)} /></label>}<label>Field name<input required maxLength={255} value={fieldName} onChange={e => setFieldName(e.target.value)} placeholder="For example, East soybean field" /></label><label>Area in hectares (optional)<input type="number" min="0.01" step="0.01" value={area} onChange={e => setArea(e.target.value)} /></label><p>Crop: Soybean</p><button className="action" disabled={busy || !fieldName.trim() || (!farmId && !farmName.trim())}>{busy ? 'Saving…' : 'Save field'}</button></form></section>}
      {fields.length > 0 && <div className="farmer-columns">
        <section className="workspace-panel">
          <div className="section-heading"><h2>Record a new scan</h2><Camera size={24} /></div>
          <p>Walk slowly. Keep the camera 30–60 cm from the leaves, in even daylight.</p>
          {isDemoMode ? (
            <div className="mt-4 p-4 rounded-xl border border-structural bg-field-canvas space-y-2 text-xs">
              <p className="font-semibold text-field-ink">Scan upload disabled in Demo Mode</p>
              <p className="text-muted-leaf">Switch to Live workspace to upload video evidence and process real AI crop assessments.</p>
              <button className="action secondary text-xs py-2 px-3 mt-1" onClick={() => setDemoMode(false)}>
                Switch to Live workspace
              </button>
            </div>
          ) : (
            <form onSubmit={upload} className="workspace-form">
              <label>Field<select required value={fieldId} onChange={e => setFieldId(e.target.value)}>{fields.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}</select></label>
              <label>10–30 second video<input type="file" accept="video/mp4,video/quicktime,video/x-m4v,video/x-msvideo" capture="environment" required onChange={e => setFile(e.target.files?.[0] || null)} /></label>
              <p className="helper-copy">MP4, MOV, M4V or AVI, up to 100 MB and 1080p. Include several plants and avoid rapid camera movement.</p>
              <label className="consent-control"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} required />I agree to processing this field video for an AI assessment.</label>
              <button className="action" disabled={busy || !file || !consent}>{busy ? 'Uploading your video…' : 'Upload and assess'}<ArrowRight size={18} /></button>
            </form>
          )}
        </section>
        <section className="workspace-panel">
          <h2>{isDemoMode ? 'Demo Fields (Rakshak Cooperative)' : 'Your fields'}</h2>
          <ul className="field-list">
            {fields.map(f => (
              <li key={f.id}>
                <Sprout size={22} />
                <div>
                  <strong>{f.name}</strong>
                  <p>Soybean{f.area_hectares ? ` · ${f.area_hectares} ha` : ''}{f.farm_name ? ` · ${f.farm_name}` : ''}{f.district ? ` (${f.district})` : ''}</p>
                </div>
                {!isDemoMode && <button className="text-action" onClick={() => setFieldId(f.id)} aria-label={`Select ${f.name} for scanning`}>{fieldId === f.id ? 'Selected' : 'Select'}</button>}
              </li>
            ))}
          </ul>
        </section>
      </div>}
      <section className="workspace-panel">
        <div className="section-heading"><h2>Recent scans</h2>{!isDemoMode && <button className="text-action" onClick={() => { void load(); }}>Refresh</button>}</div>
        {isDemoMode ? (
          <p className="text-sm text-muted-leaf py-2">No demo scans are included in this prototype.</p>
        ) : !scans.length ? (
          <p>Your first assessment will appear here after you upload a video.</p>
        ) : (
          <ul className="scan-list">{scans.map(s => <li key={s.video_id}><div><strong>{fields.find(f => f.id === s.field_id)?.name || 'Field scan'}</strong><p>{new Date(s.created_at).toLocaleString()}</p></div><span className="status-label">{readable(s.status)}</span><Link className="text-action" to={`${basePath}?scan=${s.video_id}`}>Open<ArrowRight size={16} /></Link></li>)}</ul>
        )}
      </section>
    </>}
  </div>;
}



