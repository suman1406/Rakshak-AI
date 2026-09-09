import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowDown, ArrowRight, ArrowUpRight, ClipboardCheck, Eye, Layers3, LockKeyhole, Smartphone, Sprout } from 'lucide-react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { Button } from '../../components/ui/button';
import { Accordion } from '../../components/ui/accordion';
import { WorkspacePreview } from '../../components/public/WorkspacePreview';
import { FieldExperience } from '../../components/public/FieldExperience';
const questions = [
    { question: 'Who is Rakshak AI for?', answer: 'Farmers use the mobile app to record soybean crops and revisit evidence. Organizations use the web workspace to organize field records. Agronomists review requested cases, and administrators manage access.' },
    { question: 'Is the result a confirmed diagnosis?', answer: 'No. The pilot selects useful observations and returns a visual indication with supporting frames. The supplied models are an unvalidated baseline. Consult an agronomist before acting on uncertain symptoms.' },
    { question: 'Can I use it without a connection?', answer: 'You can record a video with your phone and choose it later. Uploading, analysis and viewing saved records require a connection. A failed processing job can be retried from the saved scan.' },
    { question: 'Is my evidence private?', answer: 'Authorized accounts can access their own evidence. A requested review shares that case with an agronomist. Future training permission is optional and separate from processing consent.' },
];
export const LandingPage: React.FC = () => {
    const root = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches)
            return;
        const observer = new IntersectionObserver(entries => entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        }), { threshold: 0.08 });
        root.current?.querySelectorAll('[data-reveal]').forEach(el => { el.classList.add('reveal-ready'); observer.observe(el); });
        return () => observer.disconnect();
    }, []);
    return <div ref={root} className="brand-page premium-landing immersive-landing"><PublicNavbar /><main id="main-content">
    <section className="immersive-hero">
      <img className="hero-landscape" src="/field-landscape.webp" alt="Illustrative soybean landscape at first light" fetchPriority="high"/>
      <div className="hero-atmosphere"/>
      <div className="immersive-hero-inner"><div className="immersive-hero-copy">
        <Link to="/how-it-works" className="pilot-announcement"><span />Introducing the soybean pilot <ArrowUpRight size={14}/></Link>
        <h1>A closer look.<br />A clearer next step.</h1>
        <p>Turn a field observation into a shared understanding.<br className="desktop-break"/> Crop evidence, AI perspective and human expertise—together.</p>
        <div className="immersive-actions"><Button asChild><Link to="/apply/organization">Start your workspace <ArrowUpRight size={17}/></Link></Button><a href="#explore-product">Explore Rakshak <ArrowDown size={16}/></a></div>
      </div><FieldExperience /><div className="hero-groundline"><span><Sprout size={17}/> Rooted in the field. Connected by evidence.</span><span>Soybean pilot · India</span></div></div>
    </section>
    <section className="audience-ribbon"><p>One connected workflow.<br /><strong>Built around your perspective.</strong></p><Link to="/for-farmers"><Smartphone />For farmers <ArrowUpRight size={15}/></Link><Link to="/apply/organization"><Layers3 />For organizations <ArrowUpRight size={15}/></Link><Link to="/apply/agronomist"><ClipboardCheck />For agronomists <ArrowUpRight size={15}/></Link></section>
    <section id="explore-product" className="product-introduction" data-reveal><div className="editorial-heading"><span className="section-caption">Your field, in focus</span><h2>Every observation has a story.<br /><span>Keep the whole picture.</span></h2><p>A video on a phone. A question from the field. An expert’s next step. Rakshak brings them into one continuous record.</p></div><WorkspacePreview /></section>
    <section className="evidence-editorial" data-reveal><div className="evidence-art"><img src="/soybean-field.png" alt="Illustrative close view of soybean leaves" loading="lazy"/><div className="evidence-focus" aria-hidden="true"/><div className="evidence-art-caption"><Eye size={18}/><span>See the observation.<br /><strong>Then consider the interpretation.</strong></span></div><small>Illustrative crop imagery</small></div><div className="evidence-editorial-copy"><span className="section-caption">More context. Less guesswork.</span><h2>AI brings a perspective.<br />People bring judgment.</h2><p>A useful result is more than a label. Revisit the original video, inspect selected frames and understand uncertainty before you decide what to do next.</p><div className="editorial-note"><ClipboardCheck size={21}/><div><h3>A second pair of expert eyes.</h3><p>Request an agronomist’s assessment and keep their observations alongside the evidence.</p></div></div><Link className="editorial-link" to="/how-it-works">Inside the workflow <ArrowUpRight size={18}/></Link><p className="model-boundary">Pilot results are visual indications from baseline models, not confirmed diagnoses.</p></div></section>
    <section className="connected-section" data-reveal><div className="connected-heading"><span className="section-caption">From a field visit to a shared view</span><h2>Different roles.<br />The same picture.</h2><p>Purpose-built spaces for the people looking after the crop.</p></div><div className="connected-roles"><Link to="/for-farmers"><span className="role-number">01</span><div><h3>In the farmer’s hands.</h3><p>Capture a concern. Follow your field’s history. Return to expert advice from your phone.</p></div><ArrowUpRight /></Link><Link to="/apply/organization"><span className="role-number">02</span><div><h3>On your team’s radar.</h3><p>Organize farms, find the latest assessments and take field records into your next discussion.</p></div><ArrowUpRight /></Link><Link to="/apply/agronomist"><span className="role-number">03</span><div><h3>Ready for a closer review.</h3><p>Work through requested cases with original evidence, clear context and your independent judgment.</p></div><ArrowUpRight /></Link></div></section>
    <section className="privacy-statement" data-reveal><LockKeyhole size={28}/><div><h2>Your field evidence.<br />Handled with care.</h2><p>Private access. Optional training consent. Clear control over who can review your crop observations.</p></div><Link to="/privacy">Our approach to privacy <ArrowUpRight size={17}/></Link></section>
    <section className="launch-section launch-faq" data-reveal><div><span className="section-caption">A little more clarity</span><h2>Before your<br />next field visit.</h2><Link className="quiet-link" to="/contact">Talk to our team <ArrowUpRight size={18}/></Link></div><Accordion items={questions}/></section>
    <section className="immersive-final" data-reveal><div><span className="section-caption">A new perspective starts here</span><h2>Let’s look closer.<br />Together.</h2><p>Bring your field team into the soybean pilot.</p><Button variant="accent" asChild><Link to="/apply/organization">Request pilot access <ArrowUpRight size={18}/></Link></Button><Link className="final-pricing" to="/pricing">Explore plans <ArrowRight size={16}/></Link></div><div className="final-orbit" aria-hidden="true"><Sprout strokeWidth={.6}/></div></section>
  </main><PublicFooter /></div>;
};
