import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { Camera, Upload, CheckCircle2, Loader2, Play, Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';

export const FarmerScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedField, setSelectedField] = useState('field-north-plot');
  const [selectedCrop, setSelectedCrop] = useState('Soybean');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processStep, setProcessStep] = useState(0);

  const steps = [
    'Uploading soybean field video stream...',
    'Extracting 16 high-clarity evidence frames...',
    'Analyzing 43 leaf regions & scanning lesions...',
    'Estimating disease confidence & severity...',
    'Generating crop-health report & evidence gallery...',
  ];

  const handleStartScan = async () => {
    setIsProcessing(true);
    for (let i = 0; i < steps.length; i++) {
      setProcessStep(i);
      await new Promise((res) => setTimeout(res, 600));
    }
    const newCase = await mockApi.createDemoScan(selectedField, videoFile?.name || 'soybean_scan_field.mp4');
    setIsProcessing(false);
    navigate(`/farmer/report/${newCase.id}`);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 font-sans">
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-2">
        <div className="flex items-center gap-2">
          <span className="p-1.5 bg-lime-signal text-field-ink rounded-lg font-bold">
            <Camera size={18} />
          </span>
          <h1 className="text-2xl font-extrabold text-field-ink">Start New Field Scan</h1>
        </div>
        <p className="text-xs text-muted-leaf">
          Upload a short 10-15 second video sweeping over upper and lower leaves of your soybean crop.
        </p>
      </div>

      <SafetyBanner />

      {/* Main Scan Form */}
      <div className="bg-pure-surface border border-structural p-6 sm:p-8 rounded-3xl shadow-xs space-y-6 text-xs">
        {isProcessing ? (
          /* Processing Timeline UI */
          <div className="py-12 text-center space-y-6">
            <div className="w-16 h-16 rounded-full bg-field-ink text-lime-signal flex items-center justify-center mx-auto animate-pulse">
              <Loader2 size={32} className="animate-spin" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-field-ink">Analyzing Field Video</h3>
              <p className="text-xs text-muted-leaf">{steps[processStep]}</p>
            </div>

            {/* Step indicators */}
            <div className="max-w-md mx-auto space-y-2 text-left pt-2">
              {steps.map((st, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-3 p-2.5 rounded-xl border text-xs transition ${
                    index < processStep
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-900 font-semibold'
                      : index === processStep
                      ? 'bg-lime-signal/20 border-lime-signal text-field-ink font-bold animate-pulse'
                      : 'bg-field-canvas border-structural text-muted-leaf opacity-60'
                  }`}
                >
                  {index < processStep ? (
                    <CheckCircle2 size={16} className="text-emerald-700 shrink-0" />
                  ) : index === processStep ? (
                    <Loader2 size={16} className="text-field-ink shrink-0 animate-spin" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-gray-400 shrink-0 text-[10px] flex items-center justify-center font-mono">
                      {index + 1}
                    </span>
                  )}
                  <span>{st}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Form Controls */
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-bold mb-1 text-field-ink">Select Field</label>
                <select
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                  className="w-full p-3 rounded-xl border border-structural bg-field-canvas font-medium text-xs outline-none"
                >
                  <option value="field-north-plot">North Plot (4.5 Acres)</option>
                  <option value="field-west-plot">West Plot (3.0 Acres)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold mb-1 text-field-ink">Select Crop</label>
                <select
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  className="w-full p-3 rounded-xl border border-structural bg-field-canvas font-medium text-xs outline-none"
                >
                  <option value="Soybean">Soybean (Glycine max)</option>
                </select>
              </div>
            </div>

            {/* Video Upload Drop Area */}
            <div>
              <label className="block font-bold mb-1 text-field-ink">Field Video Stream</label>
              <div className="border-2 border-dashed border-structural rounded-2xl p-8 text-center bg-field-canvas hover:bg-gray-200/50 transition cursor-pointer space-y-3">
                <div className="w-12 h-12 rounded-full bg-pure-surface border border-structural text-field-ink flex items-center justify-center mx-auto shadow-xs">
                  <Upload size={20} />
                </div>
                <div>
                  <p className="font-bold text-field-ink">Click or drag field video here</p>
                  <p className="text-[11px] text-muted-leaf">Supports MP4, MOV, WEBM (Max 50MB)</p>
                </div>
                <div className="pt-2">
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-pure-surface border border-structural rounded-full font-mono text-[10px] font-bold text-field-ink">
                    Sample Pre-loaded: soybean_rust_scan.mp4 (14s)
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={handleStartScan}
              className="w-full py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-sm"
            >
              <Sparkles size={16} className="text-lime-signal" />
              <span>Process Video & Generate Report</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
