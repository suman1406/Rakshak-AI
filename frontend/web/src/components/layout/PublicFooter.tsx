import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, ShieldCheck, Mail, Globe, MapPin } from 'lucide-react';

export const PublicFooter: React.FC = () => {
  return (
    <footer className="bg-field-ink text-white border-t border-field-ink/20 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-12 border-b border-white/10">
          {/* Brand Col (4 cols) */}
          <div className="md:col-span-4 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-lime-signal text-field-ink flex items-center justify-center font-bold">
                <Sprout size={20} />
              </div>
              <span className="text-xl font-extrabold tracking-tight">Rakshak AI</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed max-w-sm">
              Rakshak AI by Fasal Rakshak empowers farmers, agronomists, and agricultural organizations with evidence-backed field crop intelligence.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[11px] text-lime-signal font-medium">
              <ShieldCheck size={14} />
              <span>AI indication, not confirmed diagnosis.</span>
            </div>
          </div>

          {/* Nav Links (2 cols) */}
          <div className="md:col-span-2 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-lime-signal">Product</h4>
            <ul className="space-y-2 text-xs text-slate-300">
              <li><Link to="/how-it-works" className="hover:text-white transition">How It Works</Link></li>
              <li><Link to="/pricing" className="hover:text-white transition">Pricing Plans</Link></li>
              <li><Link to="/login" className="hover:text-white transition">Farmer Scan Demo</Link></li>
              <li><Link to="/login" className="hover:text-white transition">Agronomist Queue</Link></li>
              <li><Link to="/login" className="hover:text-white transition">FPO Command Center</Link></li>
            </ul>
          </div>

          {/* Company Links (2 cols) */}
          <div className="md:col-span-2 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-lime-signal">Company</h4>
            <ul className="space-y-2 text-xs text-slate-300">
              <li><Link to="/about" className="hover:text-white transition">About Fasal Rakshak</Link></li>
              <li><Link to="/contact" className="hover:text-white transition">Contact & Demo</Link></li>
              <li><Link to="/privacy" className="hover:text-white transition">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-white transition">Terms of Service</Link></li>
            </ul>
          </div>

          {/* Contact info (4 cols) */}
          <div className="md:col-span-4 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-lime-signal">Field Operations</h4>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <MapPin size={14} className="text-lime-signal shrink-0" />
                <span>Agricultural Technology Hub, Latur & Amravati, MH, India</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail size={14} className="text-lime-signal shrink-0" />
                <span>support@fasalrakshak.org</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe size={14} className="text-lime-signal shrink-0" />
                <span>fasalrakshak.org</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom copyright & disclaimer */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
          <p>© {new Date().getFullYear()} Fasal Rakshak. All rights reserved.</p>
          <p className="text-[11px] text-slate-400">
            Pilot Demonstration Platform • Standardized deterministic data mode
          </p>
        </div>
      </div>
    </footer>
  );
};
