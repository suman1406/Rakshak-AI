import React from 'react';
import { SettingsLayout } from './SettingsProfilePage';
import { useAuth } from '../../context/AuthContext';
import { Building2, Shield, Bell, CheckCircle2 } from 'lucide-react';

export const SettingsOrgPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <SettingsLayout>
      <div className="space-y-6 text-xs">
        <div className="pb-4 border-b border-structural">
          <h3 className="font-bold text-sm text-field-ink">Organization Information</h3>
          <p className="text-muted-leaf">FPO registration details and cluster coverage</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block font-semibold mb-1">Organization / FPO Name</label>
            <input
              type="text"
              readOnly
              value={user?.organization || 'Shinde Farmer Producer Organization'}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-medium outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold mb-1">Registered Monitored Farms</label>
              <input
                type="text"
                readOnly
                value="4,281 Farms"
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-mono outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">Total Acreage</label>
              <input
                type="text"
                readOnly
                value="28,450 Acres"
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas font-mono outline-none"
              />
            </div>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
};

export const SettingsNotificationsPage: React.FC = () => {
  return (
    <SettingsLayout>
      <div className="space-y-6 text-xs">
        <div className="pb-4 border-b border-structural">
          <h3 className="font-bold text-sm text-field-ink">Field Notification Preferences</h3>
          <p className="text-muted-leaf">Manage disease escalation alerts</p>
        </div>

        <div className="space-y-3">
          <label className="flex items-center gap-3 p-3 bg-field-canvas rounded-xl border border-structural cursor-pointer">
            <input type="checkbox" defaultChecked className="rounded accent-field-ink" />
            <div>
              <p className="font-bold text-field-ink">High-Risk Disease Outbreak Alerts</p>
              <p className="text-[11px] text-muted-leaf">Notify immediately when soybean rust exceeds 80% confidence</p>
            </div>
          </label>

          <label className="flex items-center gap-3 p-3 bg-field-canvas rounded-xl border border-structural cursor-pointer">
            <input type="checkbox" defaultChecked className="rounded accent-field-ink" />
            <div>
              <p className="font-bold text-field-ink">Agronomist Verification Completion</p>
              <p className="text-[11px] text-muted-leaf">Receive WhatsApp / SMS when an agronomist verifies field scan</p>
            </div>
          </label>
        </div>
      </div>
    </SettingsLayout>
  );
};

export const SettingsSecurityPage: React.FC = () => {
  return (
    <SettingsLayout>
      <div className="space-y-6 text-xs">
        <div className="pb-4 border-b border-structural">
          <h3 className="font-bold text-sm text-field-ink">Data Retention & Consent Information</h3>
          <p className="text-muted-leaf">Compliance disclosures and AI safety guidelines</p>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-field-canvas rounded-2xl border border-structural space-y-2">
            <p className="font-bold text-field-ink">Data Retention Policy</p>
            <p className="text-muted-leaf leading-relaxed">
              Field video frames are retained for 180 days to generate historical disease progression curves. Agronomist decision logs are preserved permanently for quality auditing.
            </p>
          </div>

          <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl space-y-2 text-amber-950">
            <p className="font-bold">AI Indication Consent Notice</p>
            <p className="leading-relaxed">
              By using Rakshak AI, you acknowledge that all visual detections represent probabilistic indications and do not constitute an official legal or confirmed chemical diagnosis without agronomist verification.
            </p>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
};
