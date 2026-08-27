import React from 'react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />
      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full space-y-8 text-xs text-muted-leaf">
        <h1 className="text-3xl font-extrabold text-field-ink">Privacy Policy</h1>
        <div className="bg-pure-surface p-8 rounded-2xl border border-structural space-y-4">
          <h2 className="text-base font-bold text-field-ink">Field Data & Video Retention Policy</h2>
          <p>
            Fasal Rakshak respects the agricultural privacy of farmers and FPOs. Uploaded soybean field videos are processed solely for crop disease feature extraction, multi-frame evidence gallery rendering, and agronomist verification.
          </p>
          <h2 className="text-base font-bold text-field-ink">Geospatial Privacy</h2>
          <p>
            Field locations and GPS bounds are restricted to authorized FPO administrators and designated agronomists. Aggregated regional trend statistics are anonymized.
          </p>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
};

export const TermsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />
      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full space-y-8 text-xs text-muted-leaf">
        <h1 className="text-3xl font-extrabold text-field-ink">Terms of Service</h1>
        <div className="bg-pure-surface p-8 rounded-2xl border border-structural space-y-4">
          <h2 className="text-base font-bold text-field-ink">AI Indication & Agricultural Disclaimer</h2>
          <p className="font-semibold text-field-ink">
            ALWAYS REMEMBER: AI indication, not confirmed diagnosis.
          </p>
          <p>
            Rakshak AI outputs probabilistic machine vision indications based on visual features in video frames. Outputs do not constitute a guaranteed chemical prescription or official legal diagnosis. Farmers must verify all AI signals with a qualified agronomist before purchasing or applying crop protection products.
          </p>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
};
