import axios from 'axios';
import type { PatientSession, ClinicalCase, ConversationState, ClinicalHistory, QueueToken, ClinicalDocument, DoctorCase, FHIRBundle, Language, QueueListResponse, PatientIdentity, AyushProfile } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Auth injection
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('medikiosk_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Session / Auth
export const sessionApi = {
  start: (data: Partial<PatientIdentity>) => api.post('/sessions/start', data).then(r => r.data as PatientSession),
};

// Languages
export const languageApi = {
  list: () => api.get('/languages').then(r => r.data.languages || r.data) as Promise<Language[]>,
};

// Clinical History / Conversation (connects to real endpoints)
export const conversationApi = {
  start: (sessionId: string, data: { mode: string; language_code: string; stream?: string }) =>
    api.post(`/cases/${sessionId}/conversation/start`, data).then(r => r.data),
  respond: (sessionId: string, data: { answer_text: string; input_mode: string; raw_transcript?: string; answer_value?: string; question_id?: string }) =>
    api.post(`/cases/${sessionId}/conversation/respond`, data).then(r => r.data),
  state: (sessionId: string) => api.get(`/cases/${sessionId}/conversation/state`).then(r => r.data as ConversationState),
  history: (sessionId: string) => api.get(`/cases/${sessionId}/history`).then(r => r.data),
  submit: (sessionId: string) => api.post(`/cases/${sessionId}/history/submit`).then(r => r.data),
};

// Voice / Speech (uses backend mock / real Sarvam)
export const voiceApi = {
  transcribe: (sessionId: string, file: File, language: string) => {
    const fd = new FormData(); fd.append('audio', file);
    return api.post(`/cases/${sessionId}/voice/transcribe?language_code=${language}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
  },
  speak: (sessionId: string, text: string, language: string) =>
    api.post(`/cases/${sessionId}/conversation/speak`, { text, language_code: language }).then(r => r.data),
};

// AYUSH (existing /ayush endpoints preserved)
export const ayushApi = {
  answer: (sessionId: string, data: { question_id: string; answer_text: string; input_mode: string; language: string }) =>
    api.post(`/cases/${sessionId}/ayush/answer`, data).then(r => r.data),
  profile: (sessionId: string) => api.get(`/cases/${sessionId}/ayush/profile`).then(r => r.data as { session_id: string; ayush_profile: AyushProfile; status: string; completion_percentage: number }),
};

// OCR (existing endpoints)
export const ocrApi = {
  upload: (sessionId: string, file: File, type = 'prescription') => {
    const fd = new FormData(); fd.append('file', file); fd.append('document_type', type);
    return api.post(`/cases/${sessionId}/ocr`, fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
  },
  list: (sessionId: string) => api.get(`/cases/${sessionId}/ocr`).then(r => r.data) as Promise<{ documents: ClinicalDocument[]; total: number }>,
  detail: (sessionId: string, docId: string) => api.get(`/cases/${sessionId}/ocr/${docId}`).then(r => r.data),
};

// Queue
export const queueApi = {
  list: (department?: string) => api.get('/queue', { params: department ? { department } : {} }).then(r => r.data as QueueListResponse),
  token: (token: string) => api.get(`/queue/${token}`).then(r => r.data),
};

// Doctor
export const doctorApi = {
  cases: () => api.get('/doctor/cases').then(r => r.data) as Promise<{ cases: DoctorCase[]; total: number }>,
  summary: (sessionId: string) => api.get(`/doctor/cases/${sessionId}/summary`).then(r => r.data),
};

// FHIR
export const fhirApi = {
  bundle: (sessionId: string) => api.get(`/cases/${sessionId}/fhir`).then(r => r.data),
};
