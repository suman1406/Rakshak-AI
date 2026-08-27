import React, { useState } from 'react';
import { EvidenceFrame } from '../../types';
import { Play, Pause, Maximize2, ShieldAlert, CheckCircle2, Eye, ScanLine, Layers } from 'lucide-react';

interface EvidenceViewerProps {
  evidenceFrames: EvidenceFrame[];
  aiIndication: string;
  confidence: number;
  caseId?: string;
  videoUrl?: string;
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({
  evidenceFrames,
  aiIndication,
  confidence,
  caseId,
}) => {
  const [selectedFrameIndex, setSelectedFrameIndex] = useState(0);
  const [isPlayingVideo, setIsPlayingVideo] = useState(false);
  const [activeTab, setActiveTab] = useState<'frames' | 'video'>('frames');
  const [hoveredRegionId, setHoveredRegionId] = useState<string | null>(null);

  const activeFrame = evidenceFrames[selectedFrameIndex] || evidenceFrames[0];

  return (
    <div className="bg-pure-surface border border-structural rounded-2xl p-5 shadow-sm space-y-5">
      {/* Top Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-structural">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-field-canvas text-field-ink rounded-lg">
              <ScanLine size={18} />
            </span>
            <h3 className="text-base font-bold text-field-ink">Multi-Frame Visual Evidence Inspector</h3>
          </div>
          <p className="text-xs text-muted-leaf mt-0.5">
            {caseId ? `Case #${caseId} • ` : ''}16 sampling frames analyzed across soybean canopy
          </p>
        </div>

        {/* View mode tabs */}
        <div className="flex items-center gap-1 bg-field-canvas p-1 rounded-xl border border-structural">
          <button
            onClick={() => setActiveTab('frames')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center gap-1.5 ${
              activeTab === 'frames'
                ? 'bg-pure-surface text-field-ink shadow-xs border border-structural'
                : 'text-muted-leaf hover:text-field-ink'
            }`}
          >
            <Layers size={14} />
            Frame Gallery ({evidenceFrames.length})
          </button>
          <button
            onClick={() => setActiveTab('video')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center gap-1.5 ${
              activeTab === 'video'
                ? 'bg-pure-surface text-field-ink shadow-xs border border-structural'
                : 'text-muted-leaf hover:text-field-ink'
            }`}
          >
            <Play size={14} />
            Video Simulation
          </button>
        </div>
      </div>

      {activeTab === 'frames' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Main Inspection Canvas (7 Cols) */}
          <div className="lg:col-span-7 space-y-3">
            <div className="relative aspect-4/3 rounded-xl overflow-hidden bg-field-ink border border-structural group">
              {/* Simulated Leaf Image with Lesion Bounding Boxes */}
              <img
                src={activeFrame.thumbnailUrl}
                alt={`Frame ${activeFrame.frameNumber}`}
                className="w-full h-full object-cover opacity-90 transition group-hover:opacity-100"
              />

              {/* Overlay SVG Bounding Boxes for Leaf Regions */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {activeFrame.leafRegions.map((region) => {
                  const isHovered = hoveredRegionId === region.id;
                  return (
                    <g key={region.id}>
                      <rect
                        x={`${region.x}%`}
                        y={`${region.y}%`}
                        width={`${region.width}%`}
                        height={`${region.height}%`}
                        fill={region.hasLesion ? 'rgba(168, 75, 69, 0.25)' : 'rgba(216, 243, 106, 0.2)'}
                        stroke={region.hasLesion ? (isHovered ? '#FFFFFF' : '#A84B45') : '#D8F36A'}
                        strokeWidth={isHovered ? '3' : '2'}
                        strokeDasharray={region.hasLesion ? 'none' : '4 2'}
                        rx="6"
                      />
                    </g>
                  );
                })}
              </svg>

              {/* Bounding Box Labels overlay */}
              {activeFrame.leafRegions.map((region) => (
                <div
                  key={`label-${region.id}`}
                  onMouseEnter={() => setHoveredRegionId(region.id)}
                  onMouseLeave={() => setHoveredRegionId(null)}
                  style={{ left: `${region.x}%`, top: `${Math.max(2, region.y - 8)}%` }}
                  className={`absolute pointer-events-auto cursor-pointer px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-tight shadow-sm transition ${
                    region.hasLesion
                      ? 'bg-alert-red text-white'
                      : 'bg-lime-signal text-field-ink'
                  }`}
                >
                  {region.label} ({region.confidence}%)
                </div>
              ))}

              {/* Frame Indicator Pill */}
              <div className="absolute top-3 left-3 bg-field-ink/80 backdrop-blur-md text-white text-xs px-2.5 py-1 rounded-lg border border-white/20 font-mono flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-lime-signal animate-pulse"></span>
                Frame #{activeFrame.frameNumber} / {evidenceFrames.length} ({activeFrame.timestampSeconds}s)
              </div>

              {/* Confidence badge */}
              <div className="absolute bottom-3 right-3 bg-field-ink/90 backdrop-blur-md text-white text-xs px-3 py-1.5 rounded-xl border border-white/20 flex items-center gap-2">
                <span className="text-muted-leaf">Frame Signal:</span>
                <span className="font-bold text-lime-signal font-mono">{activeFrame.confidenceScore}%</span>
              </div>
            </div>

            {/* Frame metadata details */}
            <div className="bg-field-canvas p-3.5 rounded-xl border border-structural flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-4">
                <div>
                  <span className="text-muted-leaf block">Leaf Regions:</span>
                  <span className="font-bold text-field-ink">{activeFrame.leafRegionsCount} inspected</span>
                </div>
                <div>
                  <span className="text-muted-leaf block">Lesions Detected:</span>
                  <span className="font-bold text-alert-red">{activeFrame.lesionsCount} spots</span>
                </div>
              </div>
              <p className="text-muted-leaf italic max-w-xs">{activeFrame.notes}</p>
            </div>
          </div>

          {/* Right Column: Frame Selector Strip & Region Breakdown (5 Cols) */}
          <div className="lg:col-span-5 space-y-4 flex flex-col justify-between">
            {/* Region List Cards */}
            <div>
              <h4 className="text-xs font-bold text-muted-leaf uppercase tracking-wider mb-2">
                Detected Regions (Frame #{activeFrame.frameNumber})
              </h4>
              <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                {activeFrame.leafRegions.map((region) => (
                  <div
                    key={region.id}
                    onMouseEnter={() => setHoveredRegionId(region.id)}
                    onMouseLeave={() => setHoveredRegionId(null)}
                    className={`p-3 rounded-xl border text-xs transition cursor-pointer flex items-center justify-between ${
                      hoveredRegionId === region.id
                        ? 'border-field-ink bg-white shadow-xs'
                        : 'border-structural bg-pure-surface hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span
                        className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                          region.hasLesion ? 'bg-alert-red' : 'bg-lime-signal'
                        }`}
                      />
                      <div>
                        <p className="font-semibold text-field-ink">{region.label}</p>
                        <p className="text-[11px] text-muted-leaf">
                          Location: X-{region.x}% Y-{region.y}%
                        </p>
                      </div>
                    </div>
                    <span className="font-mono font-bold text-field-ink bg-field-canvas px-2 py-0.5 rounded border border-structural">
                      {region.confidence}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Frame Selector Grid (16 Frames) */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs font-bold text-muted-leaf uppercase tracking-wider">
                  Select Evidence Frame (1-16)
                </h4>
                <span className="text-[11px] text-muted-leaf">Click to focus</span>
              </div>
              <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
                {evidenceFrames.map((frame, index) => {
                  const isSelected = index === selectedFrameIndex;
                  const isHighConf = frame.confidenceScore >= 80;
                  return (
                    <button
                      key={frame.frameNumber}
                      onClick={() => setSelectedFrameIndex(index)}
                      className={`relative aspect-square rounded-lg overflow-hidden border text-left p-1 transition ${
                        isSelected
                          ? 'border-2 border-field-ink ring-2 ring-lime-signal/50 scale-105'
                          : 'border-structural hover:border-gray-400 opacity-75 hover:opacity-100'
                      }`}
                    >
                      <img src={frame.thumbnailUrl} alt="" className="w-full h-full object-cover rounded" />
                      <span className="absolute bottom-0.5 right-0.5 bg-field-ink/90 text-white font-mono text-[9px] px-1 rounded">
                        #{frame.frameNumber}
                      </span>
                      {isHighConf && (
                        <span className="absolute top-0.5 left-0.5 w-1.5 h-1.5 rounded-full bg-alert-red"></span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Video Simulation Mode */
        <div className="space-y-4">
          <div className="relative aspect-video rounded-2xl bg-field-ink border border-structural overflow-hidden flex items-center justify-center">
            <img
              src={evidenceFrames[selectedFrameIndex]?.thumbnailUrl}
              alt="Field Crop Video"
              className="w-full h-full object-cover opacity-80"
            />
            {/* Play overlay button */}
            <button
              onClick={() => setIsPlayingVideo(!isPlayingVideo)}
              className="absolute w-16 h-16 rounded-full bg-lime-signal text-field-ink flex items-center justify-center shadow-lg hover:scale-105 transition"
            >
              {isPlayingVideo ? <Pause size={28} /> : <Play size={28} className="ml-1" />}
            </button>

            <div className="absolute bottom-4 left-4 right-4 bg-field-ink/80 backdrop-blur-md p-3 rounded-xl border border-white/10 flex items-center justify-between text-white text-xs">
              <div className="flex items-center gap-3">
                <span className="font-mono text-lime-signal">00:04 / 00:14</span>
                <span>Field Scan Video: Soybean Leaf Canopy</span>
              </div>
              <span className="text-muted-leaf">30 FPS • 1080p Field Capture</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
