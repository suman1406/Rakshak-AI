import { UserRole } from '../types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'rakshak_ai_access_token';

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

const parseResponse = async (response: Response) => {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(body.detail || 'Request failed', response.status);
  }
  return body;
};

const request = async (path: string, init: RequestInit = {}) => {
  const token = typeof window === 'undefined' ? null : window.localStorage.getItem(TOKEN_KEY);
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return parseResponse(await fetch(`${API_BASE_URL}${path}`, { ...init, headers }));
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
    }
    return data as { access_token: string; refresh_token?: string; role: UserRole; user_id: string };
  },
  getCurrentUser: async () => {
    const data = await request('/api/v1/auth/me');
    return data as { id: string; email?: string; phone?: string; role: UserRole; org_id?: string; display_name?: string };
  },
  logout: () => {
    if (typeof window !== 'undefined') window.localStorage.removeItem(TOKEN_KEY);
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
};
