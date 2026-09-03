import { PricingPlan } from '../types';

// Public product copy, not runtime dashboard data. Keep commercial changes here
// until the backend provides a pricing/catalogue contract.
export const PRICING_PLANS: PricingPlan[] = [
  { id: 'plan-farmer', name: 'Farmer', price: '₹499', period: '/month', monitoredFarms: '1 Farm (Up to 10 acres)', scansIncluded: '10 field scans / month', targetUser: 'Individual soybean growers seeking instant AI signals', features: ['10 field scans per month', 'Instant AI crop-health reports', 'Evidence breakdown', 'Basic scan history & trends', 'WhatsApp summary share'], ctaText: 'Get started' },
  { id: 'plan-fpo', name: 'FPO', price: '₹4,999', period: '/month', monitoredFarms: '250 Monitored Farms', scansIncluded: '1,500 scans / month', targetUser: 'Farmer Producer Organizations & Agri Collectives', isPopular: true, features: ['250 monitored farms & fields', 'Organization command dashboard', 'Dedicated Agronomist review queue', 'District & cluster health analytics', 'Exportable PDF & CSV reports', 'High-risk field escalation alerts'], ctaText: 'Choose plan' },
  { id: 'plan-enterprise', name: 'Enterprise', price: 'Custom', period: '', monitoredFarms: 'Unlimited Monitored Farms', scansIncluded: 'Unlimited field scans', targetUser: 'Agri-input companies, crop insurance, & State Departments', features: ['Unlimited monitored farms & fields', 'Multi-organization workspace access', 'Priority agronomist workflows (SLA < 10 mins)', 'Direct REST & Webhook API access', 'Custom spatial intelligence reporting', 'Dedicated agronomist onboarding specialist'], ctaText: 'Talk to sales' },
];
