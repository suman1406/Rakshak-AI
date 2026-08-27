import {
  Case,
  Farm,
  Field,
  OrgDashboardMetrics,
  AgronomistMetrics,
  GeneratedReport,
  ReviewStatus,
  AgronomistVerification,
} from '../types';
import {
  MOCK_CASES,
  MOCK_FARMS,
  MOCK_FIELDS,
  MOCK_ORG_METRICS,
  MOCK_AGRONOMIST_METRICS,
  MOCK_REPORTS,
} from '../data/mockData';

// Local reactive state for simulated interactions
let casesState: Case[] = [...MOCK_CASES];
let farmsState: Farm[] = [...MOCK_FARMS];
let fieldsState: Field[] = [...MOCK_FIELDS];
let reportsState: GeneratedReport[] = [...MOCK_REPORTS];

const delay = (ms: number) => new Promise((res) => setTimeout(res, ms));

export const mockApi = {
  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/agronomist/cases
   * Query params: ?crop=&disease=&confidence=&severity=&status=&search=
   */
  getCases: async (filters?: {
    crop?: string;
    disease?: string;
    confidenceMin?: number;
    severity?: string;
    status?: ReviewStatus | 'all';
    search?: string;
  }): Promise<Case[]> => {
    await delay(150);
    let result = [...casesState];

    if (filters) {
      if (filters.status && filters.status !== 'all') {
        result = result.filter((c) => c.reviewStatus === filters.status);
      }
      if (filters.crop && filters.crop !== 'all') {
        result = result.filter((c) => c.crop.toLowerCase() === filters.crop?.toLowerCase());
      }
      if (filters.disease && filters.disease !== 'all') {
        result = result.filter((c) => c.aiIndication.toLowerCase().includes(filters.disease!.toLowerCase()));
      }
      if (filters.severity && filters.severity !== 'all') {
        result = result.filter((c) => c.severity.toLowerCase() === filters.severity?.toLowerCase());
      }
      if (filters.confidenceMin) {
        result = result.filter((c) => c.confidence >= filters.confidenceMin!);
      }
      if (filters.search && filters.search.trim()) {
        const query = filters.search.toLowerCase().trim();
        result = result.filter(
          (c) =>
            c.id.toLowerCase().includes(query) ||
            c.farmName.toLowerCase().includes(query) ||
            c.fieldName.toLowerCase().includes(query) ||
            c.fpoName.toLowerCase().includes(query)
        );
      }
    }

    return result;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/agronomist/cases/{case_id}
   */
  getCaseById: async (id: string): Promise<Case | null> => {
    await delay(100);
    const found = casesState.find((c) => c.id === id);
    return found || null;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * POST /api/v1/agronomist/cases/{case_id}/verify
   * Request body: { decision, verified_disease, expert_notes }
   */
  verifyCase: async (
    caseId: string,
    verification: Omit<AgronomistVerification, 'verifiedAt'>
  ): Promise<Case> => {
    await delay(250);
    const index = casesState.findIndex((c) => c.id === caseId);
    if (index === -1) throw new Error('Case not found');

    const updatedVerification: AgronomistVerification = {
      ...verification,
      verifiedAt: new Date().toISOString(),
    };

    const updatedCase: Case = {
      ...casesState[index],
      reviewStatus: 'reviewed',
      agronomistVerification: updatedVerification,
    };

    casesState[index] = updatedCase;
    return updatedCase;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/analytics/organization/dashboard
   */
  getOrgMetrics: async (): Promise<OrgDashboardMetrics> => {
    await delay(150);
    return MOCK_ORG_METRICS;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/agronomist/metrics
   */
  getAgronomistMetrics: async (): Promise<AgronomistMetrics> => {
    await delay(100);
    const awaitingCount = casesState.filter((c) => c.reviewStatus === 'awaiting_review').length;
    const reviewedCount = casesState.filter((c) => c.reviewStatus === 'reviewed').length;
    return {
      ...MOCK_AGRONOMIST_METRICS,
      awaitingReview: awaitingCount,
      openCases: awaitingCount + casesState.filter((c) => c.reviewStatus === 'needs_inspection').length,
      reviewedThisWeek: MOCK_AGRONOMIST_METRICS.reviewedThisWeek + reviewedCount,
    };
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/organization/farms
   */
  getFarms: async (district?: string): Promise<Farm[]> => {
    await delay(150);
    if (district && district !== 'all') {
      return farmsState.filter((f) => f.district.toLowerCase() === district.toLowerCase());
    }
    return farmsState;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/organization/farms/{farm_id}
   */
  getFarmById: async (id: string): Promise<Farm | null> => {
    await delay(100);
    const farm = farmsState.find((f) => f.id === id);
    return farm || null;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/organization/fields/{field_id}
   */
  getFieldById: async (id: string): Promise<Field | null> => {
    await delay(100);
    const field = fieldsState.find((f) => f.id === id);
    return field || null;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * POST /api/v1/farmer/scans
   * Multipart payload with soybean field video
   */
  createDemoScan: async (fieldId: string, videoFileName: string): Promise<Case> => {
    await delay(300);
    const newCaseId = `FASAL-${Math.floor(10000 + Math.random() * 9000)}`;
    const newScanCase: Case = {
      id: newCaseId,
      farmId: 'farm-001',
      farmName: 'Patil Farm',
      fieldId: fieldId,
      fieldName: fieldId === 'field-north-plot' ? 'North Plot' : 'West Plot',
      fpoName: 'Shinde FPO',
      district: 'Latur',
      crop: 'Soybean',
      aiIndication: 'Possible Soybean Rust',
      confidence: 87,
      severity: 'Moderate',
      submittedAt: new Date().toISOString(),
      reviewStatus: 'awaiting_review',
      priority: 'high',
      estimatedAffectedPlantsPercent: 20,
      framesAnalyzedCount: 16,
      supportingFramesCount: 12,
      leafRegionsAnalyzedCount: 43,
      probabilities: [
        { disease: 'Soybean Rust', probability: 87 },
        { disease: 'Bacterial Blight', probability: 5 },
        { disease: 'Healthy', probability: 4 },
        { disease: 'Other', probability: 4 },
      ],
      explanation: 'The visual symptoms are consistent with possible soybean rust across multiple plants. This is an AI indication, not a confirmed diagnosis.',
      evidenceFrames: MOCK_CASES[0].evidenceFrames,
    };

    casesState = [newScanCase, ...casesState];
    return newScanCase;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * GET /api/v1/reports
   */
  getReports: async (): Promise<GeneratedReport[]> => {
    await delay(100);
    return reportsState;
  },

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * POST /api/v1/reports/generate
   */
  generateReport: async (title: string, type: GeneratedReport['type']): Promise<GeneratedReport> => {
    await delay(350);
    const newRep: GeneratedReport = {
      id: `rep-${Math.floor(100 + Math.random() * 900)}`,
      title,
      type,
      generatedAt: new Date().toISOString().replace('T', ' ').slice(0, 16),
      format: 'PDF',
      downloadUrl: '#',
      size: '1.5 MB',
    };
    reportsState = [newRep, ...reportsState];
    return newRep;
  },
};
