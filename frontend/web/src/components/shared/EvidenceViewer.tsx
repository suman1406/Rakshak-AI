import React, { useState } from 'react';
import { EvidenceFrame } from '../../types';
import { ProtectedMedia } from './ProtectedMedia';

type Props = { evidenceFrames: EvidenceFrame[]; aiIndication: string; confidence: number; caseId?: string; videoUrl?: string };
export function EvidenceViewer({ evidenceFrames, videoUrl }: Props) {
  const [index, setIndex] = useState(0);
  const [mode, setMode] = useState<'frames' | 'video'>('frames');
  const frame = evidenceFrames[index] || evidenceFrames[0];
  return <section className="workspace-panel">
    <h2>Visual evidence</h2><p className="text-sm text-muted-leaf mb-4">{evidenceFrames.length} saved frames. Inspect multiple observations before recording your review.</p>
    <div className="workspace-actions mb-4"><button className="action secondary" aria-pressed={mode === 'frames'} onClick={() => setMode('frames')}>Frames</button>{videoUrl && <button className="action secondary" aria-pressed={mode === 'video'} onClick={() => setMode('video')}>Original video</button>}</div>
    {mode === 'video' && videoUrl ? <ProtectedMedia path={videoUrl} alt="Original field video" video /> : frame ? <>
      {frame.thumbnailUrl ? <ProtectedMedia path={frame.thumbnailUrl} alt={`Field observation ${frame.frameNumber}`} /> : <p>Image content is unavailable for this frame.</p>}
      <p className="text-sm my-4">Observation {index + 1} of {evidenceFrames.length}. {frame.notes}</p>
      <div className="flex gap-2 flex-wrap">{evidenceFrames.map((item, i) => <button key={`${item.frameNumber}-${i}`} className="action secondary" aria-pressed={index === i} aria-label={`View observation ${i + 1}`} onClick={() => setIndex(i)}>{i + 1}</button>)}</div>
    </> : <p>No evidence frames were saved for this scan.</p>}
  </section>;
}
