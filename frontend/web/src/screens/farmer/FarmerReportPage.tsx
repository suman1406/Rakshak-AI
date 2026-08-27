import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Case } from '../../types';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { EvidenceViewer } from '../../components/shared/EvidenceViewer';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Send,
  UserCheck,
  ArrowLeft,
  Share2,
  Printer,
  ShieldCheck,
} from 'lucide-react';

export const FarmerReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackNote, setFeedbackNote] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCase = async () => {
      const found = await mockApi.getCaseById(id || 'FASAL-10482');
      setCaseData(found || (await mockApi.getCaseById('FASAL-10482')));
      setLoading(false);
    };
    fetchCase();
  }, [id]);

  if (loading || !caseData) {
    return <div className="p-8 text-center text-xs text-muted-leaf">Loading crop-health report...</div>;
  }

  const handleFeedbackSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackSent(true);
  };

  return (
    <div className="space-y-6 font-sans max-w-5xl mx-auto">
      {/* Top Header & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/farmer/dashboard"
            className="p-2 bg-pure-surface border border-structural rounded-xl text-field-ink hover:bg-field-canvas transition"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-field-ink">Crop-Health Report #{caseData.id}</h1>
              <ReviewStatusBadge status={caseData.reviewStatus} />
            </div>
            <p className="text-xs text-muted-leaf">
              {caseData.farmName} • {caseData.fieldName} • {caseData.crop} • Submitted {new Date(caseData.submittedAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => window.print()}
            className="px-3 py-2 bg-pure-surface border border-structural font-bold rounded-xl text-field-ink hover:bg-field-canvas transition flex items-center gap-1.5"
          >
            <Printer size={14} /> Print Report
          </button>
        </div>
      </div>

      <SafetyBanner />

      {/* Summary Highlights Card */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-6">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-field-canvas rounded-2xl border border-structural">
            <span className="text-[10px] text-muted-leaf uppercase font-mono block">AI Indication</span>
            <span className="font-extrabold text-sm text-alert-red">{caseData.aiIndication}</span>
          </div>
          <div className="p-4 bg-field-canvas rounded-2xl border border-structural">
            <span className="text-[10px] text-muted-leaf uppercase font-mono block">Confidence Score</span>
            <span className="font-extrabold text-sm text-field-ink font-mono">{caseData.confidence}%</span>
          </div>
          <div className="p-4 bg-field-canvas rounded-2xl border border-structural">
            <span className="text-[10px] text-muted-leaf uppercase font-mono block">Severity Level</span>
            <SeverityBadge severity={caseData.severity} className="mt-1" />
          </div>
          <div className="p-4 bg-field-canvas rounded-2xl border border-structural">
            <span className="text-[10px] text-muted-leaf uppercase font-mono block">Affected Plants</span>
            <span className="font-extrabold text-sm text-field-ink font-mono">
              ~{caseData.estimatedAffectedPlantsPercent}%
            </span>
          </div>
        </div>

        <div className="bg-field-canvas p-4 rounded-2xl border border-structural space-y-2 text-xs">
          <span className="font-bold text-field-ink block">AI Analysis Explanation:</span>
          <p className="text-muted-leaf leading-relaxed">{caseData.explanation}</p>
        </div>

        {/* Technical Frame Stats */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 text-xs text-muted-leaf border-t border-structural">
          <span>Frames Analyzed: <strong className="text-field-ink font-mono">{caseData.framesAnalyzedCount}</strong></span>
          <span>Supporting Frames: <strong className="text-field-ink font-mono">{caseData.supportingFramesCount}</strong></span>
          <span>Leaf Regions Inspected: <strong className="text-field-ink font-mono">{caseData.leafRegionsAnalyzedCount}</strong></span>
        </div>
      </div>

      {/* Interactive Evidence Gallery Component */}
      <EvidenceViewer
        evidenceFrames={caseData.evidenceFrames}
        aiIndication={caseData.aiIndication}
        confidence={caseData.confidence}
        caseId={caseData.id}
      />

      {/* Agronomist Verification Status Box */}
      {caseData.agronomistVerification ? (
        <div className="bg-emerald-50 border border-emerald-200 p-6 rounded-3xl space-y-3 text-xs text-emerald-950">
          <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm">
            <UserCheck size={18} />
            <span>Agronomist Verified Note</span>
          </div>
          <p>
            <strong>Verified By:</strong> {caseData.agronomistVerification.verifiedBy} (
            {new Date(caseData.agronomistVerification.verifiedAt).toLocaleDateString()})
          </p>
          <p>
            <strong>Expert Notes:</strong> {caseData.agronomistVerification.expertNotes}
          </p>
        </div>
      ) : (
        <div className="bg-amber-50 border border-amber-200 p-6 rounded-3xl space-y-4 text-xs text-amber-950">
          <div className="flex items-center gap-2 font-bold text-sm">
            <UserCheck size={18} className="text-amber-700" />
            <span>Awaiting Agronomist Review</span>
          </div>
          <p>
            This scan is currently in the regional agronomist review queue. You will be notified once a certified agronomist verifies the visual evidence.
          </p>
        </div>
      )}

      {/* Feedback Action Card */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Farmer Field Feedback</h3>
        {feedbackSent ? (
          <div className="p-4 bg-soft-healthy text-emerald-900 rounded-2xl flex items-center gap-2 font-semibold">
            <CheckCircle2 size={18} />
            <span>Feedback submitted to agronomist team!</span>
          </div>
        ) : (
          <form onSubmit={handleFeedbackSubmit} className="space-y-3">
            <p className="text-muted-leaf">
              Do these visual symptoms match what you see on your physical plants in North Plot?
            </p>
            <textarea
              rows={3}
              value={feedbackNote}
              onChange={(e) => setFeedbackNote(e.target.value)}
              placeholder="Add optional notes for the agronomist (e.g. noticed spots after rain)..."
              className="w-full p-3 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
            <button
              type="submit"
              className="px-5 py-2.5 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition flex items-center gap-2"
            >
              <Send size={14} />
              <span>Submit Feedback</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
