import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, ArrowRight } from 'lucide-react';
import { PublicPage } from '../../components/ui/public-page';
import { Button } from '../../components/ui/button';
import { apiClient } from '../../services/apiClient';

type Plan = { code: string; name: string; monthly_price_paise: number | null; annual_price_paise: number | null; farm_limit: number | null; scan_limit: number | null };
export const PricingPage: React.FC = () => {
  const [annual, setAnnual] = useState(false);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  async function load() {
    setLoading(true); setError('');
    try { setPlans(await apiClient.listPublicPlans()); }
    catch { setError('We could not load the published plans. Please try again.'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);
  return <PublicPage title="A plan for your field team." intro="Start with a scoped pilot. Choose a published plan, then agree on access and rollout with the Rakshak team.">
    <div className="pricing-toolbar"><p>Organization workspace plans</p><div className="billing-switch" role="group" aria-label="Billing period"><Button variant={annual ? 'ghost' : 'default'} aria-pressed={!annual} onClick={() => setAnnual(false)}>Monthly</Button><Button variant={annual ? 'default' : 'ghost'} aria-pressed={annual} onClick={() => setAnnual(true)}>Annual</Button></div></div>
    {loading ? <p role="status">Loading published plans…</p> : error ? <div className="message error" role="alert">{error}<Button variant="secondary" onClick={load}>Try again</Button></div> : plans.length === 0 ? <section className="workspace-panel"><h2>Let's scope your pilot.</h2><p>No plans are currently published. Tell us about your team and the fields you monitor.</p><Button asChild><Link to="/contact">Contact the team <ArrowRight size={18}/></Link></Button></section> : <div className="pricing-grid">{plans.map(plan => {
      const amount = annual ? plan.annual_price_paise : plan.monthly_price_paise;
      const saving = annual && plan.monthly_price_paise && plan.annual_price_paise != null ? Math.round((1 - plan.annual_price_paise / (12 * plan.monthly_price_paise)) * 100) : 0;
      return <section className="pricing-plan" key={plan.code}><p className="eyebrow">Organization pilot</p><h2>{plan.name}</h2><p className="plan-price">{amount == null ? 'Let’s talk' : `₹${(amount / 100).toLocaleString('en-IN')}`}<span>{amount != null ? annual ? ' / year' : ' / month' : ' Custom scope'}</span></p>{saving > 0 && <p className="helper-copy">{saving}% less than 12 monthly payments</p>}<dl><div><dt>Farm allowance</dt><dd>{plan.farm_limit ?? 'By agreement'}</dd></div><div><dt>Scan allowance</dt><dd>{plan.scan_limit ?? 'By agreement'}</dd></div></dl><ul>{['A shared evidence workspace', 'Reviewed access and activation', 'No automatic charge'].map(item => <li key={item}><Check size={18}/>{item}</li>)}</ul><Button asChild><Link to={`/apply/organization?plan=${encodeURIComponent(plan.code)}`}>Request this plan <ArrowRight size={18}/></Link></Button></section>;
    })}</div>}
    <section className="pricing-note"><h2>A conversation before a commitment.</h2><p>Submitting a plan request does not start a paid subscription. Scope, allowances and commercial terms are confirmed with your organization before activation.</p><p>Using Rakshak for your own fields? <Link to="/register">Create a farmer account.</Link></p></section>
  </PublicPage>;
};
