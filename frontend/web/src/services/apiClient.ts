import { UserRole } from '../types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'rakshak_ai_access_token';
const REFRESH_KEY = `${TOKEN_KEY}_refresh`;

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

const parseResponse = async (response: Response) => {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(body.message || body.detail || 'Request failed', response.status);
  }
  return body;
};

const refreshAccessToken = async () => {
  if (typeof window === 'undefined') return false;
  const refreshToken = window.localStorage.getItem(REFRESH_KEY);
  if (!refreshToken) return false;
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok || !body.access_token) return false;
  window.localStorage.setItem(TOKEN_KEY, body.access_token);
  return true;
};

const request = async (path: string, init: RequestInit = {}, canRefresh = true): Promise<any> => {
  const token = typeof window === 'undefined' ? null : window.localStorage.getItem(TOKEN_KEY);
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (response.status === 401 && canRefresh && await refreshAccessToken()) return request(path, init, false);
  return parseResponse(response);
};

export const apiClient = {
  isConfigured: () => Boolean(process.env.NEXT_PUBLIC_API_URL),
  register: async (payload: { display_name: string; email: string; password: string; consent_to_data_processing: boolean }) => {
    const data = await request('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, role: 'farmer' }),
    });
    return data as { id: string; email?: string; role: UserRole; display_name?: string; account_status: string };
  },
  login: async (emailOrPhone: string, password: string) => {
    const data = await request('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_or_phone: emailOrPhone, password }),
    });
    if (typeof window !== 'undefined' && data.access_token) {
      window.localStorage.setItem(TOKEN_KEY, data.access_token);
      if (data.refresh_token) window.localStorage.setItem(`${TOKEN_KEY}_refresh`, data.refresh_token);
    }
    return data as { access_token: string; refresh_token?: string; role: UserRole; user_id: string };
  },
  getCurrentUser: async () => {
    const data = await request('/api/v1/auth/me');
    return data as { id: string; email?: string; phone?: string; role: UserRole; org_id?: string; display_name?: string; account_status: string };
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(TOKEN_KEY);
      window.localStorage.removeItem(REFRESH_KEY);
    }
  },
  listFields: () => request('/api/v1/fields'),
  getField: (fieldId: string) => request(`/api/v1/fields/${fieldId}`),
  getFieldHealth: (fieldId: string) => request(`/api/v1/fields/${fieldId}/health`),
  getFarm: (farmId: string) => request(`/api/v1/farms/${farmId}`),
  listFarms: () => request('/api/v1/farms'),
  listVideos: (fieldId?: string) => request(`/api/v1/videos${fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : ''}`),
  getVideo: (videoId: string) => request(`/api/v1/videos/${videoId}`),
  uploadVideo: (fieldId: string, file: File, consent: boolean) => {
    const formData = new FormData();
    formData.append('field_id', fieldId);
    formData.append('consent', String(consent));
    formData.append('file', file);
    return request('/api/v1/videos', { method: 'POST', body: formData });
  },
  getVideoStatus: (videoId: string) => request(`/api/v1/videos/${videoId}/status`),
  getVideoAnalysis: (videoId: string) => request(`/api/v1/videos/${videoId}/analysis`),
  getVideoFrames: (videoId: string) => request(`/api/v1/videos/${videoId}/frames`),
  getB2BDashboard: () => request('/api/v1/b2b/dashboard'),
  getAgronomistQueue: (limit = 50) => request(`/api/v1/agronomist/queue?limit=${limit}`),
  getAgronomistCase: (diagnosisId: string) => request(`/api/v1/agronomist/cases/${diagnosisId}`),
  getAgronomistCaseHistory: (diagnosisId: string) => request(`/api/v1/agronomist/cases/${diagnosisId}/history`),
  claimAgronomistCase: (diagnosisId: string) => request(`/api/v1/agronomist/cases/${diagnosisId}/claim`, { method: 'POST' }),
  verifyAgronomistCase: (diagnosisId: string, payload: { disease_id?: string | null; is_healthy_override: boolean; severity_level: number; affected_plant_estimate_independent: number; notes?: string }) => request(`/api/v1/diagnosis/${diagnosisId}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  getDiagnosis: (diagnosisId: string) => request(`/api/v1/diagnosis/${diagnosisId}`),
  getB2BDrilldown: (params: { district?: string; farmId?: string; fieldId?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.district) query.set('district', params.district);
    if (params.farmId) query.set('farm_id', params.farmId);
    if (params.fieldId) query.set('field_id', params.fieldId);
    const suffix = query.toString();
    return request(`/api/v1/b2b/drilldown${suffix ? `?${suffix}` : ''}`);
  },
  listPublicPlans: () => request('/api/v1/onboarding/plans') as Promise<Array<{ code: string; name: string; monthly_price_paise: number | null; annual_price_paise: number | null; farm_limit: number | null; scan_limit: number | null }>>,
  submitApplication: (payload: { application_type: 'agronomist' | 'organization'; email: string; access_phrase: string; display_name: string; consent_to_data_processing: boolean; organization_name?: string; organization_type?: string; requested_plan_code?: string }) => request('/api/v1/onboarding/applications', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }) as Promise<{ reference: string; status: 'pending'; message: string }>,
  listAdminApplications: (applicationStatus = 'pending') => request(`/api/v1/admin/onboarding-applications?application_status=${encodeURIComponent(applicationStatus)}`),
  listAdminOnboardingAudit: () => request('/api/v1/admin/onboarding-audit-history'),
  decideAdminApplication: (reference: string, payload: { decision: 'approved' | 'rejected'; review_note?: string }) => request(`/api/v1/admin/onboarding-applications/${encodeURIComponent(reference)}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }),
  listAdminPlans: () => request('/api/v1/admin/plans'),
  createAdminPlan: (payload: { code: string; name: string; monthly_price_paise?: number; annual_price_paise?: number; farm_limit?: number; scan_limit?: number; is_public: boolean }) => request('/api/v1/admin/plans', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }),
  getDemoDataStatus: () => request('/api/v1/admin/demo-data') as Promise<{ available: boolean; videos: number; message: string }>,
  initializeDemoData: () => request('/api/v1/admin/demo-data/initialize', { method: 'POST' }) as Promise<{ initialized: boolean; organization: string; farms: number; fields: number; videos: number; message: string }>,
  getDemoWorkspace: () => request('/api/v1/demo-data/workspace') as Promise<DemoWorkspace>,
};

export type DemoField = { reference: string; name: string; farm_name: string; district: string; crop: string; area_hectares: number; scan_count: number };
export type DemoWorkspace = {
  available: boolean; message: string;
  organization: null | { name: string; farms: Array<{ reference: string; name: string; district: string; owner_name: string; fields: DemoField[] }>; metrics: { total_farms: number; total_fields: number; videos: number; reports: number } };
  farmer: null | { display_name: string; fields: DemoField[]; videos: [] };
  agronomist: null | { open_cases: number; message: string };
  admin: null | { pilot_plan: { code: string; name: string; monthly_price_paise: number; annual_price_paise: number; farm_limit: number; scan_limit: number }; message: string };
};
