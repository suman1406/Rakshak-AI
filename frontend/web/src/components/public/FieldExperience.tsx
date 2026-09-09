import React, { useState } from 'react';
import { ArrowRight, Camera, Check, ClipboardCheck, Focus, Leaf, ScanLine } from 'lucide-react';
const stages = [
    { title: 'Capture', icon: Camera, label: 'Start with what you see.', description: 'Record a short video of the crop. Keep the original observation with your field.', detail: 'Original video · Your field record' },
    { title: 'Understand', icon: ScanLine, label: 'Look beyond the label.', description: 'Explore selected frames and a visual indication, including when the model is uncertain.', detail: 'Selected frames · Visual indication' },
    { title: 'Review', icon: ClipboardCheck, label: 'Bring expertise closer.', description: 'Request an agronomist’s assessment. Their observations stay with your saved report.', detail: 'Expert perspective · Saved next steps' },
];
export function FieldExperience() {
    const [stage, setStage] = useState(0);
    const selected = stages[stage];
    const Icon = selected.icon;
    return <div className="field-experience">
    <div className="field-viewfinder" aria-hidden="true"><span /><span /><span /><span /><Focus size={30}/></div>
    <div className="field-experience-card">
      <div className="experience-caption"><Leaf size={14}/><span>A field-to-review journey</span><small>Illustration</small></div>
      <div key={stage} className="experience-content" aria-live="polite"><span className="experience-icon"><Icon size={22}/></span><h2>{selected.label}</h2><p>{selected.description}</p><div className="experience-detail"><Check size={13}/>{selected.detail}</div></div>
      <div className="experience-controls" role="group" aria-label="Explore the field workflow">{stages.map((item, index) => <button key={item.title} onClick={() => setStage(index)} aria-pressed={stage === index}><span>0{index + 1}</span>{item.title}{stage === index && <ArrowRight size={13}/>}</button>)}</div>
    </div>
  </div>;
}
