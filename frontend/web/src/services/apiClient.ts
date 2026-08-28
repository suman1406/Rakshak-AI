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
    return data as { id: string; email?: string; phone?: string; role: UserRole; org_id?: string; display_name?: string };
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
};
