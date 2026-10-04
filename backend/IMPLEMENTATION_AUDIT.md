# MediKiosk Implementation Audit Report

Generated: 2026-08-29
Project: SIH26047 — Patient Case-Taking Software (Ministry of AYUSH)

## 1. Existing Repository State (from inspection)

### Directory layout
- `backend/app/` — FastAPI backend (exists, partial)
- `frontend-patient/src/` — empty scaffolding (no components/pages)
- `frontend-doctor/src/` — empty scaffolding (no components/pages)
- `alembic/` — migrations exist
- `docker-compose.yml` — exists
- `.env` / `.env.example` — exist
- `README.md` / `PROJECT_STATUS.md` — exist
- `requirements.txt` — exists
- `tests/app/tests/test_medikiosk.py` — exists (20 tests)

### Backend modules audited
- `models/`: patient, clinical_case, document, physician, queue, base
- `schemas/`: auth, clinical_history, conversation, ayush, fhir, ocr, queue, languages, tts
- `api/v1/`: clinical_history.py, endpoints.py, sessions.py
- `core/`: config, database, security
- `services/`: conversation (engine, extractor, questionnaire, speech, tts), ayush (engine only), triage (red_flag_engine), ocr (provider, entity_extractor), fhir (builder), queue (engine), abdm (empty-ish)

### Feature matrix (actual from code inspection)

FEATURE                     | STATUS | NOTES
----------------------------|--------|--------------------------------------------------
Patient registration      | EX | `models/patient.py`; session start endpoint
Guest mode                 | EX | `is_guest` + `temp_id`; session flow
ABHA abstraction           | PART | `abha_id` / `abha_address` fields; no live adapter
OPD token routing          | EX | `QueueToken`; queue_service
Allopathy intake           | EX | `conversation_engine`; `clinical_history`; extraction
Ayurveda                  | PART | `ayush_engine.py` has Ayurveda questions only
Unani                     | MIS | No Unani questionnaire/engine
Siddha                    | MIS | No Siddha questionnaire/engine
Yoga/Naturopathy           | MIS | No dedicated module
Homoeopathy               | MIS | No dedicated module
Multilingual UI            | PART | 5-language registry (en/hi/ta/te/ml); frontends empty
ASR                       | PART | `speech.py`; mock provider abstraction
TTS                       | PART | `tts.py`; mock provider abstraction
Conversation engine       | EX | adaptive; conditionals; state tracking
Clinical extraction       | EX | `answer_extractor`; provenance
Negation                  | EX | engine respects `negative` status
Unknown state             | EX | `status = "unknown"` supported in model
Corrections              | PART | conversation state overwritten; provenance preserved
Red flags                 | EX | `red_flag_engine`; deterministic rules
Document upload           | EX | `clinical_document`; upload endpoint
Printed OCR               | PART | `ocr_provider` mock + tesseract reference
Handwriting OCR           | PART | `ocr_provider` references handwriting; no dedicated handler
Document entity extraction | EX | `clinical_entity_extractor`; JSON structured
OCR verification         | MIS | No doctor verification gate / workflow
Medical timeline         | MIS | No chronological timeline model/endpoint
Doctor dashboard         | MIS | `frontend-doctor/src` empty; no doctor UI built
Provenance               | EX | provenance dict in clinical_history, answers
FHIR                     | PART | `fhir_builder` exists; basic bundle generation
ABDM abstraction         | PART | `services/abdm/` directory exists (minimal)
NAMASTE mapping         | MIS | Terminology layer missing
ICD-11 TM1 mapping       | MIS | Terminology layer missing
Offline mode             | MIS | No IndexedDB / sync queue implemented
Sync/conflict resolution | MIS | No sync service
Security                 | PART | JWT + roles; password hashing
Tests                   | PART | 20 tests; 6 failures remain

### Existing test results (before any new changes)
- PASSED: 14 tests (auth basic, languages, conversation start, AYUSH answer submit, security, queue)
- FAILED: 6 tests:
  * `TestConversation::test_conversation_response`
  * `TestConversation::test_extraction`
  * `TestNegation::test_english_negation`
  * `TestRedFlags::test_chest_pain_red_flag`
  * `TestAYUSH::test_ayush_profile_calculation`
  * `TestProvenance::test_voice_provenance`
- Authentication tests (`test_physician_register`, `test_physician_login`) also fail due to missing `physician` table setup or DB initialization differences.

## 2. Errors to Resolve (from previous session context)

The conversation was interrupted after implementing several fixes. The remaining failures must be diagnosed and fixed:

1. `test_conversation_response` — exception inside `process_answer`; likely schema/model mismatch between `dict` returned by engine and `Question` Pydantic model expected by `NextQuestionResponse`.
2. `test_extraction` — same root cause (extraction works but response fails).
3. `test_english_negation` — same endpoint failure prevents verifying negation logic.
4. `test_chest_pain_red_flag` — needs `db.refresh(case)` + nested severity handling (already partially implemented; needs verification after engine fix).
5. `test_ayush_profile_calculation` — `ayush_engine` needs to handle `question_text` in answers and key variants (`answer_text`, `value`). Partial fix applied; verify complete.
6. `test_voice_provenance` — provenance tracking needs correct source; verify after response fix.

## 3. Architecture Principles (preserved)

- Modular backend with `app/services/` per domain.
- Provider abstractions for ASR (SpeechProvider), TTS (TTSProvider), OCR (OCRProvider), ABHA (ABHAProvider), ABDM (ABDMProvider), FHIR (FHIRProvider).
- Mock providers used when live credentials unavailable (explicitly documented).
- No false claims of production government integration.
- Patient isolation enforced (session_id-bound queries + JWT verification).
- Clinical states: positive / negative / unknown / not_provided preserved in JSON fields.

## 4. Implementation Plan (phased, from instruction)

Phase A (audit) — COMPLETED
Phase B (fix existing regressions) — IN PROGRESS (remaining 6 failures)
Phase C (build common AYUSH engine) — NEXT
Phase D (Ayurveda) — NEXT
Phase E (Unani) — NEXT
Phase F (Siddha) — NEXT
Phase G (Yoga/Naturopathy) — NEXT
Phase H (Homoeopathy) — NEXT
Phase I (document upload + OCR verification) — NEXT
Phase J (timeline) — NEXT
Phase K (terminology mapping) — NEXT
Phase L (FHIR/ABDM abstractions) — NEXT
Phase M (offline sync) — NEXT
Phase N (UI upgrade) — NEXT
Phase O (security audit) — NEXT
Phase P (tests) — NEXT
Phase Q (end-to-end) — NEXT

## 5. Key Gaps Not Yet Implemented

- Multi-stream AYUSH questionnaires (only Ayurveda exists in `ayush_engine.py`).
- Unani / Siddha / Yoga-Naturopathy / Homoeopathy engines and schemas.
- Doctor verification gate for OCR (`ocr/` has extraction but no `verify/approval` endpoint or UI).
- Medical timeline model (`timeline` table / endpoint missing).
- Offline-first local storage / IndexedDB in frontend.
- Terminology / NAMASTE / ICD-11 TM1 mapping fixtures.
- Professional doctor frontend (pages/components empty).
- Patient frontend UI pages/components empty.
- Full multilingual voice+touch integration (backend providers exist; frontend missing).
- Handwriting-specific OCR provider (only generic `ocr_provider` exists).

## 6. Next Actions

1. Fix remaining 6 test failures (engine response schema, extraction, negation, red flags, AYUSH calculation, provenance).
2. Build common AYUSH adaptive engine (`app/services/ayush/common/`).
3. Implement Ayurveda, Unani, Siddha, Yoga/Naturopathy, Homoeopathy questionnaires.
4. Add OCR doctor verification workflow (endpoint + schema + basic UI placeholder).
5. Add timeline model + endpoint.
6. Document mock/sandbox behavior clearly; update `.env.example` with provider flags.
7. Do NOT claim live ABDM/ABHA/NAMASTE/ICD-11 production sync.
8. Preserve all existing passing functionality (14 tests) while extending.
