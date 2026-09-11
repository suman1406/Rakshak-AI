import React from 'react';
import { Link } from 'react-router-dom';
import { PublicPage } from '../../components/ui/public-page';
import { Button } from '../../components/ui/button';
const steps = [
  ['Choose your field', 'Create a farmer account and give your field a recognizable name. Keep separate areas as separate records.'],
  ['Record 10–30 seconds', 'Walk slowly in even daylight. Hold the camera about 30–60 cm from the plants. Pause on several leaves, including affected and nearby plants. Avoid filming people or private documents.'],
  ['Upload with consent', 'Select the video and agree to processing. Uploads support MP4, MOV, M4V and AVI, up to 100 MB and 1080p. Keep the page open until the upload is saved.'],
  ['Review the result', 'Rakshak selects usable observations and runs the current soybean baseline model. Read the indication, confidence and visual severity together with the saved evidence. A low-quality video may require a retake.'],
  ['Add context or request review', 'Record what you saw in the field. Request an agronomist review when you need a second opinion, then return to the report to read the completed review.'],
];
export const HowItWorksPage: React.FC = () => <PublicPage title="Make your next video useful." intro="A steady, short recording gives you clearer evidence to work with. Start with these five steps."><ol className="guide-steps">{steps.map(([title,body],i) => <li key={title}><span>{String(i+1).padStart(2,'0')}</span><div><h2>{title}</h2><p>{body}</p></div></li>)}</ol><section className="message"><h2>Know the limits.</h2><p>This pilot does not verify crop identity or measure infection across an entire field. Model confidence is not a calibrated probability of disease. Inspect uncertain symptoms and seek expert judgment before deciding on treatment.</p></section><div className="workspace-actions"><Button asChild><Link to="/register">Create your farmer account</Link></Button><Link className="quiet-link" to="/contact">Get help</Link></div></PublicPage>;
