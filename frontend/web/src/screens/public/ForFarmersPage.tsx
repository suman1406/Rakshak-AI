import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, Leaf, Users } from 'lucide-react';
import { PublicPage } from '../../components/ui/public-page';
import { Button } from '../../components/ui/button';

export function ForFarmersPage() {
  return <PublicPage title="Your field. A closer look." intro="A simple mobile workflow for soybean farmers: record what you see, keep the evidence, and ask for an expert review.">
    <section className="farmer-pilot-panel"><div><p className="eyebrow">Farmer mobile pilot · Free</p><h2>Made for the moments in your field.</h2><p>Save your fields, record a 10–30 second crop video, and follow its assessment from your phone. Uncertain results stay clearly marked.</p><Button asChild><Link to="/contact">Request Android pilot access</Link></Button><p className="helper-copy">Distribution is coordinated by the pilot team. Public app-store downloads are not available yet.</p></div><img src="/soybean-field.png" alt="Soybean plants growing in a field" /></section>
    <div className="public-card-grid">{[{ icon: Leaf, title: 'Choose your field', text: 'Keep captures and past assessments together under the right farm and field.' }, { icon: Camera, title: 'Record a clear view', text: 'Use daylight, move slowly, and keep leaves in focus. The app checks the video before assessment.' }, { icon: Users, title: 'Follow up with an expert', text: 'Read the evidence and limitations. Request a human review when you need another opinion.' }].map(item => <section className="workspace-panel" key={item.title}><item.icon aria-hidden="true"/><h2>{item.title}</h2><p>{item.text}</p></section>)}</div>
    <section className="pricing-note"><h2>Start with the farmer workspace.</h2><p>You can also create your free farmer account on the web. Processing needs an internet connection; the app does not diagnose offline.</p><Button variant="secondary" asChild><Link to="/register">Create a farmer account</Link></Button><p>AI assessments are preliminary. Expert review availability depends on the pilot team.</p></section>
  </PublicPage>;
}
