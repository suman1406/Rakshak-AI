import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Camera, Play, Sprout, ScanLine, ArrowUpRight } from 'lucide-react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { Button } from '../../components/ui/button';
import { Accordion } from '../../components/ui/accordion';

const questions = [
  { question: 'What do I need to get started?', answer: 'Create a farmer account, add your field, and record a 10–30 second soybean video. Use even daylight and show several leaves across multiple plants. You need a connection to upload; you can return to the saved result later.' },
  { question: 'Is the result a confirmed diagnosis?', answer: 'No. The current pilot uses baseline models to suggest visual indications. Crop identity, confidence and severity have not been validated under field conditions. Ask an agronomist to review uncertain or concerning symptoms.' },
  { question: 'Who can see my field videos?', answer: 'Evidence is private to authorized accounts. When you request an expert review, the reviewing agronomist can see that scan. Optional permission for future model-training exports is separate from processing consent.' },
  { question: 'Can an FPO or agronomist join?', answer: 'Yes. Apply for an organization or agronomist workspace. Applications are reviewed before access is granted. Organizations see their own field records; experts review the cases available to them.' },
];

export const LandingPage: React.FC = () => <div className="brand-page">
  <PublicNavbar />
  <main id="main-content">
    <section className="landing-hero">
      <div className="hero-copy"><div className="pilot-note"><span /> Soybean pilot · Made for the field</div><h1>A closer look.<br />A clearer next step.</h1><p>Turn a short walk through your crop into a field record you can understand, revisit, and share with an agronomist.</p><div className="hero-actions"><Button asChild variant="accent"><Link to="/register">Start with your field <ArrowRight size={19} /></Link></Button><Link className="quiet-link" to="/how-it-works"><Play size={16} /> See how it works</Link></div><div className="hero-footnote"><Sprout size={18} /><span>Your observations first. AI assistance. Human judgment.</span></div></div>
      <figure className="hero-photo"><img src="/soybean-field.png" alt="Illustrative soybean leaves in soft morning light, with planted rows beyond" fetchPriority="high" /><figcaption><span>Observe the whole plant.</span><span>Illustrative image</span></figcaption><div className="capture-guide" aria-hidden="true"><ScanLine size={30} /><span>Keep it steady.<br />Let the leaves tell the story.</span></div></figure>
    </section>
    <div className="field-strip"><span>10–30 seconds of video</span><span>Saved visual evidence</span><span>Expert review on request</span><span>Private by default</span></div>
    <section className="landing-process" id="how-it-works"><div className="process-intro"><p className="section-label">From observation to action</p><h2>A field visit,<br />with more context.</h2><p>No special equipment. Just your phone, a few plants, and a moment to look closely.</p><Button asChild variant="secondary"><Link to="/how-it-works">Recording guide <ArrowUpRight size={18} /></Link></Button></div><ol className="process-steps"><li><span className="step-number">01</span><div><h3>Walk. Pause. Record.</h3><p>Choose your field and capture several plants. A steady video in even daylight gives the system more to work with.</p></div><Camera size={24} /></li><li><span className="step-number">02</span><div><h3>Read the evidence.</h3><p>See the visual indication alongside its frames and uncertainty. If the footage is not clear enough, you will know to try again.</p></div><ScanLine size={24} /></li><li><span className="step-number">03</span><div><h3>Bring in a second opinion.</h3><p>Save your observations and request an agronomist review. Keep the assessment with the field for your next visit.</p></div><Sprout size={24} /></li></ol></section>
    <section className="evidence-story"><div className="evidence-story-image"><img src="/soybean-field.png" alt="Close view of soybean leaf surfaces" loading="lazy" /><span>Look closer before you act.</span></div><div className="evidence-story-copy"><p className="section-label">A considered approach</p><h2>A signal is a starting point.</h2><p>Field conditions are complex. A video can help you notice symptoms, but it cannot replace a trained person examining the crop.</p><p>Rakshak keeps the original evidence close to every result. Baseline model confidence and visual severity are shown as estimates, with an explicit route to human review.</p><Link className="quiet-link" to="/about">Our approach <ArrowRight size={18} /></Link></div></section>
    <section className="landing-roles"><div><p className="section-label">One field record, shared context</p><h2>Built around the people<br />who care for the crop.</h2></div><div className="role-links"><Link to="/register"><span><strong>For farmers</strong><small>Your fields, scans, and next steps.</small></span><ArrowUpRight /></Link><Link to="/apply/agronomist"><span><strong>For agronomists</strong><small>Evidence to inspect. Reviews to record.</small></span><ArrowUpRight /></Link><Link to="/apply/organization"><span><strong>For organizations</strong><small>A clear view across your own farms.</small></span><ArrowUpRight /></Link></div></section>
    <section className="landing-faq"><div><p className="section-label">Before you begin</p><h2>A few useful answers.</h2><p>More to discuss? <Link to="/contact">Talk to the team.</Link></p></div><Accordion items={questions} /></section>
    <section className="landing-final"><Sprout size={36} /><h2>Your next field visit<br />can tell you more.</h2><Button asChild variant="accent"><Link to="/register">Create your farmer account <ArrowRight size={19} /></Link></Button><Link to="/pricing">Explore pilot plans</Link></section>
  </main><PublicFooter />
</div>;

