import React from 'react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { Video, Layers, Scan, CheckCircle2, UserCheck, BarChart2 } from 'lucide-react';

export const HowItWorksPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full space-y-12">
        <div className="space-y-4">
          <span className="px-3 py-1 bg-lime-signal text-field-ink text-xs font-mono font-bold rounded-full">
            COMPUTER VISION PIPELINE
          </span>
          <h1 className="text-4xl font-extrabold text-field-ink tracking-tight">
            How Rakshak AI Analyzes Soybean Field Videos
          </h1>
          <p className="text-base text-muted-leaf leading-relaxed">
            Unlike static leaf photograph models that struggle with lighting variability and motion blur, Rakshak AI processes short video sweeps to construct a robust multi-frame evidence portfolio.
          </p>
        </div>

        <SafetyBanner />

        <div className="space-y-8 pt-4">
          <div className="p-6 bg-pure-surface rounded-2xl border border-structural space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-8 h-8 rounded-lg bg-field-ink text-lime-signal font-bold flex items-center justify-center text-sm">1</span>
              <h3 className="text-lg font-bold text-field-ink">10-Second Field Video Recording</h3>
            </div>
            <p className="text-xs text-muted-leaf leading-relaxed pl-11">
              Farmers record a short sweep across upper, middle, and lower leaf canopies using the mobile app interface.
            </p>
          </div>

          <div className="p-6 bg-pure-surface rounded-2xl border border-structural space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-8 h-8 rounded-lg bg-field-ink text-lime-signal font-bold flex items-center justify-center text-sm">2</span>
              <h3 className="text-lg font-bold text-field-ink">16-Frame Extraction & Quality Filtering</h3>
            </div>
            <p className="text-xs text-muted-leaf leading-relaxed pl-11">
              The engine samples 16 distinct high-resolution frames, discarding out-of-focus or motion-blurred captures.
            </p>
          </div>

          <div className="p-6 bg-pure-surface rounded-2xl border border-structural space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-8 h-8 rounded-lg bg-field-ink text-lime-signal font-bold flex items-center justify-center text-sm">3</span>
              <h3 className="text-lg font-bold text-field-ink">Foliar Lesion Region Segmentation</h3>
            </div>
            <p className="text-xs text-muted-leaf leading-relaxed pl-11">
              Deep convolutional nets detect leaf boundaries and isolate rust pustules, bacterial spots, or chlorotic halos across 40+ leaf sub-regions.
            </p>
          </div>

          <div className="p-6 bg-pure-surface rounded-2xl border border-structural space-y-3">
            <div className="flex items-center gap-3">
              <span className="w-8 h-8 rounded-lg bg-field-ink text-lime-signal font-bold flex items-center justify-center text-sm">4</span>
              <h3 className="text-lg font-bold text-field-ink">Agronomist Review & Cluster Analytics</h3>
            </div>
            <p className="text-xs text-muted-leaf leading-relaxed pl-11">
              High-priority signals are dispatched to regional agronomists for verification, while aggregate health data updates the FPO cluster command dashboard.
            </p>
          </div>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
};
