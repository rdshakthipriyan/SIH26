export type StreamMode = 'allopathy' | 'ayush';
export type AyushStream = 'ayurveda' | 'siddha' | 'unani' | 'homoeopathy' | 'yoga_naturopathy';
export type InputMode = 'voice' | 'touch' | 'voice_edited' | 'ocr';
export type FactStatus = 'positive' | 'negative' | 'unknown' | 'not_provided';
export type QueueStatus = 'waiting' | 'in_progress' | 'history_pending' | 'history_ready' | 'triage_required' | 'completed';
export type Priority = 'normal' | 'high';
export type CaseStatus = 'in_progress' | 'submitted' | 'review' | 'completed';
export type OCRStatus = 'processing' | 'completed' | 'failed';

// ─── Intake Sections ───────────────────────────────────────────────────────
export type IntakeSection = 'Chief Complaint' | 'HPI' | 'Past Medical History' | 'Surgical History' | 'CRks';

export interface Question {
  id: string;
  section: IntakeSection;
  text: {
    en: string;
    hi: string;
  };
  field_type: 'select' | 'multiselect' | 'text';
  options?: { value: string; label: string; label_hi: string }[];
}

// ─── Language ────────────────────────────────────────────────────────────────
export interface Language {
  code: string;
  name: string;
  native_name: string;
  script: string;
  is_indic: boolean;
  capabilities: {
    asr: boolean;
    tts: boolean;
    ui: boolean;
    questionnaire: boolean;
    conversation: boolean;
  };
}

// ─── Auth / Session ─────────────────────────────────────────────────────────
export interface PatientSession {
  session_id: string;
  temp_id?: string;
  token: string;
  token_type: string;
}

export interface PhysicianSession {
  access_token: string;
  token_type: string;
  user_id: string;
  role: string;
}

// ─── Patient identity ───────────────────────────────────────────────────────
export interface PatientIdentity {
  patient_name: string;
  patient_age?: number;
  patient_gender?: string;
  patient_phone?: string;
  abha_id?: string;
  abha_address?: string;
  is_guest: boolean;
  consent_given: boolean;
  consent_scope?: string;
  token_number?: string;
  department?: string;
  mode: StreamMode;
  language_code: string;
}

// ─── Clinical History ────────────────────────────────────────────────────────
export interface Provenance {
  input_mode: InputMode;
  language: string;
  timestamp: string;
  raw_transcript?: string;
  question_id?: string;
}

export interface ClinicalFact {
  fact_id: string;
  category: string;
  label: string;
  value: string;
  status: FactStatus;
  confidence: number;
  provenance: Provenance;
}

export interface ClinicalCase {
  case_id: string;
  session_id: string;
  patient_id?: string;
  language_code: string;
  mode: StreamMode;
  department: string;
  status: CaseStatus;
  priority: Priority;
  has_red_flags: boolean;
  red_flags?: Array<{
    flag_id: string;
    severity: 'critical' | 'warning';
    description: string;
    detected_at: string;
  }>;
  clinical_history: ClinicalFact[];
  ayush_profile?: {
    stream: AyushStream;
    dominant_dosha?: string;
    scores: Record<string, number>;
    answers: Record<string, string>;
  };
  abdm_synced: boolean;
  clinical_summary?: string;
}

export interface DoctorCase {
  case_id: string;
  session_id: string;
  patient_name: string;
  department: string;
  mode: StreamMode;
  status: CaseStatus;
  priority: Priority;
  has_red_flags: boolean;
  wait_time_mins: number;
  queue_position: number;
}

export interface FHIRBundle {
  resourceType: string;
  entry: Array<{
    resource: any;
  }>;
}

export interface OCREntity {
  entity_id: string;
  label: string;
  value: string;
  type?: string;
  confidence: number;
  requires_verification: boolean;
  warning?: string;
  source_box?: [number, number, number, number];
}

export interface ClinicalDocument {
  doc_id?: string;
  document_id?: string;
  filename?: string;
  original_filename?: string;
  upload_date?: string;
  status?: OCRStatus;
  processing_status?: OCRStatus;
  warnings?: string[];
  requires_verification?: boolean;
  extracted_entities?: OCREntity[];
}

export interface QueueToken {
  token_id?: string;
  token_number: string;
  session_id?: string;
  status: QueueStatus;
  priority: Priority;
  estimated_wait?: number;
  department?: string;
  position?: number;
  has_red_flags?: boolean;
}

export interface QueueListResponse {
  tokens: QueueToken[];
  total: number;
}

export interface ConversationState {
  session_id: string;
  current_question_id?: string;
  current_section?: string;
  answered_questions: string[];
  completion_percentage: number;
  is_complete: boolean;
  mode: StreamMode;
  language_code: string;
}

export interface ClinicalHistory {
  [section: string]: unknown;
}

export interface AyushProfile {
  stream: AyushStream;
  dominant_dosha?: string;
  scores: Record<string, number>;
  answers: Record<string, string>;
  completion_percentage?: number;
}

export interface AyushQuestion {
  question_id: string;
  section: string;
  text: Record<string, string>;
  field_type: 'select' | 'multiselect' | 'text';
  options: { value: string; label: string; label_hi: string }[];
  scoring_key?: string;
}

export const AYUSH_STREAMS = [
  { id: 'ayurveda', name: 'Ayurveda', label: 'Ayurveda', description: 'Traditional Indian system of medicine focusing on body constitution and natural therapies', color: '#059669', icon: '🌿' },
  { id: 'siddha', name: 'Siddha', label: 'Siddha', description: 'Ancient Tamil system of medicine emphasizing the body\'s humoral balance', color: '#d97706', icon: '☀️' },
  { id: 'unani', name: 'Unani', label: 'Unani', description: 'Greco-Arabic medicine system using the concept of four humours', color: '#2563eb', icon: '🌙' },
  { id: 'homoeopathy', name: 'Homoeopathy', label: 'Homoeopathy', description: 'System of alternative medicine using highly diluted substances', color: '#7c3aed', icon: '💧' },
  { id: 'yoga_naturopathy', name: 'Yoga & Naturopathy', label: 'Yoga & Naturopathy', description: 'Natural healing through yoga, diet, and lifestyle practices', color: '#0d9488', icon: '🧘' },
];

export const AYUSH_QUESTIONNAIRES: Record<AyushStream, AyushQuestion[]> = {
  ayurveda: [
    { question_id: 'body_build', section: 'Constitution', text: { en: 'What is your general body build?', hi: 'आपका शरीर का आकार कैसा है?' }, field_type: 'select', options: [{ value: 'slim', label: 'Thin / Lean', label_hi: 'पतला / दुबला' }, { value: 'medium', label: 'Medium', label_hi: 'मध्यम' }, { value: 'heavy', label: 'Heavy / Stocky', label_hi: 'भारी / स्थूल' }], scoring_key: 'body_build' },
    { question_id: 'cold_sensitivity', section: 'Constitution', text: { en: 'Do you feel cold easily?', hi: 'क्या आपको आसानी से ठंड लगती है?' }, field_type: 'select', options: [{ value: 'yes', label: 'Yes, always', label_hi: 'हाँ, हमेशा' }, { value: 'sometimes', label: 'Sometimes', label_hi: 'कभी-कभी' }, { value: 'no', label: 'No', label_hi: 'नहीं' }], scoring_key: 'cold_sensitivity' },
    { question_id: 'heat_sensitivity', section: 'Constitution', text: { en: 'Do you feel hot easily?', hi: 'क्या आपको आसानी से गर्मी लगती है?' }, field_type: 'select', options: [{ value: 'yes', label: 'Yes, always', label_hi: 'हाँ, हमेशा' }, { value: 'sometimes', label: 'Sometimes', label_hi: 'कभी-कभी' }, { value: 'no', label: 'No', label_hi: 'नहीं' }], scoring_key: 'heat_sensitivity' },
    { question_id: 'appetite', section: 'Digestion', text: { en: 'How is your appetite?', hi: 'आपकी भूख कैसी है?' }, field_type: 'select', options: [{ value: 'high', label: 'Strong / Always hungry', label_hi: 'तीव्र / हमेशा भूख' }, { value: 'regular', label: 'Regular', label_hi: 'नियमित' }, { value: 'low', label: 'Low / Irregular', label_hi: 'कम / अनियमित' }], scoring_key: 'appetite' },
    { question_id: 'bowel_habits', section: 'Digestion', text: { en: 'How are your bowel habits?', hi: 'आपकी मलत्याग की आदतें कैसी हैं?' }, field_type: 'select', options: [{ value: 'regular', label: 'Regular', label_hi: 'नियमित' }, { value: 'constipated', label: 'Constipated', label_hi: 'कब्ज' }, { value: 'loose', label: 'Loose', label_hi: 'दस्त' }], scoring_key: 'bowel_habits' },
    { question_id: 'sleep_pattern', section: 'General', text: { en: 'How is your sleep?', hi: 'आपकी नींद कैसी है?' }, field_type: 'select', options: [{ value: 'good', label: 'Good / Deep', label_hi: 'अच्छी / गहरी' }, { value: 'disturbed', label: 'Disturbed / Light', label_hi: 'अशांत / हल्की' }, { value: 'insomnia', label: 'Insomnia', label_hi: 'अनिद्रा' }], scoring_key: 'sleep_pattern' },
    { question_id: 'skin_type', section: 'General', text: { en: 'Your skin type is...', hi: 'आपकी त्वचा का प्रकार है...' }, field_type: 'select', options: [{ value: 'dry', label: 'Dry / Rough', label_hi: 'रूखी / खुरदरी' }, { value: 'oily', label: 'Oily / Greasy', label_hi: 'तैलीय / चिकनी' }, { value: 'normal', label: 'Normal / Balanced', label_hi: 'सामान्य / संतुलित' }], scoring_key: 'skin_type' },
  ],
  siddha: [],
  unani: [],
  homoeopathy: [],
  yoga_naturopathy: [],
};
