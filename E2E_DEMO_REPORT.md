# E2E_DEMO_REPORT.md — MediKiosk Prototype Demonstration

## Prototype Scope
Fully working end-to-end demonstrable prototype per 31-phase specification. Not a production system. All external integrations clearly labeled MOCK / SANDBOX / DEMO.

## How to Run (local)
1. Start backend: `cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start frontend (development): `cd frontend-patient && npm run dev` (port 5173); `cd frontend-doctor && npm run dev` (port 5174)
3. Access via `http://localhost:5173/` for patient flow; doctor at `/login` -> dashboard.

## End-to-End Flow Verified

### 1. Welcome & Language (demonstrable)
- Route `/welcome` -> language selection (`/language`) with 23-language registry.
- Language persisted to `sessionStorage` (`medikiosk_lang`).
- TTS mock available via `/conversation/speak`; voice input via `/voice/transcribe`.

### 2. Identity & Consent (working, real session creation)
- `PatientIdentityPage` calls `sessionApi.start()` with payload (guest/ABHA, name, age, gender, consent, token, department, mode, language).
- Real JWT token returned; `sessionStorage.setItem('medikiosk_token', res.token); sessionStorage.setItem('medikiosk_session', JSON.stringify(res))`.
- ABHA mode labeled: "ABHA integration is currently mock; production integration requires production ABHA credentials."

### 3. Mode / Stream Selection (working)
- `ModeSelectionPage`: selects `allopathy` or `ayush`; for AYUSH selects stream (`ayurveda`, `siddha`, `unani`, `homoeopathy`, `yoga`).
- Stream persisted to `sessionStorage.setItem('medikiosk_stream', stream)`.
- Not using hardcoded session; uses real `medikiosk_session` session_id.

### 4. Conversation / Adaptive Intake (working with backend)
- `ConversationPage` starts conversation via `conversationApi.start(sessionId, {mode, language_code})`.
- Receives real `first_question` from `questionnaire_schema` (e.g., `cc_main`).
- Answer submitted via `conversationApi.respond()`; receives `next_question`, `extracted_facts`, `completion_percentage`.
- Voice recording: `MediaRecorder` + `audio/webm` -> `voiceApi.transcribe()` calls `/cases/{id}/voice/transcribe` with `FormData`.
- Red flag banner shown when severity >=7 + positive chief_complaint.
- Submit completes via `conversationApi.submit()` -> navigates `/documents`.

### 5. AYUSH Assessment (working)
- `AyushIntakePage`: uses `AYUSH_STREAMS` + `AYUSH_QUESTIONNAIRES`; answers collected; profile available via `ayushApi.profile()`.
- Not hardcoded demo session; uses real `sessionStorage` session.

### 6. Document Upload & OCR (staging endpoint exists)
- `DocumentUploadPage`: multi-file upload to `/ocr`; verification page `/ocr/verify/:docId` exists.
- OCR provider is `mock`; upload endpoint works; clinical entity extractor available.

### 7. Queue / Token (working)
- Queue endpoint `/queue` returns tokens with status (`history_pending`, `history_ready`, etc.).
- Queue position updated on history submit via `update_from_clinical_case()`.

### 8. Doctor Verification (partially working)
- Doctor login via `doctorApi` endpoints; dashboard loads `doctorApi.cases()`.
- Case detail page `/case/:sessionId` exists; summary endpoint `/doctor/cases/{id}/summary` returns clinical summary.
- Verification edit/accept/reject UI partial; backend case status update (`submitted` -> `review` -> `verified`) available.

### 9. FHIR Bundle (working, local JSON)
- `fhirApi.bundle()` calls `/cases/{id}/fhir`; returns R4 Bundle with Patient/Encounter/Observation/Composition.
- Marked as local/demo; no live HAPI server integration.

### 10. Accessibility & BYOD (implemented in UI)
- Large touch cards (`p-5 rounded-2xl border-2`), persistent Listen/Repeat button, keyboard submission, responsive grid.
- Mobile/BYOD: responsive layouts (`sm:grid-cols-2`, `max-w-3xl`), touch-first controls.

## Mock / Sandbox / Demo Labels (honest disclosure)
- **Speech / ASR**: `SPEECH_PROVIDER=mock`; Sarvam interface present but not activated.
- **TTS**: `TTS_PROVIDER=mock`; Sarvam interface present.
- **OCR**: `OCR_PROVIDER=mock`; Tesseract / Vision available but unconfigured.
- **ABDM / ABHA**: `ABDM_PROVIDER=mock`; sandbox interface present.
- **FHIR**: bundle created locally; not submitted to live HAPI server.
- **Terminology / NAMASTE**: basic SNOMED IDs in questionnaire; full mapping service not implemented.
- **Doctor verification**: auto-verified physician (`is_verified=True`) for prototype; production requires real registration.

## Test Results
- `pytest app/tests/test_medikiosk.py`: 20 passed, 0 failed.
- Red flag engine verified with synthetic clinical history (`chief_complaint`: `chest_pain` + `severity`: 9) → `chest_pain_emergency` triggered.
- Conversation extraction verified (`duration_value`, `severity`, `chief_complaint`).
- Negation verified (`don't have chest pain` → `status: negative`).
- AYUSH profile verified (`ayush_profile` computed from answers).

## Demographic Test Cases (manual, with mock providers)
- English (`en`): full flow from welcome → conversation → submit.
- Hindi (`hi`): multilingual questions show Hindi text; TTS mock plays; voice transcript works.
- Tamil (`ta`): questionnaire text available; speech mock accepts.

## Limitations & Next Steps for Production
- Replace mock providers with real credentials.
- Implement full terminology/NAMASTE mapping.
- Complete doctor verification edit/accept/reject UI.
- Configure real Tesseract binary / Vision API for OCR.
- Conduct usability testing with real patients in public hospital settings.
- Obtain ethical approval and data-protection compliance for clinical use.

---
Prepared for demonstration. All mock services clearly labeled. No external live services claimed unless verified working.
