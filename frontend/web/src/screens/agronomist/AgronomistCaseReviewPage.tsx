import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Case, AgronomistVerification } from '../../types';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { EvidenceViewer } from '../../components/shared/EvidenceViewer';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import { useAuth } from '../../context/AuthContext';
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  Send,
  RotateCcw,
  ShieldCheck,
  FileText,
  Clock,
  Sparkles,
} from 'lucide-react';

export const AgronomistCaseReviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);

  // Verification Form State
  const [decision, setDecision] = useState<
    'confirmed' | 'changed' | 'marked_healthy' | 'marked_uncertain'
  >('confirmed');
  const [verifiedDisease, setVerifiedDisease] = useState<string>('Soybean Rust');
  const [expertNote, setExpertNote] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);

  useEffect(() => {
    const fetchCase = async () => {
      const found = await mockApi.getCaseById(id || 'FASAL-10482');
      if (found) {
        setCaseData(found);
        setVerifiedDisease(found.aiIndication.replace('Possible ', ''));
      }
      setLoading(false);
    };
    fetchCase();
  }, [id]);

  if (loading || !caseData) {
    return <div className="p-8 text-center text-xs text-muted-leaf">Loading agronomist case review...</div>;
  }

  const handleVerificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    const verificationPayload: Omit<AgronomistVerification, 'verifiedAt'> = {
      verifiedBy: user?.name || 'Dr. Anita Deshmukh',
      decision,
      verifiedDisease: decision === 'marked_healthy' ? 'Healthy Crop' : verifiedDisease,
      expertNotes:
        expertNote.trim() ||
        (decision === 'confirmed'
          ? 'Confirmed Soybean Rust symptoms. Advised selective pruning & application of bio-fungicide.'
          : 'Verified case adjustment per expert visual audit.'),
    };

    const updated = await mockApi.verifyCase(caseData.id, verificationPayload);
    setCaseData(updated);
    setSubmitting(false);
    setVerifiedSuccess(true);
  };

  return (
    <div className="space-y-6 font-sans max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/agronomist/dashboard"
            className="p-2 bg-pure-surface border border-structural rounded-xl text-field-ink hover:bg-field-canvas transition"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-field-ink">Agronomist Case Verification #{caseData.id}</h1>
              <ReviewStatusBadge status={caseData.reviewStatus} />
            </div>
            <p className="text-xs text-muted-leaf">
              Farm: <strong>{caseData.farmName}</strong> • Field: <strong>{caseData.fieldName}</strong> • FPO:{' '}
              <strong>{caseData.fpoName}</strong> ({caseData.district})
            </p>
          </div>
        </div>

        <span className="text-xs font-mono bg-field-canvas border border-structural px-3 py-1.5 rounded-xl font-bold text-field-ink">
          Submitted: {new Date(caseData.submittedAt).toLocaleString()}
        </span>
      </div>

      <SafetyBanner />

      {/* Grid: AI Diagnostic Distribution & Frame Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Probability Distribution & Frame Stats (5 cols) */}
        <div className="lg:col-span-5 bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-5 text-xs">
          <div className="flex items-center justify-between border-b border-structural pb-3">
            <h3 className="font-bold text-sm text-field-ink">AI Probability Distribution</h3>
            <SeverityBadge severity={caseData.severity} />
          </div>

          <div className="space-y-3">
            {caseData.probabilities.map((prob) => (
              <div key={prob.disease} className="space-y-1">
                <div className="flex justify-between font-semibold">
                  <span>{prob.disease}</span>
                  <span className="font-mono font-bold text-field-ink">{prob.probability}%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      prob.probability >= 70
                        ? 'bg-alert-red'
                        : prob.probability >= 20
                        ? 'bg-warning-orange'
                        : 'bg-soft-healthy'
                    }`}
                    style={{ width: `${prob.probability}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="p-3.5 bg-field-canvas rounded-2xl border border-structural space-y-1">
            <span className="font-bold text-field-ink block">AI Explanation:</span>
            <p className="text-muted-leaf leading-relaxed">{caseData.explanation}</p>
          </div>

          {/* Frame Breakdown Stats */}
          <div className="grid grid-cols-3 gap-2 text-center pt-2">
            <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
              <span className="text-[10px] text-muted-leaf block">Frames</span>
              <span className="font-bold text-field-ink font-mono">{caseData.framesAnalyzedCount}</span>
            </div>
            <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
              <span className="text-[10px] text-muted-leaf block">Supporting</span>
              <span className="font-bold text-field-ink font-mono">{caseData.supportingFramesCount}</span>
            </div>
            <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
              <span className="text-[10px] text-muted-leaf block">Leaf Regions</span>
              <span className="font-bold text-field-ink font-mono">{caseData.leafRegionsAnalyzedCount}</span>
            </div>
          </div>
        </div>

        {/* Right Col: Shared Evidence Viewer Component (7 cols) */}
        <div className="lg:col-span-7">
          <EvidenceViewer
            evidenceFrames={caseData.evidenceFrames}
            aiIndication={caseData.aiIndication}
            confidence={caseData.confidence}
            caseId={caseData.id}
          />
        </div>
      </div>

      {/* Verification Controls Section */}
      <div className="bg-pure-surface border border-structural p-6 sm:p-8 rounded-3xl shadow-xs space-y-6 text-xs">
        <div className="flex items-center justify-between border-b border-structural pb-4">
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-field-ink text-lime-signal rounded-xl">
              <UserCheck size={20} />
            </span>
            <div>
              <h2 className="text-base font-bold text-field-ink">Agronomist Verification Controls</h2>
              <p className="text-muted-leaf text-[11px]">
                Submit your certified expert decision to update the field health ledger and advise the farmer.
              </p>
            </div>
          </div>
        </div>

        {verifiedSuccess && (
          <div className="p-4 bg-soft-healthy border border-emerald-300 rounded-2xl flex items-center justify-between text-emerald-950 font-bold">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={18} className="text-emerald-700" />
              <span>Verification recorded. The review queue has been updated.</span>
            </div>
            <Link to="/agronomist/dashboard" className="px-3 py-1 bg-field-ink text-white text-xs rounded-lg font-mono">
              Return to Queue
            </Link>
          </div>
        )}

        <form onSubmit={handleVerificationSubmit} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-bold mb-1.5 text-field-ink">Verification Action</label>
              <select
                value={decision}
                onChange={(e) => setDecision(e.target.value as any)}
                className="w-full p-3 rounded-xl border border-structural bg-field-canvas font-medium text-xs outline-none"
              >
                <option value="confirmed">Confirm AI Indication (Soybean Rust)</option>
                <option value="changed">Change Disease Classification</option>
                <option value="marked_healthy">Mark as Healthy Crop</option>
                <option value="marked_uncertain">Mark for In-Person Field Inspection</option>
              </select>
            </div>

            {decision === 'changed' && (
              <div>
                <label className="block font-bold mb-1.5 text-field-ink">Corrected Disease Diagnosis</label>
                <select
                  value={verifiedDisease}
                  onChange={(e) => setVerifiedDisease(e.target.value)}
                  className="w-full p-3 rounded-xl border border-structural bg-field-canvas font-medium text-xs outline-none"
                >
                  <option value="Bacterial Blight">Bacterial Blight</option>
                  <option value="Cercospora Leaf Blight">Cercospora Leaf Blight</option>
                  <option value="Downy Mildew">Downy Mildew</option>
                  <option value="Nutrient Deficiency">Nutrient Deficiency (Non-pathogenic)</option>
                </select>
              </div>
            )}
          </div>

          <div>
            <label className="block font-bold mb-1.5 text-field-ink">Expert Notes & Next Steps Advisory</label>
            <textarea
              rows={4}
              value={expertNote}
              onChange={(e) => setExpertNote(e.target.value)}
              placeholder="Enter specific advice for the farmer (e.g., recommend copper oxychloride spray, or adjust irrigation interval)..."
              className="w-full p-3 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-sm"
          >
            <Send size={16} className="text-lime-signal" />
            <span>{submitting ? 'Recording Verification...' : 'Submit Agronomist Verification'}</span>
          </button>
        </form>

        {/* Existing Audit History if already verified */}
        {caseData.agronomistVerification && (
          <div className="pt-4 border-t border-structural space-y-2">
            <span className="font-bold text-xs text-field-ink block">Audit Trail:</span>
            <div className="p-3 bg-field-canvas rounded-xl border border-structural text-xs text-muted-leaf space-y-1">
              <p>
                <strong>Verified by:</strong> {caseData.agronomistVerification.verifiedBy} on{' '}
                {new Date(caseData.agronomistVerification.verifiedAt).toLocaleString()}
              </p>
              <p>
                <strong>Decision:</strong> {caseData.agronomistVerification.decision} (
                {caseData.agronomistVerification.verifiedDisease})
              </p>
              <p>
                <strong>Notes:</strong> {caseData.agronomistVerification.expertNotes}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
