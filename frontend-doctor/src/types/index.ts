// ─── Core domain types mirroring backend Pydantic schemas ─────────────────────

export type StreamMode = 'allopathy' | 'ayush';
export type AyushStream = 'ayurveda' | 'siddha' | 'unani' | 'homoeopathy' | 'yoga_naturopathy';
export type InputMode = 'voice' | 'touch' | 'voice_edited' | 'ocr';
export type FactStatus = 'positive' | 'negative' | 'unknown' | 'not_provided';
export type QueueStatus = 'waiting' | 'in_progress' | 'history_pending' | 'history_ready' | 'triage_required' | 'completed';
export type Priority = 'normal' | 'high';
export type CaseStatus = 'in_progress' | 'submitted' | 'review' | 'completed';
export type OCRStatus = 'processing' | 'completed' | 'failed';

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

export interface ExtractedFact {
  field: string;
  value: string | number | boolean | null;
  status: FactStatus;
  provenance: Provenance;
  confidence?: number;
}

export interface ClinicalHistory {
  chief_complaint?: ExtractedFact;
  history_of_present_illness?: ExtractedFact;
  current_symptoms?: ExtractedFact[];
  associated_symptoms?: ExtractedFact[];
  aggravating_factors?: ExtractedFact;
  relieving_factors?: ExtractedFact;
  timing?: ExtractedFact;
  severity?: ExtractedFact;
  past_medical_history?: ExtractedFact[];
  surgical_history?: ExtractedFact[];
  medications?: ExtractedFact[];
  allergies?: ExtractedFact[];
  family_history?: ExtractedFact[];
  social_history?: ExtractedFact[];
  review_of_systems?: Record<string, ExtractedFact>;
}

export interface ClinicalCase {
  case_id: string;
  session_id: string;
  language_code: string;
  department: string;
  mode: StreamMode;
  clinical_history?: ClinicalHistory;
  clinical_history_array?: Array<{fact_id: string; category: string; label: string; value: string; provenance: Provenance}>;
  ayush_profile?: AyushProfile;
  conversation_state?: ConversationState;
  draft_answers?: DraftAnswer[];
  red_flags?: RedFlag[];
  has_red_flags: boolean;
  triage_required: boolean;
  priority: Priority;
  provenance?: Record<string, Provenance>;
  status: CaseStatus;
  completion_percentage: number;
  abdm_synced?: boolean;
}

// ─── Conversation ────────────────────────────────────────────────────────────
export interface QuestionOption {
  value: string;
  label: string;
  label_hi?: string;
  label_ta?: string;
  label_te?: string;
  label_ml?: string;
}

export interface Question {
  question_id: string;
  section: string;
  section_order: number;
  text: Record<string, string>;
  text_hi?: string;
  text_ta?: string;
  text_te?: string;
  text_ml?: string;
  field_type: 'text' | 'select' | 'multiselect' | 'number' | 'severity' | 'duration';
  options?: QuestionOption[];
  conditional_rules?: { depends_on: string; value: string }[];
  clinical_concept_id?: string;
  required: boolean;
  order: number;
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

export interface DraftAnswer {
  question_id: string;
  answer_text: string;
  input_mode: InputMode;
  language: string;
}

// ─── AYUSH Profile ───────────────────────────────────────────────────────────
export interface AyushAnswer {
  question_id: string;
  question_text: string;
  answer: string;
  answer_text: string;
  timestamp: string;
  input_mode: InputMode;
  language: string;
}

export interface PrakritiScore {
  vata: number;
  pitta: number;
  kapha: number;
  dominant: string;
  indicators: string[];
}

export interface AyushProfile {
  prakriti?: PrakritiScore;
  agni?: string;
  koshtha?: string;
  ahara_vihara?: string;
  satva?: string;
  completion_percentage?: number;
  answers: AyushAnswer[];
  scores?: Record<string, number>;
}

// ─── AYUSH Stream definitions (UI labels – no backend change) ───────────────
export const AYUSH_STREAMS: { id: AyushStream; label: string; label_hi: string; description: string; icon: string; color: string }[] = [
  { id: 'ayurveda', label: 'Ayurveda', label_hi: 'आयुर्वेद', description: 'Traditional Indian system of medicine focusing on body constitution and natural therapies', icon: '🌿', color: 'emerald' },
  { id: 'siddha', label: 'Siddha', label_hi: 'சித்தா', description: 'Ancient Tamil system of medicine emphasizing the body\'s humoral balance', icon: '🔥', color: 'amber' },
  { id: 'unani', label: 'Unani', label_hi: 'यूनानी', description: 'Greco-Arabic medicine system using the concept of four humours', icon: '💧', color: 'blue' },
  { id: 'homoeopathy', label: 'Homoeopathy', label_hi: 'होम्योपैथी', description: 'System of alternative medicine using highly diluted substances', icon: '⚕️', color: 'violet' },
  { id: 'yoga_naturopathy', label: 'Yoga & Naturopathy', label_hi: 'योग एवं प्राकृतिक चिकित्सा', description: 'Natural healing through yoga, diet, and lifestyle practices', icon: '🧘', color: 'teal' },
];

// ─── Red Flags ──────────────────────────────────────────────────────────────
export interface RedFlag {
  type: string;
  severity: string;
  description: string;
  detected_at?: string;
  requires_immediate_attention: boolean;
}

// ─── OCR / Documents ─────────────────────────────────────────────────────────
export interface OCREntity {
  label: string;
  fact_id?: string;
  type: string;
  value: string;
  confidence: number;
  requires_verification: boolean;
  provenance?: Provenance;
  warning?: string;
}

export interface ClinicalDocument {
  document_id: string;
  session_id: string;
  document_type: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  ocr_provider?: string;
  raw_text?: string;
  ocr_confidence?: number;
  structured_entities?: OCREntity[];
  processing_status: OCRStatus;
  warnings?: string[];
  requires_verification?: boolean;
  created_at?: string;
}

// ─── Queue ──────────────────────────────────────────────────────────────────
export interface QueueToken {
  token_id: string;
  token_number: string;
  department: string;
  mode: StreamMode;
  session_id?: string;
  status: QueueStatus;
  priority: Priority;
  has_red_flags: boolean;
  position: number;
  called_at?: string;
  completed_at?: string;
  physician_id?: string;
}

// ─── Doctor Dashboard ────────────────────────────────────────────────────────
export interface DoctorCase {
  case_id: string;
  session_id: string;
  patient_name: string;
  department: string;
  mode: StreamMode;
  language: string;
  status: CaseStatus;
  has_red_flags: boolean;
  priority: Priority;
  queue_position?: number;
  wait_time_mins?: number;
  created_at: string;
  updated_at: string;
}

// ─── FHIR ───────────────────────────────────────────────────────────────────
export interface FHIRBundle {
  resourceType: string;
  id: string;
  type: string;
  entry?: FHIREntry[];
}

export interface FHIREntry {
  resource: Record<string, unknown>;
}

// ─── API Response wrappers ───────────────────────────────────────────────────
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

export interface QueueListResponse {
  tokens: QueueToken[];
  total: number;
  waiting: number;
  in_progress: number;
  completed: number;
}

// ─── Stream-specific AYUSH questionnaire (client-side, keyed by stream) ──────
// Each stream has its own questions – no backend changes needed.
export interface AyushQuestion {
  question_id: string;
  section: string;
  text: Record<string, string>;
  field_type: 'select' | 'multiselect' | 'text';
  options: { value: string; label: string; label_hi: string }[];
  scoring_key?: string;
}

export const AYUSH_QUESTIONNAIRES: Record<AyushStream, AyushQuestion[]> = {
  ayurveda: [
    { question_id: 'body_build', section: 'Constitution', text: { en: 'What is your general body build?', hi: 'आपका शरीर का आकार कैसा है?' }, field_type: 'select', options: [{ value: 'slim', label: 'Thin / Lean', label_hi: 'पतला / दुबला' }, { value: 'medium', label: 'Medium', label_hi: 'मध्यम' }, { value: 'heavy', label: 'Heavy / Stocky', label_hi: 'भारी / स्थूल' }], scoring_key: 'body_build' },
    { question_id: 'cold_sensitivity', section: 'Constitution', text: { en: 'Do you feel cold easily?', hi: 'क्या आपको आसानी से ठंड लगती है?' }, field_type: 'select', options: [{ value: 'yes', label: 'Yes, always', label_hi: 'हाँ, हमेशा' }, { value: 'sometimes', label: 'Sometimes', label_hi: 'कभी-कभी' }, { value: 'no', label: 'No', label_hi: 'नहीं' }], scoring_key: 'cold_sensitivity' },
    { question_id: 'heat_sensitivity', section: 'Constitution', text: { en: 'Do you feel hot easily?', hi: 'क्या आपको आसानी से गर्मी लगती है?' }, field_type: 'select', options: [{ value: 'yes', label: 'Yes, always', label_hi: 'हाँ, हमेशा' }, { value: 'sometimes', label: 'Sometimes', label_hi: 'कभी-कभी' }, { value: 'no', label: 'No', label_hi: 'नहीं' }], scoring_key: 'heat_sensitivity' },
    { question_id: 'appetite', section: 'Digestion', text: { en: 'How is your appetite?', hi: 'आपकी भूख कैसी है?' }, field_type: 'select', options: [{ value: 'high', label: 'Strong / Always hungry', label_hi: 'तीव्र / हमेशा भूख' }, { value: 'regular', label: 'Regular', label_hi: 'नियमित' }, { value: 'low', label: 'Low / Irregular', label_hi: 'कम / अनियमित' }], scoring_key: 'appetite' },
    { question_id: 'bowel_habits', section: 'Digestion', text: { en: 'How are your bowel habits?', hi: 'आपकी आँतों की आदतें कैसी हैं?' }, field_type: 'select', options: [{ value: 'regular', label: 'Regular', label_hi: 'नियमित' }, { value: 'constipation', label: 'Prone to constipation', label_hi: 'कब्ज की प्रवृत्ति' }, { value: 'loose', label: 'Loose / Frequent', label_hi: 'ढीला / बार-बार' }], scoring_key: 'bowel_habits' },
    { question_id: 'skin_type', section: 'Physical', text: { en: 'What is your skin type?', hi: 'आपकी त्वचा का प्रकार कैसा है?' }, field_type: 'select', options: [{ value: 'dry', label: 'Dry', label_hi: 'सूखी' }, { value: 'oily', label: 'Oily', label_hi: 'तेलीय' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }], scoring_key: 'skin_type' },
    { question_id: 'sleep_quality', section: 'Lifestyle', text: { en: 'How is your sleep quality?', hi: 'आपकी नींद की गुणवत्ता कैसी है?' }, field_type: 'select', options: [{ value: 'deep', label: 'Deep & refreshing', label_hi: 'गहरी और ताज़ा' }, { value: 'light', label: 'Light / Disturbed', label_hi: 'हल्की / बाधित' }, { value: 'insomnia', label: 'Trouble sleeping', label_hi: 'नींद में परेशानी' }], scoring_key: 'sleep_quality' },
    { question_id: 'stress_response', section: 'Lifestyle', text: { en: 'How do you handle stress?', hi: 'आप तनाव कैसे से निपटते हैं?' }, field_type: 'select', options: [{ value: 'calm', label: 'Stay calm', label_hi: 'शांत रहते हैं' }, { value: 'anxious', label: 'Feel anxious / worried', label_hi: 'चिंतित / परेशान' }, { value: 'irritable', label: 'Get irritated easily', label_hi: 'जल्दी चिड़चिड़े' }], scoring_key: 'stress_response' },
  ],
  siddha: [
    { question_id: 'body_temperature', section: 'Constitution', text: { en: 'Do you usually feel hot or cold?', hi: 'आपको आमतौर पर गर्मी या ठंड लगती है?' }, field_type: 'select', options: [{ value: 'always_hot', label: 'Always feel hot', label_hi: 'हमेशा गर्मी लगती है' }, { value: 'always_cold', label: 'Always feel cold', label_hi: 'हमेशा ठंड लगती है' }, { value: 'normal', label: 'Normal / Balanced', label_hi: 'सामान्य / संतुलित' }], scoring_key: 'body_temperature' },
    { question_id: 'skin_complexion', section: 'Physical', text: { en: 'What is your skin complexion?', hi: 'आपकी त्वचा का रंग कैसा है?' }, field_type: 'select', options: [{ value: 'dark', label: 'Dark / Dull', label_hi: 'गहरा / मैला' }, { value: 'fair', label: 'Fair / Bright', label_hi: 'गोरा / चमकीला' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }], scoring_key: 'skin_complexion' },
    { question_id: 'eating_speed', section: 'Digestion', text: { en: 'How fast do you eat?', hi: 'आप कितनी तेज़ी से खाते हैं?' }, field_type: 'select', options: [{ value: 'slow', label: 'Slow', label_hi: 'धीमा' }, { value: 'moderate', label: 'Moderate', label_hi: 'मध्यम' }, { value: 'fast', label: 'Fast', label_hi: 'तेज़' }], scoring_key: 'eating_speed' },
    { question_id: 'stamina', section: 'Lifestyle', text: { en: 'How is your physical stamina?', hi: 'आपकी शारीरिक सहनशक्ति कैसी है?' }, field_type: 'select', options: [{ value: 'high', label: 'High stamina', label_hi: 'उच्च सहनशक्ति' }, { value: 'moderate', label: 'Moderate', label_hi: 'मध्यम' }, { value: 'low', label: 'Low / Fatigue easily', label_hi: 'कम / आसानी से थकान' }], scoring_key: 'stamina' },
    { question_id: 'mental_activity', section: 'Mental', text: { en: 'How is your mental activity?', hi: 'आपकी मानसिक गतिविधि कैसी है?' }, field_type: 'select', options: [{ value: 'very_active', label: 'Very active', label_hi: 'बहुत सक्रिय' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }, { value: 'slow', label: 'Slow / Forgetful', label_hi: 'धीमा / भूलने वाला' }], scoring_key: 'mental_activity' },
    { question_id: 'voice_quality', section: 'Physical', text: { en: 'What is your voice quality?', hi: 'आपकी आवाज़ की गुणवत्ता कैसी है?' }, field_type: 'select', options: [{ value: 'harsh', label: 'Harsh / Hoarse', label_hi: 'कर्कश / भारी' }, { value: 'soft', label: 'Soft / Clear', label_hi: 'मुलायम / स्पष्ट' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }], scoring_key: 'voice_quality' },
    { question_id: 'hair_condition', section: 'Physical', text: { en: 'What is your hair condition?', hi: 'आपके बालों की स्थिति कैसी है?' }, field_type: 'select', options: [{ value: 'dry_brittle', label: 'Dry / Brittle', label_hi: 'सूखे / टूटने वाले' }, { value: 'oily', label: 'Oily / Greasy', label_hi: 'तेलीय' }, { value: 'normal', label: 'Normal / Healthy', label_hi: 'सामान्य / स्वस्थ' }], scoring_key: 'hair_condition' },
    { question_id: 'sweating', section: 'Physical', text: { en: 'How is your sweating pattern?', hi: 'आपका पसीना आने का पैटर्न कैसा है?' }, field_type: 'select', options: [{ value: 'excessive', label: 'Excessive', label_hi: 'अधिक' }, { value: 'moderate', label: 'Moderate', label_hi: 'मध्यम' }, { value: 'less', label: 'Less / Minimal', label_hi: 'कम / न्यूनतम' }], scoring_key: 'sweating' },
  ],
  unani: [
    { question_id: 'humour_balance', section: 'Constitution', text: { en: 'How do you describe your temperament?', hi: 'आप अपने मिजाज़ का वर्णन कैसे करेंगे?' }, field_type: 'select', options: [{ value: 'sanguine', label: 'Warm & cheerful', label_hi: 'गर्म और प्रसन्न' }, { value: 'phlegmatic', label: 'Cool & calm', label_hi: 'ठंडा और शांत' }, { value: 'choleric', label: 'Hot & irritable', label_hi: 'गर्म और चिड़चिड़ा' }, { value: 'melancholic', label: 'Cold & thoughtful', label_hi: 'ठंडा और विचारशील' }], scoring_key: 'humour_balance' },
    { question_id: 'body_fluid', section: 'Constitution', text: { en: 'Do you feel thirsty often?', hi: 'क्या आपको अक्सर प्यास लगती है?' }, field_type: 'select', options: [{ value: 'excessive', label: 'Yes, frequently', label_hi: 'हाँ, बार-बार' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }, { value: 'less', label: 'Rarely feel thirsty', label_hi: 'कभी-कभी प्यास लगती है' }], scoring_key: 'body_fluid' },
    { question_id: 'digestion_strength', section: 'Digestion', text: { en: 'How would you rate your digestion?', hi: 'आप अपने पाचन को कैसे रेट करेंगे?' }, field_type: 'select', options: [{ value: 'strong', label: 'Strong – quick digestion', label_hi: 'तीव्र – जल्दी पचता है' }, { value: 'average', label: 'Average', label_hi: 'औसत' }, { value: 'weak', label: 'Weak – slow digestion', label_hi: 'कमज़ोर – धीरे पचता है' }], scoring_key: 'digestion_strength' },
    { question_id: 'stool_quality', section: 'Digestion', text: { en: 'What is your stool quality?', hi: 'आपकी मल की गुणवत्ता कैसी है?' }, field_type: 'select', options: [{ value: 'soft', label: 'Soft / Loose', label_hi: 'नरम / ढीला' }, { value: 'normal', label: 'Normal / Formed', label_hi: 'सामान्य / बना हुआ' }, { value: 'hard', label: 'Hard / Dry', label_hi: 'कठोर / सूखा' }], scoring_key: 'stool_quality' },
    { question_id: 'skin_texture', section: 'Physical', text: { en: 'How would you describe your skin texture?', hi: 'आप अपनी त्वचा की बनावट का वर्णन कैसे करेंगे?' }, field_type: 'select', options: [{ value: 'rough', label: 'Rough / Dry', label_hi: 'खुरदरा / सूखा' }, { value: 'smooth', label: 'Smooth / Oily', label_hi: 'चिकना / तेलीय' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }], scoring_key: 'skin_texture' },
    { question_id: 'sleep_pattern', section: 'Lifestyle', text: { en: 'How is your sleep pattern?', hi: 'आपका नींद का पैटर्न कैसा है?' }, field_type: 'select', options: [{ value: 'deep', label: 'Deep sleep', label_hi: 'गहरी नींद' }, { value: 'light', label: 'Light / Restless', label_hi: 'हल्की / बेचैन' }, { value: 'disturbed', label: 'Disturbed / Insomnia', label_hi: 'बाधित / अनिद्रा' }], scoring_key: 'sleep_pattern' },
    { question_id: 'anger_response', section: 'Mental', text: { en: 'How do you respond to anger?', hi: 'आप गुस्से पर कैसे प्रतिक्रिया देते हैं?' }, field_type: 'select', options: [{ value: 'slow_to_anger', label: 'Slow to anger', label_hi: 'धीरे गुस्सा होते हैं' }, { value: 'moderate', label: 'Moderate', label_hi: 'मध्यम' }, { value: 'quick_to_anger', label: 'Quick to anger', label_hi: 'जल्दी गुस्सा होते हैं' }], scoring_key: 'anger_response' },
    { question_id: 'body_odor', section: 'Physical', text: { en: 'How is your body odour?', hi: 'आपकी शरीर की गंध कैसी है?' }, field_type: 'select', options: [{ value: 'strong', label: 'Strong', label_hi: 'तेज़' }, { value: 'mild', label: 'Mild', label_hi: 'हल्की' }, { value: 'normal', label: 'Normal', label_hi: 'सामान्य' }], scoring_key: 'body_odor' },
  ],
  homoeopathy: [
    { question_id: 'thermal_preference', section: 'Constitution', text: { en: 'Do you prefer hot or cold environments?', hi: 'आप गर्म या ठंडा वातावरण किसे पसंद करते हैं?' }, field_type: 'select', options: [{ value: 'hot', label: 'Prefer hot', label_hi: 'गर्म पसंद करते हैं' }, { value: 'cold', label: 'Prefer cold', label_hi: 'ठंडा पसंद करते हैं' }, { value: 'neutral', label: 'No preference', label_hi: 'कोई प्राथमिकता नहीं' }], scoring_key: 'thermal_preference' },
    { question_id: 'thirst_level', section: 'Fluids', text: { en: 'How is your thirst?', hi: 'आपकी प्यास कैसी है?' }, field_type: 'select', options: [{ value: 'large_quantities', label: 'Drinks large quantities', label_hi: 'बड़ी मात्रा में पीते हैं' }, { value: 'small_quantities', label: 'Small sips frequently', label_hi: 'बार-बार छोटे घूंट' }, { value: 'no_thirst', label: 'Little or no thirst', label_hi: 'कम या बिना प्यास' }], scoring_key: 'thirst_level' },
    { question_id: 'food_desires', section: 'Cravings', text: { en: 'What foods do you crave?', hi: 'आपको किस चीज़ की ख्वाहिश होती है?' }, field_type: 'select', options: [{ value: 'salty', label: 'Salty / Savory', label_hi: 'नमकीन' }, { value: 'sweet', label: 'Sweet', label_hi: 'मीठा' }, { value: 'sour', label: 'Sour / Acidic', label_hi: 'खट्टा' }, { value: 'nothing_specific', label: 'Nothing specific', label_hi: 'कोई विशेष नहीं' }], scoring_key: 'food_desires' },
    { question_id: 'food_aversions', section: 'Cravings', text: { en: 'What foods do you dislike or avoid?', hi: 'आप किन खाद्य पदार्थों से चिढ़ते हैं?' }, field_type: 'select', options: [{ value: 'milk', label: 'Milk / Dairy', label_hi: 'दूध / डेयरी' }, { value: 'meat', label: 'Meat', label_hi: 'मांस' }, { value: 'eggs', label: 'Eggs', label_hi: 'अंडे' }, { value: 'nothing_specific', label: 'Nothing specific', label_hi: 'कोई विशेष नहीं' }], scoring_key: 'food_aversions' },
    { question_id: 'position_sleep', section: 'Sleep', text: { en: 'How do you prefer to sleep?', hi: 'आप कैसे सोना पसंद करते हैं?' }, field_type: 'select', options: [{ value: 'on_back', label: 'On back', label_hi: 'पीठ के बल' }, { value: 'on_stomach', label: 'On stomach', label_hi: 'पेट के बल' }, { value: 'on_side', label: 'On side', label_hi: 'किसी एक करवट' }], scoring_key: 'position_sleep' },
    { question_id: 'sweating', section: 'Physical', text: { en: 'Do you sweat? Where?', hi: 'क्या आपको पसीना आता है? कहाँ?' }, field_type: 'select', options: [{ value: 'none', label: 'No sweating', label_hi: 'कोई पसीना नहीं' }, { value: 'head', label: 'Mostly on head', label_hi: 'ज़्यादातर सिर पर' }, { value: 'hands_feet', label: 'Hands and feet', label_hi: 'हाथ और पैर' }, { value: 'general', label: 'General / All over', label_hi: 'सामान्य / पूरे शरीर' }], scoring_key: 'sweating' },
    { question_id: 'emotional_state', section: 'Mental', text: { en: 'How would you describe your emotional state?', hi: 'आप अपनी भावनात्मक स्थिति का वर्णन कैसे करेंगे?' }, field_type: 'select', options: [{ value: 'cheerful', label: 'Cheerful / Laughing', label_hi: 'प्रसन्न / हंसते रहते हैं' }, { value: 'sad', label: 'Sad / Weeping', label_hi: 'उदास / रोते हैं' }, { value: 'anxious', label: 'Anxious / Fearful', label_hi: 'चिंतित / डरपोक' }, { value: 'irritable', label: 'Irritable / Angry', label_hi: 'चिड़चिड़े / गुस्सैल' }], scoring_key: 'emotional_state' },
    { question_id: 'left_right', section: 'Laterality', text: { en: 'Do symptoms affect one side of the body more?', hi: 'क्या लक्षण शरीर के एक तरफ ज़्यादा प्रभावित करते हैं?' }, field_type: 'select', options: [{ value: 'left', label: 'Mostly left side', label_hi: 'ज़्यादातर बाईं तरफ' }, { value: 'right', label: 'Mostly right side', label_hi: 'ज़्यादातर दाईं तरफ' }, { value: 'both', label: 'Both sides equally', label_hi: 'दोनों तरफ बराबर' }], scoring_key: 'left_right' },
  ],
  yoga_naturopathy: [
    { question_id: 'daily_activity', section: 'Lifestyle', text: { en: 'How physically active are you daily?', hi: 'आप रोज़ाना कितने शारीरिक रूप से सक्रिय हैं?' }, field_type: 'select', options: [{ value: 'sedentary', label: 'Mostly sitting', label_hi: 'ज़्यादातर बैठे' }, { value: 'moderate', label: 'Some walking / movement', label_hi: 'कुछ चलना-फिरना' }, { value: 'active', label: 'Regular exercise / Yoga', label_hi: 'नियमित व्यायाम / योग' }], scoring_key: 'daily_activity' },
    { question_id: 'water_intake', section: 'Diet', text: { en: 'How much water do you drink daily?', hi: 'आप रोज़ाना कितना पानी पीते हैं?' }, field_type: 'select', options: [{ value: 'less_than_2l', label: 'Less than 2 litres', label_hi: '2 लीटर से कम' }, { value: '2_to_3l', label: '2–3 litres', label_hi: '2-3 लीटर' }, { value: 'more_than_3l', label: 'More than 3 litres', label_hi: '3 लीटर से ज़्यादा' }], scoring_key: 'water_intake' },
    { question_id: 'diet_type', section: 'Diet', text: { en: 'What type of diet do you follow?', hi: 'आप किस प्रकार का आहार लेते हैं?' }, field_type: 'select', options: [{ value: 'vegetarian', label: 'Vegetarian', label_hi: 'शाकाहारी' }, { value: 'vegan', label: 'Vegan', label_hi: 'वीगन' }, { value: 'non_vegetarian', label: 'Non-vegetarian', label_hi: 'मांसाहारी' }, { value: 'mixed', label: 'Mixed', label_hi: 'मिश्रित' }], scoring_key: 'diet_type' },
    { question_id: 'sun_exposure', section: 'Nature', text: { en: 'How much natural sunlight do you get?', hi: 'आपको कितनी प्राकृतिक धूप मिलती है?' }, field_type: 'select', options: [{ value: 'minimal', label: 'Minimal / Indoor', label_hi: 'कम / घर के अंदर' }, { value: 'moderate', label: 'Some time outdoors', label_hi: 'कुछ समय बाहर' }, { value: 'good', label: 'Good sun exposure', label_hi: 'अच्छी धूप' }], scoring_key: 'sun_exposure' },
    { question_id: 'breathing', section: 'Breath', text: { en: 'Do you practice any breathing exercises?', hi: 'क्या आप कोई श्वास व्यायाम करते हैं?' }, field_type: 'select', options: [{ value: 'none', label: 'No', label_hi: 'नहीं' }, { value: 'pranayama', label: 'Yes – Pranayama / Yoga breathing', label_hi: 'हाँ – प्राणायाम / योग श्वास' }, { value: 'other', label: 'Other breathing techniques', label_hi: 'अन्य श्वास तकनीक' }], scoring_key: 'breathing' },
    { question_id: 'bowel_movement', section: 'Digestion', text: { en: 'How regular are your bowel movements?', hi: 'आपकी आँतों की गति कितनी नियमित है?' }, field_type: 'select', options: [{ value: 'regular', label: 'Daily, regular', label_hi: 'रोज़ाना, नियमित' }, { value: 'irregular', label: 'Sometimes irregular', label_hi: 'कभी-कभी अनियमित' }, { value: 'constipation', label: 'Often constipated', label_hi: 'अक्सर कब्ज' }], scoring_key: 'bowel_movement' },
    { question_id: 'stress_level', section: 'Mental', text: { en: 'How would you rate your current stress level?', hi: 'आप अपने वर्तमान तनाव के स्तर को कैसे रेट करेंगे?' }, field_type: 'select', options: [{ value: 'low', label: 'Low / Manageable', label_hi: 'कम / नियंत्रित' }, { value: 'moderate', label: 'Moderate', label_hi: 'मध्यम' }, { value: 'high', label: 'High / Overwhelming', label_hi: 'उच्च / असहनीय' }], scoring_key: 'stress_level' },
    { question_id: 'sleep_hours', section: 'Rest', text: { en: 'How many hours do you sleep daily?', hi: 'आप रोज़ाना कितने घंटे सोते हैं?' }, field_type: 'select', options: [{ value: 'less_than_6', label: 'Less than 6 hours', label_hi: '6 घंटे से कम' }, { value: '6_to_8', label: '6–8 hours', label_hi: '6-8 घंटे' }, { value: 'more_than_8', label: 'More than 8 hours', label_hi: '8 घंटे से ज़्यादा' }], scoring_key: 'sleep_hours' },
  ],
};
