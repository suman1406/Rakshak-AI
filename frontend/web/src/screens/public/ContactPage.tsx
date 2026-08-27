import React, { useState } from 'react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { Mail, Phone, MapPin, Send, CheckCircle2 } from 'lucide-react';

export const ContactPage: React.FC = () => {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full space-y-12">
        <div className="space-y-4">
          <span className="px-3 py-1 bg-lime-signal text-field-ink text-xs font-mono font-bold rounded-full">
            GET IN TOUCH
          </span>
          <h1 className="text-4xl font-extrabold text-field-ink tracking-tight">Contact Fasal Rakshak Team</h1>
          <p className="text-base text-muted-leaf leading-relaxed">
            Interested in onboarding your FPO or integrating Rakshak AI into your regional crop advisory network? Send us a message.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          <div className="md:col-span-5 space-y-6">
            <div className="bg-pure-surface p-6 rounded-2xl border border-structural space-y-4 text-xs">
              <h3 className="font-bold text-sm text-field-ink">Field Operations Hub</h3>
              <div className="flex items-start gap-3">
                <MapPin size={18} className="text-lime-signal shrink-0 mt-0.5" />
                <span>Agricultural Innovation Center, Latur & Amravati District, Maharashtra, India</span>
              </div>
              <div className="flex items-center gap-3">
                <Mail size={18} className="text-lime-signal shrink-0" />
                <span>support@fasalrakshak.org</span>
              </div>
              <div className="flex items-center gap-3">
                <Phone size={18} className="text-lime-signal shrink-0" />
                <span>+91 1800 123 4567 (Toll Free Demo Line)</span>
              </div>
            </div>
          </div>

          <div className="md:col-span-7 bg-pure-surface p-6 sm:p-8 rounded-2xl border border-structural">
            {submitted ? (
              <div className="text-center py-12 space-y-4">
                <div className="w-12 h-12 rounded-full bg-soft-healthy text-emerald-800 flex items-center justify-center mx-auto">
                  <CheckCircle2 size={24} />
                </div>
                <h3 className="text-lg font-bold text-field-ink">Message Received!</h3>
                <p className="text-xs text-muted-leaf">
                  Thank you for reaching out. A Fasal Rakshak agricultural specialist will follow up shortly.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block font-semibold mb-1">Your Name</label>
                    <input
                      required
                      type="text"
                      placeholder="e.g. Ramesh Patil"
                      className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold mb-1">Organization / FPO</label>
                    <input
                      required
                      type="text"
                      placeholder="e.g. Shinde FPO"
                      className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block font-semibold mb-1">Email Address</label>
                  <input
                    required
                    type="email"
                    placeholder="name@example.com"
                    className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1">Message / Pilot Inquiry</label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Tell us about your farm or FPO scope..."
                    className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2"
                >
                  <Send size={14} />
                  <span>Send Pilot Inquiry</span>
                </button>
              </form>
            )}
          </div>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
};
