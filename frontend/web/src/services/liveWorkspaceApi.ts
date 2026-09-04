import { apiClient } from './apiClient';
import { AgronomistMetrics, Case, EvidenceFrame, Farm, Field, OrgDashboardMetrics, ReviewStatus, SeverityLevel } from '../types';

type RecordValue = Record<string, any>;

const diseaseLabel = (value?: string) => (value || 'unknown_other').split('_').map((part) => part ? `${part[0].toUpperCase()}${part.slice(1)}` : '').join(' ');
const severity = (value?: number | null): SeverityLevel => value == null ? 'Uncertain' : value <= 0 ? 'Healthy' : value === 1 ? 'Early' : value === 2 ? 'Moderate' : 'Severe';
const priority = (confidence?: number) => confidence == null || confidence < 0.65 ? 'high' : confidence < 0.8 ? 'medium' : 'low';

const toEvidenceFrames = (frames: RecordValue[] = []): EvidenceFrame[] => frames.map((frame, index) => ({
  frameNumber: frame.sequence_index ?? index + 1,
  timestampSeconds: frame.sequence_index ?? index + 1,
  // Frame content is protected by bearer authentication. The UI deliberately does not
  // substitute a fixture image while the backend has no signed or token-aware image URL.
  thumbnailUrl: '',
  leafRegionsCount: 0,
  lesionsCount: 0,
  confidenceScore: Math.round((frame.is_selected ? 1 : 0) * 100),
  leafRegions: [],
  notes: frame.is_selected ? 'Selected as evidence by the processing pipeline.' : 'Not selected as supporting evidence.',
}));

const toCase = (diagnosis: RecordValue, context: Partial<RecordValue> = {}): Case => ({
  id: diagnosis.video_diagnosis_id,
  farmId: context.farm?.id || '',
  farmName: context.farm?.name || 'Not available',
  fieldId: context.field?.id || '',
  fieldName: context.field?.name || 'Not available',
  fpoName: context.farm?.org_id ? 'Organization workspace' : 'Not available',
  district: context.farm?.district || 'Not available',
  crop: context.field?.crop_id || 'Soybean',
  aiIndication: diseaseLabel(diagnosis.disease),
  confidence: Math.round((diagnosis.confidence || 0) * 100),
  severity: severity(diagnosis.severity_level),
  submittedAt: diagnosis.created_at || '',
  reviewStatus: diagnosis.verifications_count > 0 ? 'reviewed' : diagnosis.is_unknown ? 'needs_inspection' : 'awaiting_review',
  priority: priority(diagnosis.confidence),
  estimatedAffectedPlantsPercent: Math.round((diagnosis.affected_plant_estimate || 0) * 100),
  framesAnalyzedCount: diagnosis.total_frames || 0,
  supportingFramesCount: diagnosis.supporting_frames || 0,
  leafRegionsAnalyzedCount: 0,
  probabilities: [{ disease: diseaseLabel(diagnosis.disease), probability: Math.round((diagnosis.confidence || 0) * 100) }],
  explanation: diagnosis.explanation || 'No explanation is available for this analysis.',
  evidenceFrames: toEvidenceFrames(diagnosis.frames),
});

const toField = (field: RecordValue, farm?: RecordValue, videos: RecordValue[] = []): Field => {
  const latest = videos[0];
  const status = latest?.status === 'ready' ? 'At Risk' : latest?.status === 'insufficient_evidence' ? 'At Risk' : 'Healthy';
  return {
    id: field.id,
    name: field.name,
    farmId: field.farm_id,
    farmName: farm?.name || 'Not available',
    fpoName: farm?.org_id ? 'Organization workspace' : 'Not available',
    district: farm?.district || 'Not available',
    crop: field.crop_id || 'Not set',
    areaAcres: field.area_hectares == null ? 0 : Number((field.area_hectares * 2.47105).toFixed(2)),
    healthScore: 0,
    healthStatus: status,
    latestScanDate: latest?.created_at || '',
    primaryDiseaseSignal: latest?.status === 'ready' ? 'Analysis available' : latest?.status || 'No scans yet',
    severity: latest?.status === 'ready' ? 'Moderate' : 'Uncertain',
    totalScansCount: videos.length,
    scanHistory: videos.map((video) => ({
      id: video.video_id,
      date: video.created_at,
      crop: field.crop_id || 'Not set',
      diseaseIndication: video.status === 'ready' ? 'Analysis available' : video.status,
      confidence: 0,
      severity: video.status === 'ready' ? 'Moderate' : 'Uncertain',
      healthScore: 0,
      verifiedByAgronomist: false,
    })),
  };
};

export const liveWorkspaceApi = {
  async getCaseById(id: string): Promise<Case> {
    const diagnosis = await apiClient.getAgronomistCase(id) as RecordValue;
    const video = await apiClient.getVideo(diagnosis.video_id) as RecordValue;
    const field = await apiClient.getField(video.field_id) as RecordValue;
    const farm = await apiClient.getFarm(field.farm_id) as RecordValue;
    return toCase(diagnosis, { field, farm });
  },

  async getCases(): Promise<Case[]> {
    const queue = await apiClient.getAgronomistQueue() as RecordValue[];
    return Promise.all(queue.map((item) => this.getCaseById(item.video_diagnosis_id)));
  },

  async verifyCase(caseData: Case, payload: { is_healthy_override: boolean; severity_level: number; notes?: string }): Promise<void> {
    await apiClient.claimAgronomistCase(caseData.id);
    await apiClient.verifyAgronomistCase(caseData.id, {
      ...payload,
      affected_plant_estimate_independent: caseData.estimatedAffectedPlantsPercent / 100,
    });
  },

  async getAgronomistMetrics(cases: Case[]): Promise<AgronomistMetrics> {
    const reviewedThisWeek = cases.filter((item) => item.reviewStatus === 'reviewed' && Date.now() - new Date(item.submittedAt).getTime() < 7 * 24 * 60 * 60 * 1000).length;
    return {
      openCases: cases.filter((item) => item.reviewStatus !== 'reviewed').length,
      highPriorityCases: cases.filter((item) => item.priority === 'high').length,
      awaitingReview: cases.filter((item) => item.reviewStatus === 'awaiting_review').length,
      reviewedThisWeek,
      averageReviewTimeMinutes: 0,
    };
  },

  async getFarms(district?: string): Promise<Farm[]> {
    const [farms, fields, videos] = await Promise.all([
      apiClient.listFarms() as Promise<RecordValue[]>,
      apiClient.listFields() as Promise<RecordValue[]>,
      apiClient.listVideos() as Promise<RecordValue[]>,
    ]);
    return farms
      .filter((farm) => !district || district === 'all' || farm.district === district)
      .map((farm) => {
        const farmFields = fields.filter((field) => field.farm_id === farm.id).map((field) => toField(field, farm, videos.filter((video) => video.field_id === field.id)));
        const scans = videos.filter((video) => farmFields.some((field) => field.id === video.field_id));
        return {
          id: farm.id,
          name: farm.name,
          fpoName: farm.org_id ? 'Organization workspace' : 'Not available',
          district: farm.district || 'Not available',
          ownerName: farm.owner_user_id ? 'Farm member' : 'Not available',
          totalFieldsCount: farmFields.length,
          healthScore: 0,
          riskStatus: scans.some((scan) => scan.status === 'ready') ? 'Moderate Risk' : 'Low Risk',
          diseaseSignalsCount: scans.filter((scan) => scan.status === 'ready').length,
          totalScansCount: scans.length,
          fields: farmFields,
          recentCases: [],
        };
      });
  },

  async getFarmById(id: string): Promise<Farm | null> {
    return (await this.getFarms()).find((farm) => farm.id === id) || null;
  },

  async getFieldById(id: string): Promise<Field | null> {
    const farms = await this.getFarms();
    return farms.flatMap((farm) => farm.fields).find((field) => field.id === id) || null;
  },

  async getLatestFieldCase(fieldId: string): Promise<Case | null> {
    const videos = await apiClient.listVideos(fieldId) as RecordValue[];
    const latestReadyVideo = videos.find((video) => video.status === 'ready');
    if (!latestReadyVideo) return null;
    const analysis = await apiClient.getVideoAnalysis(latestReadyVideo.video_id) as RecordValue;
    return analysis.diagnosis_id ? this.getCaseById(analysis.diagnosis_id) : null;
  },

  async getOrgMetrics(): Promise<OrgDashboardMetrics> {
    const [dashboard, farms] = await Promise.all([apiClient.getB2BDashboard() as Promise<RecordValue>, this.getFarms()]);
    const totalFields = dashboard.total_fields || 0;
    const healthyPercent = totalFields ? Math.round(((dashboard.healthy_fields_count || 0) / totalFields) * 100) : 0;
    const atRiskPercent = totalFields ? Math.round(((dashboard.at_risk_fields_count || 0) / totalFields) * 100) : 0;
    const totalSignals = (dashboard.top_diseases || []).reduce((sum: number, item: RecordValue) => sum + item.count, 0);
    return {
      totalFarms: dashboard.total_farms || 0,
      healthyPercent,
      atRiskPercent,
      diseaseDetectedPercent: atRiskPercent,
      highRiskFarmsCount: farms.filter((farm) => farm.riskStatus === 'High Risk').length,
      diseaseDistribution: (dashboard.top_diseases || []).map((item: RecordValue, index: number) => ({ disease: diseaseLabel(item.disease), percentage: totalSignals ? Math.round((item.count / totalSignals) * 100) : 0, color: ['#A84B45', '#B86B36', '#66766D'][index % 3] })),
      timeTrends: [],
    };
  },
};
