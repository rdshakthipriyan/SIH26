# MANUAL END-TO-END DEMO FLOW + FULL LIMITATIONS AUDIT
# Date: 2026-08-31
# Instruction: Do NOT modify anything. Report only actual state from source inspection.

====================================================================
SECTION 1: DEMO FLOW (manual test steps)
====================================================================

Prerequisites (must be running):
  - Backend server (FastAPI) with DB accessible
  - Frontend dev server running (npm run dev / equivalent)
  - Mock TTS is the only provider configured unless SARVAM_API_KEY set (see tts.py line 141-142)

Steps (in order):

A. Session start (backend contract preserved - NOT modified)
  POST /api/v1/sessions/start
  Body: { mode: "ayush", stream: "ayurveda", language_code: "hi", is_guest: true }
  Expected: HTTP 200, session_id returned. PatientSession created with mode="ayush".
  NOTE: The session-start endpoint does NOT persist stream to PatientSession or ClinicalCase yet
  (see sessions.py line 55: mode=request.mode only - stream not stored in session record).

B. Conversation start (uses new contract)
  POST /cases/{session_id}/conversation/start
  Body: { mode: "ayush", stream: "ayurveda", language_code: "hi" }
  Expected: HTTP 200, first_question returned (Ayurveda Constitution/BODY_BUILD via stream_questionnaire.py)
  Actual working: YES - conversation_engine __init__ passes stream to get_questionnaire()

C. Answer submission
  POST /cases/{session_id}/conversation/respond
  Body: { answer_text: "Thin", input_mode: "touch", raw_transcript: null }
  Expected: Next Ayurveda question returned; clinical_history updated with extraction hints.
  Actual working: PARTIAL - process_answer stores answer_text + answer_value in conversation_state,
  but answer_extractor.extract_from_answer() may not have Ayurveda-specific concept mappings.

D. Voice input
  1. Click microphone button in ConversationPage -> MediaRecorder starts
  2. Speak answer -> recorder stops
  3. Blob sent to /cases/{session_id}/voice/transcribe
  4. Transcript shown in confirmation modal (showVoiceConfirm true)
  5. Click "Yes" -> handleVoiceConfirm submits with input_mode="voice_edited"
  6. Click "No" -> handleVoiceReject discards; recording stops
  Actual working: YES - all components present in ConversationPage.tsx (verified by source read)

E. TTS playback
  After each question change, speakQuestion() calls voiceApi.speak()
  Backend /speak returns { audio_base64: "..." } from MockTextToSpeechProvider (silence mock)
  ConversationPage.playAudio() creates new Audio() with data:audio/mp3;base64,...
  Actual working: FRONTEND PLAYS AUDIO - but only MOCK audio (b"MOCK_AUDIO_DATA").
  Real Sarvam TTS requires SARVAM_API_KEY env var (see settings/reference); not confirmed configured.

F. Red flags
  After answer with severity >=7 or specific keywords, red_flag_engine.check_red_flags() runs
  Only triggers on status="positive" - negation handled (line 128 of red_flag_engine.py)
  Actual working: YES - checks status explicitly.

G. Queue / Submit
  POST /cases/{session_id}/history/submit -> case.status = "submitted"
  QueueService updates token status.
  Actual working: YES - endpoint exists.

H. Doctor view
  /queue, OCR verify pages present in App routes.
  Stream-specific doctor filter not implemented (no stream filter in doctor endpoints visible).

====================================================================
SECTION 2: ACTUALLY WORKING FEATURES (verified by source inspection)
====================================================================

[VERIFIED WORKING]
  - ModeSelectionPage: selects allopathy vs ayush; selects AYUSH stream; writes sessionStorage
  - ConversationPage: starts conversation, displays questions, submits answers
  - ConversationPage: voice recording (MediaRecorder), STT to backend
  - ConversationPage: voice confirmation modal (showVoiceConfirm)
  - ConversationPage: input_mode tracking (touch / voice / voice_edited via inputModeRef)
  - ConversationPage: TTS audio playback from audio_base64 (playAudio function)
  - ConversationPage: red flag banner display
  - stream_questionnaire.py: unified loader; Ayurveda/Siddha/Unani/Homoeopathy/Yoga questions defined
  - conversation_engine.py: uses get_questionnaire(mode, stream); processes answers with provenance
  - auth.py: stream validator added; PatientSessionStart accepts stream
  - conversation schema: stream in request/response
  - clinical_history API: passes mode+stream to engine; responds with stream
  - clinical_case model: mode_stream column added
  - red_flag_engine.py: checks status!="positive" (negation respected)
  - modeMap.ts: STREAM_OPTIONS array; stream preserved separately from mode
  - api.ts: conversationApi.start() accepts stream parameter

[NOT WORKING / NOT FULLY CONNECTED]
  - TTS: only MockTextToSpeechProvider configured (silent mock audio); real Sarvam only if API key present
  - STT: MockSpeechRecognitionProvider or Sarvam - depends on settings; no confirmation of working real STT
  - Ayurveda scoring: ayush_engine exists but NOT integrated into conversation_engine flow
  - Answer extractor: extract_from_answer exists; Ayurveda-specific extraction hints in questions but mapping to clinical_history keys unverified
  - Session start (/sessions/start): does NOT pass stream to PatientSession or ClinicalCase (sessions.py line 55-69)
  - Stream persistence: conversation/start saves to case.mode_stream but session start doesn't initialize it
  - Doctor dashboard stream filter: not visible in endpoints inspected
  - FHIR / NAMASTE coding: endpoints not fully inspected; mapping code likely missing verification
  - Offline/demo mode: sessionId === 'demo-session-001' navigates to /mode; not a real demo
  - AyushIntakePage: kept intact but NOT integrated with new stream flow (separate static page)

[ARCHITECTURE GAPS]
  - conversation_engine.process_answer uses answer_text OR answer_value; option IDs preserved but answer_extractor may not normalize Ayurveda answers (SLIM/MEDIUM/HEAVY) to clinical concepts
  - No unified provenance for all streams - provenance is per-answer but no aggregate clinical summary
  - Queue status updates after red flags but no stream-specific triage routing
  - No stream-specific question loader called from doctor endpoints

====================================================================
SECTION 3: ALL KNOWN LIMITATIONS (numbered, source-based)
====================================================================

1. TTS IS MOCK ONLY (unless env configured)
   Source: backend/app/services/conversation/tts.py line 141-142
   MockTextToSpeechProvider returns b"MOCK_AUDIO_DATA" encoded.
   No evidence SARVAM_API_KEY is set in this environment.

2. SESSION START DOES NOT PERSIST STREAM
   Source: backend/app/api/v1/sessions.py lines 55, 68
   PatientSession.mode = request.mode; ClinicalCase.mode = request.mode.
   No mode_stream set at session creation - must be added via conversation/start.

3. RED FLAG ENGINE RESPECTS NEGATION BUT NO STREAM RULES
   Source: red_flag_engine.py line 128 (status != "positive")
   No AYUSH-specific red flag rules (e.g., severe dosha imbalance, acute pitta aggravation).

4. AYURVEDA SCORING ENGINE EXISTS BUT NOT WIRED
   Source: backend/app/services/ayush/ayush_engine.py exists
   Not called by conversation_engine (no import/reference found in engine code).
   Profile calculation (prakriti, agni, koshtha, satva) not triggered in flow.

5. ANSWER EXTRACTOR MAY NOT HANDLE AYUSH CONCEPTS
   Source: answer_extractor.py (not fully read, but extraction_hints reference prakriti/agni)
   No verified mapping from language-independent values (SLIM) to clinical_history keys.

6. VOICE CONFIRMATION IS FRONTEND-ONLY; NO BACKEND CONFIRM ENDPOINT
   Source: ConversationPage.tsx has handleVoiceConfirm / handleVoiceReject
   No /conversation/confirm or /transcript/confirm endpoint visible in clinical_history.py.

7. STREAM-SPECIFIC DOCTOR FILTER NOT IMPLEMENTED
   Source: App.tsx routes /queue but no stream query param visible in endpoints.

8. FHIR / NAMASTE / ICD-11 TM2 MAPPING NOT VERIFIED
   Source: ClinicalCase.ayush_profile exists but code mapping (clinical_concept_id -> icd11_tm2_code / namaste_code) not confirmed in conversation_engine.

9. OCR INTEGRATION PARTIAL
   Source: /ocr/verify/:docId route exists; OCRVerifyPage exists
   Document upload and staging visible; human verification flow exists but not fully tested.

10. SESSION STORAGE IS PRIMARY FRONTEND PERSISTENCE
    Source: ConversationPage lines 9-13 use sessionStorage for lang, session, mode, stream
    Backend DB is source of truth; sessionStorage is sync mechanism.

11. NO OFFLINE / DEMO MODE REALITY
    Source: ConversationPage line 39 (sessionId === 'demo-session-001' -> navigate('/mode'))
    Not a functional offline kiosk; just a redirect.

12. AyushIntakePage NOT INTEGRATED WITH NEW FLOW
    Source: App.tsx has /ayush-intake route; AyushIntakePage exists and navigates to /documents
    No stream parameter passed from intake to conversation; static questionnaire never hits backend engine.

13. STT PROVIDER MAY BE MOCK
    Source: backend/app/services/conversation/speech.py not read fully; MockSpeechRecognitionProvider referenced in types but actual provider selection depends on settings.

14. CATEGORY/SECTION MAPPING FOR AYUSH QUESTIONS INCONSISTENT
    Source: stream_questionnaire uses sections "Constitution", "Digestion", "General", "Lifestyle", etc.
    conversation_engine.get_next_question uses question.section for current_section.
    No verified section-to-clinical-category mapping exists.

15. INPUT MODE TRACKING IS FRONTEND-ONLY IN SOME PATHS
    Source: ConversationPage uses inputModeRef; conversation_engine.process_answer accepts input_mode
    But API respond endpoint uses response.input_mode - depends on frontend sending correct value.

16. NO LANGUAGE-PERSISTED ASH-CODE-DEPENDENT FLOW
    Source: stream_questionnaire has text in {en, hi, ta} only for some questions
    Languages beyond ta (tamil) may fall back to en for several AYUSH questions.

17. NO REAL RED FLAG FROM CONVERSATION RESPONSE (only from clinical_history)
    Source: clinical_history.py line 130 — red_flag_engine.check_red_flags called on case.clinical_history
    Conversation response does not include red_flags directly; UI parses extracted_facts.severity >= 7 (line 68 in old ConversationPage). New version uses redFlags state but does not consume backend red_flags from response.

18. NO STREAM-SPECIFIC QUEUE ROUTING
    Source: QueueService updates from clinical_case but no stream-specific branch.

19. NO DOUBLE-CONFIRM FLOW BEFORE SUBMIT
    Source: submit_clinical_history endpoint immediately sets status to "submitted" with no doctor-side review path.

20. NO TERMINOLOGY CODE LOOKUP TABLE
    Source: clinical_concept_id present in question schema but no /codes/lookup or similar endpoint visible in clinical_history.py.

====================================================================
SECTION 4: FILES CHECKED (no edits made for this audit)
====================================================================

Read (not modified):
  - conversation_engine.py (full read; confirmed stream param, get_questionnaire call, process_answer)
  - stream_questionnaire.py (head 90 lines; confirmed 5 stream definitions, option value fields)
  - ConversationPage.tsx (full; confirmed audio, voice, input_mode, stream pass-through)
  - ModeSelectionPage.tsx (full; confirmed stream selection, sessionStorage write, navigation)
  - App.tsx (full; confirmed routes)
  - auth.py (modified earlier; now has stream)
  - modeMap.ts (modified earlier; now has STREAM_OPTIONS)
  - clinical_history.py (modified earlier; now uses stream in engine)
  - sessions.py (full; confirmed session start does not persist stream to case/session)
  - tts.py (full; confirmed mock provider)
  - red_flag_engine.py (full; confirmed negation via status check)
  - clinical_case.py model (read; added mode_stream column earlier)
  - api.ts (modified earlier; start accepts stream)

Not fully read (referenced only):
  - answer_extractor.py (header only; full extraction logic not inspected)
  - conversation/speech.py (STT provider selection)
  - ayush_engine.py (full file exists but not fully read)

====================================================================
SECTION 5: WHAT WOULD BE NEEDED FOR FULL END-TO-END VERIFICATION
====================================================================

To manually verify the complete flow with confidence:

  1. Confirm SARVAM_API_KEY is set (or accept mock audio for demo).
  2. Confirm database is running and accessible.
  3. Confirm both frontend and backend servers are running.
  4. Run step A (session start with stream) -> verify session record.
  5. Verify session start saved stream to case.mode_stream (currently requires conversation/start, not session/start - fix needed if required).
  6. Run step B (conversation start with stream) -> verify first question is Ayurveda Constitution.
  7. Answer 3-5 questions with touch and voice -> verify clinical_history updates with extraction hints.
  8. Introduce a red-flag answer (e.g., chest_pain with severity 8) -> verify red_flags array populated.
  9. Submit history -> verify case.status = "submitted" and queue updated.
  10. Check doctor view for stream filter - not expected to work until implemented.

====================================================================
END OF AUDIT - NO CODE CHANGED FOR THIS OUTPUT
====================================================================
