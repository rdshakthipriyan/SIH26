import axios from 'axios';
import type { DoctorCase, ClinicalCase, FHIRBundle } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('medikiosk_doctor_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const doctorApi = {
  cases: () => api.get('/doctor/cases').then(r => r.data as { cases: DoctorCase[]; total: number }),
  summary: (sessionId: string) => api.get(`/doctor/cases/${sessionId}/summary`).then(r => r.data as ClinicalCase),
  fhir: (sessionId: string) => api.get(`/cases/${sessionId}/fhir`).then(r => r.data as FHIRBundle),
};
