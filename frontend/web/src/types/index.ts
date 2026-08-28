export type UserRole = 'farmer' | 'agronomist' | 'org_admin' | 'admin' | 'enterprise';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organization?: string;
  district?: string;
  avatarUrl?: string;
}

export type SeverityLevel = 'Early' | 'Moderate' | 'Severe' | 'Uncertain' | 'Healthy';

export type ReviewStatus = 'awaiting_review' | 'reviewed' | 'needs_inspection';

export interface DiagnosisProbability {
  disease: string;
  probability: number; // 0 to 100
}

export interface LeafRegion {
  id: string;
  x: number; // percentage on image
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
  hasLesion: boolean;
}

export interface EvidenceFrame {
  frameNumber: number;
  timestampSeconds: number;
  thumbnailUrl: string;
  leafRegionsCount: number;
  lesionsCount: number;
  confidenceScore: number;
  leafRegions: LeafRegion[];
  notes?: string;
}

export interface Case {
  id: string; // e.g. "FASAL-10482"
  farmId: string;
  farmName: string;
  fieldId: string;
  fieldName: string;
  fpoName: string;
  district: string;
  crop: string;
  aiIndication: string;
  confidence: number; // 0 to 100
  severity: SeverityLevel;
  submittedAt: string;
  reviewStatus: ReviewStatus;
  priority: 'high' | 'medium' | 'low';
  estimatedAffectedPlantsPercent: number;
  framesAnalyzedCount: number; // e.g. 16
  supportingFramesCount: number; // e.g. 12
  leafRegionsAnalyzedCount: number; // e.g. 43
  probabilities: DiagnosisProbability[];
  explanation: string;
  evidenceFrames: EvidenceFrame[];
  videoUrl?: string;
  agronomistVerification?: AgronomistVerification;
}

export interface AgronomistVerification {
  verifiedBy: string; // agronomist name
  verifiedAt: string;
  decision: 'confirmed' | 'changed' | 'marked_healthy' | 'marked_uncertain';
  verifiedDisease: string;
  expertNotes: string;
  recommendedNextSteps?: string[];
}

export interface Field {
  id: string;
  name: string;
  farmId: string;
  farmName: string;
  fpoName: string;
  district: string;
  crop: string;
  areaAcres: number;
  healthScore: number; // 0 - 100
  healthStatus: 'Healthy' | 'At Risk' | 'Disease Detected';
  latestScanDate: string;
  primaryDiseaseSignal?: string;
  severity?: SeverityLevel;
  openCaseId?: string;
  totalScansCount: number;
  scanHistory: ScanSummary[];
}

export interface ScanSummary {
  id: string;
  date: string;
  crop: string;
  diseaseIndication: string;
  confidence: number;
  severity: SeverityLevel;
  healthScore: number;
  verifiedByAgronomist: boolean;
}

export interface Farm {
  id: string;
  name: string;
  fpoName: string;
  district: string;
  ownerName: string;
  totalFieldsCount: number;
  healthScore: number; // 0 - 100
  riskStatus: 'Low Risk' | 'Moderate Risk' | 'High Risk';
  diseaseSignalsCount: number;
  totalScansCount: number;
  fields: Field[];
  recentCases: Case[];
}

export interface OrgDashboardMetrics {
  totalFarms: number;
  healthyPercent: number;
  atRiskPercent: number;
  diseaseDetectedPercent: number;
  highRiskFarmsCount: number;
  diseaseDistribution: { disease: string; percentage: number; color: string }[];
  timeTrends: { month: string; rustCases: number; blightCases: number; healthyScans: number }[];
}

export interface AgronomistMetrics {
  openCases: number;
  highPriorityCases: number;
  awaitingReview: number;
  reviewedThisWeek: number;
  averageReviewTimeMinutes: number;
}

export interface PricingPlan {
  id: string;
  name: string;
  price: string;
  period: string;
  monitoredFarms: string;
  scansIncluded: string;
  targetUser: string;
  features: string[];
  ctaText: string;
  isPopular?: boolean;
}

export interface GeneratedReport {
  id: string;
  title: string;
  type: 'disease_outbreak' | 'fpo_health' | 'agronomist_sla' | 'field_risk';
  generatedAt: string;
  format: 'PDF' | 'CSV';
  downloadUrl: string;
  size: string;
}
