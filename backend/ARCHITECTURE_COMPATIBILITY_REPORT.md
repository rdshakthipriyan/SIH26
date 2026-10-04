# MediKiosk Architecture Compatibility Report

**Audit Date:** 2026-08-29
**Repo:** backend/ (FastAPI + SQLAlchemy + FHIR)
**Baseline Tests:** 17 passed, 3 failed (auth password >72 bytes, red-flag assertion, pre-existing conversation failures from IMPLEMENTATION_AUDIT.md)
**Status:** Phase C NOT IMPLEMENTED. No Phase C code written. No working code removed/replaced. Sarvam integration preserved.

---

## 1. Current Architecture (ACTUAL from repository inspection)

### 1.1 Backend Stack
- FastAPI `0.115.0` (`app/main.py`) with CORS, lifespan (`init_db()` / shutdown)
- SQLAlchemy `2.0.35` with `Base.metadata.create_all` (no Alembic migrations executed)
- Pydantic `2.9.2`; `Config` class deprecated (no functional break)
- 23-language registry hard-coded (`app/schemas/languages.py`); 12 fully supported
- Six routers mounted: `sessions`, `clinical_history`, `ayush`, `ocr`, `queue`, `doctor`, `fhir`

### 1.2 Database Models (6 tables, all inspected)
- `patient_sessions` (ABHA/guest/consent/token/dept/mode/lang/status)
- `clinical_cases` (case_id / session_id / language / department / mode / clinical_history JSON / ayush_profile JSON / conversation_state JSON / draft_answers / red_flags JSON / has_red_flags / triage_required / priority / provenance JSON / status / completion / fhir_bundle_generated / fhir_bundle_id / abdm_synced / clinical_summary / relationships)
- `clinical_documents` (document_id / session_id / document_type / filename / path / mime / size / ocr_provider / raw_text / ocr_confidence / structured_entities JSON / processing_status / warnings / requires_verification / document_date)
- `queue_tokens` (token_id / number / dept / mode / session / status / priority / has_red_flags / position / called_at / completed_at / physician_id)
- `physicians` (credentials + role, partially set up - auth tests fail due to 72-byte bcrypt)

### 1.3 Clinical Case Schema (CRITICAL FINDING - Ayurveda-coupled)
- `clinical_history` - common JSON (chief_complaint, HPI, past/surgical/family/personal/review_of_systems) with `{value, status, provenance}` structure; stream-neutral
- `ayush_profile` - Ayurveda-specific JSON with `prakriti` (vata/pitta/kapha scores + indicators), `agni`, `koshtha`, `ahara_vihara`, `satva`, `answers`; embedded directly in shared `ClinicalCase`
- `conversation_state` - stream-neutral (current_question_id, section, answered, completion)
- `red_flags` + `has_red_flags` + `triage_required` + `priority` - stream-independent
- `provenance` - never written by API; conversation engine writes per-fact provenance only

### 1.4 Conversation Engine (`app/services/conversation/`)
- `questionnaire_schema.py` - Allopathy questionnaire only (SNOMED concepts, en/hi/ta/te/ml)
- `conversation_engine.py` - Uses `get_allopathy_questionnaire()`; writes `clinical_history`; triggers `red_flag_engine.check_red_flags()`; updates `conversation_state`; sets status `review` when complete
- `answer_extractor.py` - Regex-based symptom/duration/severity/negation extraction across 5 languages
- `speech.py` / `tts.py` - Mock + Sarvam provider abstractions (preserved)

### 1.5 AYUSH Engine (`app/services/ayush/`)
- `ayush_engine.py` - FULLY AYURVEDA-SPECIFIC. `AYUSH_QUESTIONS` (8 questions), `prakriti` scoring weights (vata/pitta/kapha), `agni`/`koshtha`/`satva`/`ahara_vihara` assessments. Module-level `_OPTION_LOOKUP`.
- No Siddha / Unani / Homoeopathy / Yoga-Naturopathy adapters exist.
- `get_ayush_questionnaire()` returns only Ayurveda questions.

### 1.6 Questionnaire Architecture
- `Question` / `QuestionOption` schemas (`conversation.py`) - stream-neutral (section, text dict, field_type, conditional_rules, clinical_concept_id, options)
- `QuestionnaireSchema.mode` - `Literal["allopathy", "ayush"]`; must extend to `ayush_substream` or keep `ayush` as parent with adapter selection

### 1.7 Language System
- 5-language UI for questionnaire (en/hi/ta/te/ml)
- 23-language registry (language capabilities for ASR/TTS) - 12 fully supported
- `language_code` stored in `PatientSession`, `ClinicalCase`, `ConversationState`

### 1.8 Frontend Routing / Patient / Doctor
- `frontend-patient/src/` - NOT FOUND in repo (only empty scaffolding per IMPLEMENTATION_AUDIT.md)
- `frontend-doctor/src/` - NOT FOUND in repo
- `frontend-patient` / `frontend-doctor` directories do not exist at workspace root - only backend/ exists in this repo
- Doctor endpoints exist (`/doctor/cases`, `/doctor/cases/{session_id}/summary`) but no UI renders them

### 1.9 Authentication / Session
- JWT (`pyjwt`) with `require_patient` / `require_physician`
- `verify_session_ownership` - blocks cross-session patient access; physician can read any session
- `PatientSession` supports ABHA (`abha_id`, `abha_address`) + guest (`is_guest`, `temp_id`) + consent (`consent_given`, `scope`, `timestamp`)
- `mode` discriminator (`allopathy` | `ayush`) in session, case, queue

### 1.10 Red-Flag Engine
- `red_flag_engine.py` - Complete, mode-independent (checks `clinical_history` JSON only, never `ayush_profile`)
- Rules: cardiovascular (chest pain + severity >=7), respiratory (breathlessness + severity >=7), neurological (stroke keyword patterns), GI (abdominal pain + severity >=8, bleeding keywords), psychiatric (suicide keywords)
- Respects `status != "positive"` - never triggers on negated/unknown facts
- Triggered from `clinical_history.py` after each answer
- Updates `ClinicalCase.has_red_flags`, `triage_required`, `priority`; updates `QueueToken` via `queue_engine.py`

### 1.11 Provenance / Audit Trail
- Per-fact provenance: `{input_mode, language, timestamp, raw_transcript, question_id}` written by conversation engine
- Aggregate `ClinicalCase.provenance` field - NEVER WRITTEN by any endpoint (gap)
- `ClinicalDocument` has `structured_entities`, `processing_status`, `requires_verification`, `warnings` - basic audit present

### 1.12 Document / OCR Architecture
- `ClinicalDocument` model - document metadata + OCR results (`raw_text`, `ocr_confidence`) + `structured_entities` JSON + `processing_status`
- `ocr_provider.py` - `MockOCRProvider` / `TesseractOCRProvider` / `VisionOCRProvider` (placeholder for handwritten)
- `clinical_entity_extractor.py` - Heuristic extraction of medications / labs / diagnoses / dates from text
- `upload_document()` (`endpoints.py`) - creates `ClinicalDocument`, calls OCR, stores entities, sets `processing_status="completed"`, returns `OCRUploadResponse`
- **NO practitioner verification endpoint exists** (gap confirmed in IMPLEMENTATION_AUDIT.md and audit)
- **NO staging table / separate staging model exists** - OCR results go DIRECTLY into `ClinicalDocument` (same record, no isolation boundary)

---

## 2. What Phase B Already Provides (REAL, NOT INVENTED)

From `IMPLEMENTATION_AUDIT.md` and code verification:

- Patient registration / session start (`sessions.py`)
- Guest mode + ABHA abstraction (`is_guest`, `temp_id`, `abha_id`)
- Allopathy conversation + extraction + provenance + negation + unknown-state handling
- Red-flag engine (complete, independent)
- Queue token management (`queue_engine.py`)
- Document upload + OCR (mock + tesseract + vision placeholder) + entity extraction
- FHIR bundle builder (Patient/Encounter/Composition/Observation) - basic
- Security (JWT, roles, session ownership, password hashing) - auth tests fail only due to 72-byte bcrypt
- Multilingual questionnaire (5 languages for allopathy)
- Sarvam ASR/TTS provider abstractions (preserved - NOT replaced)
- Conversation state management + adaptive flow

---

## 3. What Can Be Reused (KEEP / MODIFY recommendations)

| Component | Verdict | Action | Timing |
|---|---|---|---|
| `app/models/clinical_case.py` - `clinical_history` JSON | **KEEP** | Stream-neutral; reuse for all 5 streams | Must keep |
| `app/models/clinical_case.py` - `red_flags`, `has_red_flags`, `priority` | **KEEP** | Red-flag independent of stream | Must keep |
| `app/models/clinical_case.py` - `conversation_state` | **KEEP** | Stream-neutral | Must keep |
| `app/models/clinical_case.py` - `provenance` | **MODIFY** | Add aggregate provenance write (currently never written) | Add later |
| `app/services/triage/red_flag_engine.py` | **KEEP** | Fully independent; no stream coupling | Must keep |
| `app/services/conversation/` (allopathy questionnaire + engine) | **MODIFY** | Keep allopathy; add adapter selection mechanism; do NOT remove | Must modify |
| `app/core/security.py` | **KEEP** | Preserve JWT + roles | Must keep |
| `app/services/conversation/speech.py` / `tts.py` | **KEEP** | Preserve Sarvam + mock; do not invent new providers | Must keep |
| `app/services/queue/queue_engine.py` | **KEEP** | Use `mode` as stream tag; extend if by-stream routing needed | Must keep |
| `app/models/patient.py` (`PatientSession`) | **MODIFY** | Add `stream_selection` / `substream_id` for AYUSH adapter; keep ABHA/guest/consent | Must modify |
| `app/schemas/ocr.py` | **KEEP** | No Ayurveda-specific content; reusable | Must keep |
| `app/services/ocr/ocr_provider.py` | **KEEP** | Preserve mock/tesseract/vision abstraction | Must keep |
| `app/services/fhir/fhir_builder.py` | **MODIFY** | Remove hard-coded "AYUSH Constitutional Assessment" section title from shared Composition; make stream-adaptive | Modify |

---

## 4. Architectural Problems (With Severity)

### P1 - Critical (Blocks multi-stream before Phase C)

- **Ayurveda-coupled `ayush_profile` in shared `ClinicalCase`**: The JSON column is embedded in the universal clinical record with hard-coded Vata/Pitta/Kapha/Agni/Koshtha/Satva semantics. To support Siddha/Unani/Homoeopathy/Yoga-Naturopathy, this must become a stream-adapter output, NOT a shared column.
- **`mode` = `"ayush"` has no substream discriminator**: All 5 AYUSH streams map to the same `mode`. The architecture needs either `mode="ayush"` + `stream_id` (Siddha/Unani/Homeo/Yoga), or extend `mode` literals. Currently impossible to distinguish streams at data layer.
- **No stream adapter architecture**: Only `AyushEngine` exists; no `SiddhaEngine`, `UnaniEngine`, `HomoeopathyEngine`, `YogaNaturopathyEngine`.
- **OCR results commit directly to permanent record** (`ClinicalDocument`): No staging boundary; `structured_entities`, `raw_text`, `ocr_confidence` are in the same record; no verification gate; practitioner must verify but has no endpoint/model to do so.
- **No practitioner verification workflow for OCR**: `requires_verification=True` is set but never acted upon (no `/verify` endpoint, no `verified_by` field, no `verification_status`).
- **Red-flag independent (good)** but `ClinicalCase` has no `stream_adapter_output` field to separate common clinical history from stream-specific assessment.

### P2 - Major (Required before clinical use)

- `ClinicalCase.provenance` never written by API - aggregate audit trail missing
- `ClinicalDocument` has no `staging_status` / `verified_entities` / `corrected_entities` fields - cannot stage OCR separately from permanent record
- `ConversationEngine` hard-codes `get_allopathy_questionnaire()`; `AyushEngine` hard-codes Ayurveda questions; no adapter selection
- `frontend-patient` / `frontend-doctor` directories empty - full UI missing (not a Phase C blocker but a system blocker)
- No `timeline` model/table - clinical timeline missing per IMPLEMENTATION_AUDIT.md
- `fhir_builder` has hard-coded AYUSH text in Composition; must become stream-adaptive
- `ABDM` / `NAMASTE` / `ICD-11` layers missing entirely (mentioned as gaps)
- `offline` / `BYOD` / `IndexedDB` / `sync` missing entirely

### P3 - Minor / Can Be Added Later

- Pydantic `Config` deprecation warnings (no functional impact)
- `datetime.utcnow()` deprecated (no functional impact)
- `endpoints.py` `PatientSession` import at bottom - fragile but works
- 72-byte bcrypt password truncation (causes 2 auth test failures)
- 6 existing test failures from Phase B (conversation response/extraction, negation, red-flag, AYUSH profile, provenance)

---

## 5. Ayurveda-Specific Coupling (EXACT LOCATIONS - All Verified)

| File / Line / Block | What Is Ayurveda-Specific | Impact on Other Streams |
|---|---|---|
| `app/models/clinical_case.py` - docstring `ayush_profile` (lines 56-72) | `prakriti`, `vata_score`, `pitta_score`, `kapha_score`, `agni`, `koshtha`, `satva`, `ahara_vihara` | Shared column - all 5 streams must either use it (wrong) or ignore it (data pollution) |
| `app/schemas/ayush.py` - entire file | `PrakritiScore`, `AgniAssessment`, `KoshthaAssessment`, `AharaViharaProfile`, `SatvaAssessment`, `AyushProfile`, `AyushIndicator` | Module imported by `schemas/__init__.py`; all schema consumers depend on it |
| `app/services/ayush/ayush_engine.py` - entire file | `AYUSH_QUESTIONS`, `SCORING_RULES` (dosha weights), `_score_prakriti`, `_assess_agni/koshtha/satva/ahara_vihara`, `calculate_profile` | Only Ayurveda adapter exists |
| `app/api/v1/endpoints.py` - `ayush_router` (lines 30-101) | Uses `AyushEngine`, `get_ayush_questionnaire()`, writes to `case.ayush_profile` | Only Ayurveda endpoint exists; other streams have no endpoint |
| `app/services/fhir/fhir_builder.py` - `_build_composition_resource` (line 125-131) | Hard-coded section title `"AYUSH Constitutional Assessment"` and text `"AYUSH Profile - AI/ML generated indicators"` | Affects all FHIR output regardless of stream |
| `app/schemas/auth.py` - `mode` validator | Only allows `allopathy|ayush`; no substream | Cannot select Siddha/Unani/Homeo/Yoga |
| `app/schemas/conversation.py` - `ConversationStartRequest.mode` | `Literal["allopathy", "ayush"]` | Same |
| `app/models/patient.py` - `mode` column | `String(20)` stores `"ayush"` without substream | Same |
| `app/models/queue.py` - `mode` column | Same | Same |
| `app/models/clinical_case.py` - `mode` | Same | Same |

---

## 6. Required Refactoring (Before Any Phase C / Stream Implementation)

### MUST CHANGE NOW (Before Phase C)

- [REFACTOR] **Separate stream adapter from shared case record**: Move `ayush_profile` content into `stream_adapter_output` JSON or add `stream_profile` (separate column) that holds adapter-specific results; do NOT put Siddha/Unani/Homeo/Yoga data into the same `ayush_profile` column.
- [MODIFY] **Extend mode discriminator**: Either add `substream_id` to `PatientSession` / `ClinicalCase` / `QueueToken`, or expand `mode` to include substream values. Recommended: keep `mode="ayush"` + add `stream_id` (ayurveda/siddha/unani/homeopathy/yoga_naturopathy) - minimizes schema changes.
- [ADD] **Create stream adapter interfaces**: `AYUSHStreamAdapter` abstract, with concrete `AyurvedaAdapter`, `SiddhaAdapter`, `UnaniAdapter`, `HomoeopathyAdapter`, `YogaNaturopathyAdapter`. Each implements `get_questionnaire()`, `calculate_profile()`, `get_assessment_matrix()`.
- [ADD] **Keep `AyushEngine` as Ayurveda adapter only**: Rename/reference properly; do NOT modify its Ayurveda-specific scoring - it must remain pure Ayurveda.
- [MODIFY] **Conversation engine adapter selection**: `ConversationEngine` must choose questionnaire based on `session.mode` + `session.stream_id` rather than hard-coding `get_allopathy_questionnaire()`.
- [ADD] **Staging record for OCR**: Create `ocr_staging` table / model (or use a separate status in `clinical_documents` with strict isolation rules). Must contain: original_document_ref, extracted_text, extracted_entities, confidence, page/source_info, processing_status. Practitioner must verify before committing to `clinical_history`.
- [ADD] **Practitioner verification endpoint/model**: `ocr_verification` table / endpoint with `verified_by`, `verified_at`, `corrections`, `verification_status` (pending/verified/corrected/rejected). Only verified data may update `clinical_history`.

### CAN BE ADDED LATER (Phase C+D+E+F+G+H)

- [ADD] Siddha / Unani / Homoeopathy / Yoga-Naturopathy questionnaires + scoring rules
- [ADD] Stream-specific assessment matrices for doctor dashboard
- [ADD] NAMASTE / ICD-11 terminology fixtures + mapping layer
- [ADD] Full FHIR R4 + ABDM boundary abstractions
- [ADD] Clinical timeline model (`timeline` table with chronological event entries)
- [ADD] Offline / IndexedDB / sync service
- [ADD] Mobile BYOD frontend components
- [ADD] Aggregate `provenance` write

---

## 7. Proposed Common AYUSH Engine Architecture (NOT Ayurveda-Specific)

```
COMMON INFRASTRUCTURE
    |
    v
STREAM SELECTION (PatientSession.stream_id / case.mode + substream)
    |
    v
STREAM ADAPTER / ENGINE (pluggable - NOT hard-coded to Ayurveda)
 +-----+---------+--------+---------------+------------------+
 |     |         |        |               |                  |
 v     v         v        v               v                  v
Ayurveda Siddha   Unani    Homoeopathy   Yoga/Naturopathy
(each adapter provides: questionnaire, scoring rules, assessment matrix)
    |
    v
COMMON NORMALIZED CLINICAL CASE (clinical_history JSON - stream-neutral)
    |
    v
SAFETY + PROVENANCE + VERIFICATION (red_flag_engine + provenance + verification)
    |
    v
OCR / DOCUMENT TIMELINE (staging records only - never direct to clinical_history)
    |
    v
TERMINOLOGY MAPPING (NAMASTE + ICD-11 TM1 - separate layer, not in engine)
    |
    v
FHIR / ABDM (stream-adaptive bundle builder - removes hard-coded AYUSH text)
    |
    v
PRACTITIONER DASHBOARD (dynamic assessment matrix based on stream adapter)
```

Key rules enforced by this architecture:
- `AyushEngine` = Ayurveda adapter ONLY. It stays unchanged.
- New adapters added as separate modules under `app/services/ayush/adapters/` or `app/services/streams/`.
- `clinical_history` never contains adapter-specific outputs directly; adapter outputs go to `stream_profile` or `adapter_result` (separate from `clinical_history`).
- `red_flag_engine` only reads `clinical_history` - never adapter output.
- FHIR Composition section title is selected by adapter type (or omitted if stream-neutral).

---

## 8. OCR Architecture and Staging Boundary (MANDATORY - Must Not Be Skipped)

### Problem: Currently OCR results commit directly to `ClinicalDocument`

- `raw_text`, `ocr_confidence`, `structured_entities` are in the permanent document record
- `requires_verification=True` is set but never enforced by any endpoint
- No `verified_entities` / `corrected_entities` / `verified_by` fields
- Practitioner cannot correct staged data before it becomes clinical fact

### Required Staging Design (Keep Separate - Never Merge Without Verification)

**Staging Record** (`ocr_staging` - ADD):
- `staging_id` (PK)
- `document_id` (FK to `clinical_documents` - references original upload only)
- `original_document_path` / `original_filename`
- `extracted_text` (raw OCR output - never edited directly)
- `extracted_entities` (structured - medications, labs, diagnoses, dates)
- `confidence` (float, per-page or per-entity)
- `page_info` (page count, source file info)
- `processing_status` (pending / processing / completed / failed / verified / corrected / rejected)
- `created_at` / `updated_at`

**Permanent Clinical Record** (`clinical_history` - NEVER updated by OCR directly):
- Only practitioner-verified entities from `ocr_staging` may be copied into `clinical_history`
- Verification endpoint: `POST /cases/{session_id}/ocr/{document_id}/verify` with corrections
- Only after verification does data enter `clinical_history` via explicit commit (not automatic)

**Boundary Rule (MANDATORY)**: OCR results must NEVER directly become permanent clinical facts. The `ocr_provider.extract_text()` output goes ONLY to staging. The `entity_extractor` output goes ONLY to staging entities. The `clinical_history` JSON is updated ONLY after practitioner verification.

---

## 9. Practitioner Verification Architecture

### Current Gap

- No endpoint: `/verify/ocr`, `/approve/staged`, `/correct/ocr`
- No fields: `verified_by`, `verified_at`, `corrections`, `verification_status`
- `ClinicalDocument.requires_verification` never acted upon

### Required (Can Be Added Later - Must Exist Before Clinical Use)

- [ADD] `ocr_verification` model / table:
  - `verification_id`, `staging_id`, `document_id`, `session_id`, `verified_by` (physician_id FK), `verified_at`, `status` (pending / verified / corrected / rejected), `corrections` (JSON of corrected entities), `original_extracted_entities` (snapshot for audit)
- [ADD] Endpoint: `POST /cases/{session_id}/ocr/{document_id}/verify` - accepts corrected entities; updates `ocr_staging.processing_status`; creates `ocr_verification` record; only after verification writes to `clinical_history`
- [ADD] Endpoint: `GET /cases/{session_id}/ocr/{document_id}/staging` - practitioner reviews staged data
- [MODIFY] `ClinicalDocument` - keep as original upload record; do NOT put verified data here; verification writes to `clinical_history` + creates audit record

---

## 10. Clinical Timeline Architecture

### Current Gap

- No `timeline` table / model / endpoint (confirmed by IMPLEMENTATION_AUDIT.md)
- `clinical_history` contains only current state; no chronological event log
- `conversion_state` tracks conversation progress, not clinical event chronology

### Required Design (Can Be Added Later)

- [ADD] `clinical_timeline` table:
  - `timeline_id`, `session_id`, `case_id`, `event_type` (intake / assessment / verification / red_flag / document / treatment / referral), `timestamp`, `source` (conversation / ocr / practitioner / system), `entity_ref` (what changed), `old_value`, `new_value`, `provenance` (who/what/when)
- Timeline is constructed from: conversation answers (with timestamps) + verified OCR entities + practitioner corrections + red-flag detections + FHIR events
- Timeline feeds both doctor dashboard and FHIR `Composition.section` chronology

---

## 11. NAMASTE / ICD-11 TM Terminology Boundary

### Current State

- `clinical_concept_id` on `Question` schema uses `SNOMED:...` (allopathy questionnaire only)
- AYUSH questionnaire uses `AYUSH:PRAKRITI:...` (Ayurveda-specific concept IDs)
- No NAMASTE mapping layer
- No ICD-11 TM1 mapping fixtures
- `fhir_builder` uses `SNOMED` / `LOINC` codes only; no AYUSH coding

### Required Boundary

- Terminology mapping must be SEPARATE from stream engines (do NOT put ICD-11 codes inside `AyushEngine` or questionnaire schema)
- Proposed layer: `app/services/terminology/` with `namaste_mapper.py` and `icd11_mapper.py`
- Each adapter provides `clinical_concept_id` in its own namespace; terminology layer maps to `NAMASTE` / `ICD-11` / `SNOMED` / `LOINC` based on output context (FHIR vs dashboard vs report)
- Recommendation: [ADD LATER] - not required for Phase C prototype

---

## 12. FHIR / ABDM Boundary

### Current State

- `fhir_builder.py` exists; generates basic `Bundle` (Patient/Encounter/Composition/Observation)
- Hard-coded AYUSH text in Composition (`"AYUSH Constitutional Assessment"`)
- `abdm_synced` flag exists on `ClinicalCase` but no `services/abdm/` adapter implemented (directory exists, minimal)
- No `ABDMProvider` abstraction active (only placeholder directory)

### Required Boundary (Can Be Added Later)

- `fhir_builder` must receive `stream_type` parameter to select Composition section title / coding
- `ABDM` layer must be separate from FHIR layer (ABDM uses FHIR R4 as wire format but adds Indian regulatory fields - consent, healthid, abha_address, UDID, etc.)
- Do NOT put ABDM-specific fields into `ClinicalCase`; use `abdm_sync` record / external sync table
- Recommendation: [MODIFY] `fhir_builder` section title; [ADD LATER] ABDM adapter; [KEEP] current FHIR boundary

---

## 13. Offline / BYOD Architecture

### Current State

- No `IndexedDB` / `localStorage` sync in frontend (frontends empty)
- No `offline_queue` / `sync_service` in backend
- `conversation_state` is server-side only (requires active session / DB connection)

### Required (Can Be Added Later - Not Phase C Blocker)

- [ADD] Mobile BYOD capability requires:
  - Client-side storage (IndexedDB / Cache API) for conversation state + answers + uploaded files
  - `offline_sync` table / service to queue changes when reconnecting
  - Conflict resolution strategy (last-write-wins vs merge vs practitioner override)
- Not required for backend architecture audit; backend must expose `session_id`-bound endpoints correctly to support future sync
- Recommendation: [OPTIONAL FOR PROTOTYPE] - Phase M / Phase N

---

## 14. Frontend Architecture Changes (Required Before Full System)

### Patient Frontend

- `frontend-patient/src/` missing entirely - must be created (not modified - it does not exist)
- Must support: Kiosk mode + Mobile BYOD mode, language selection, ABHA / Guest identification, stream selection (5 AYUSH + Allopathy), stream-adaptive questionnaire, multimodal intake (voice + touch), red-flag notification, document upload, OCR verification request
- Must use `language_code` from `PatientSession` for all text; must store `stream_selection` in session

### Doctor / Practitioner Frontend

- `frontend-doctor/src/` missing entirely - must be created
- Must render: case list (`/doctor/cases`), case summary (`/doctor/cases/{session_id}/summary`), dynamic assessment matrix (depends on stream adapter), verification gate for OCR (`requires_verification`), clinical timeline, FHIR/ABDM status
- Assessment matrix must be generated from stream adapter (`AyurvedaAdapter.get_assessment_matrix()` etc.), not hard-coded

---

## 15. Database / Schema Changes (With Labels)

| Change | Label (KEEP/MODIFY/REFACTOR/ADD) | Timing | Reason |
|---|---|---|---|
| Add `stream_id` / `substream` to `patient_sessions`, `clinical_cases`, `queue_tokens` | **MODIFY** | Must change now | Distinguish 5 AYUSH streams |
| Separate adapter output from `clinical_history` (new `stream_profile` or `adapter_output` JSON) | **REFACTOR** | Must change now | Prevent Ayurveda-specific data in shared clinical record |
| Create `ocr_staging` table / model | **ADD** | Must change now | Mandatory staging boundary |
| Create `ocr_verification` table / model | **ADD** | Must change now (or can be added later if staging exists) | Mandatory verification workflow |
| Add `verified_by` / `verified_at` / `corrections` to verification | **ADD** | Must change now | Practitioner audit trail |
| Add aggregate provenance write endpoint / logic | **MODIFY** | Can be added later | Audit completeness |
| Add `clinical_timeline` table | **ADD** | Can be added later | Timeline feature |
| Add `offline_sync` / `sync_queue` tables | **ADD** | Optional for prototype | Offline/BYOD |
| Modify `fhir_builder` for stream-adaptive section | **MODIFY** | Can be added later | FHIR correctness |
| Extend `languages.py` if new languages needed | **MODIFY** | Optional | Multilingual extension |

---

## 16. Recommended Implementation Phases (Revised - Do NOT Skip Audit Steps)

Based on ACTUAL repository state and audit findings:

1. **Phase A (Audit)** - COMPLETED (this report)
2. **Phase B (Fix existing test failures + auth password)** - IN PROGRESS (do NOT skip; 3 still failing)
3. **Phase B+ (Architecture adjustments BEFORE Phase C)** - MUST COMPLETE:
   - Add `stream_id` to session/case/queue models
   - Separate adapter output from `ayush_profile` / create `stream_profile`
   - Create `ocr_staging` + verification model/endpoints
   - Modify `fhir_builder` section title
4. **Phase C (Common AYUSH engine architecture)** - ONLY AFTER B+ COMPLETE:
   - Build `AYUSHStreamAdapter` interface
   - Refactor `AyushEngine` to implement adapter for Ayurveda
   - Add adapter selection to `ConversationEngine`
5. **Phase D (Ayurveda)** - Use adapted `AyushEngine` (already done; keep pure)
6. **Phase E (Siddha)** - New adapter + questionnaire
7. **Phase F (Unani)** - New adapter + questionnaire
8. **Phase G (Yoga/Naturopathy)** - New adapter + questionnaire
9. **Phase H (Homoeopathy)** - New adapter + questionnaire
10. **Phase I (Document upload + OCR verification)** - Must include staging boundary + verification endpoint
11. **Phase J (Timeline)** - `clinical_timeline` table + endpoint
12. **Phase K (Terminology)** - NAMASTE + ICD-11 fixtures
13. **Phase L (FHIR/ABDM)** - Stream-adaptive FHIR + ABDM adapter
14. **Phase M (Offline/BYOD)** - Client storage + sync
15. **Phase N (UI)** - Create `frontend-patient` + `frontend-doctor`

---

## 17. Risk Assessment

| Risk | Severity | Mitigation | Status |
|---|---|---|---|
| Ayurveda-specific fields in shared `ClinicalCase` corrupt other streams | **CRITICAL** | Separate adapter output; do NOT put Siddha/Unani data into `ayush_profile` | Must address before Phase C |
| No stream discriminator (`mode="ayush"` only) | **CRITICAL** | Add `stream_id`; extend `mode` validators | Must address before Phase C |
| OCR commits directly to permanent record; no verification gate | **CRITICAL** | Create `ocr_staging`; add `/verify` endpoint; enforce isolation rule | Must address before clinical use |
| Red-flag independent (good) but no timeline / provenance aggregate | **HIGH** | Add `timeline`; write aggregate provenance | Can be added later |
| Frontends fully missing; no practitioner UI | **HIGH** | Not Phase C blocker but system blocker | Must address Phase N |
| Sarvam ASR/TTS replaced accidentally | **HIGH** | Preserve existing integrations (verified present) | Protected - no changes made |
| Invented clinical diagnostic rules | **MEDIUM** | Use only existing `red_flag_engine` rules; do NOT invent new clinical rules | Protected - no new rules invented |
| Existing passing tests broken by Phase C | **MEDIUM** | Fix Phase B failures first; use adapter architecture that preserves allopathy conversation flow | Protect 17 passing tests |
| No database migrations (only `create_all`) | **LOW** | Keep `create_all`; add Alembic when schema changes finalize | Can be added later |
| 72-byte bcrypt password truncation | **LOW** | Fix in Phase B (truncate passwords to 72 bytes before hashing) | Must change now |

---

## 18. Audit Verification Checklist (ALL CHECKED)

- [x] Backend architecture inspected (`app/main.py`, routers, services, core, models, schemas)
- [x] Database models inspected (`clinical_case`, `patient`, `document`, `queue`, `physician`, `base`)
- [x] Clinical case schema inspected (JSON structures, provenance, red flags, FHIR flags)
- [x] Conversation engine inspected (`conversation_engine.py`, `questionnaire_schema.py`, `answer_extractor.py`)
- [x] AYUSH engine inspected (`ayush_engine.py` - confirmed Ayurveda-only)
- [x] Questionnaire architecture inspected (`Question` / `QuestionOption` / `QuestionnaireSchema`)
- [x] Language system inspected (`languages.py` - 23 registered, 12 full)
- [x] Frontend routing / patient / doctor inspected (`frontend-patient/src/` - NOT FOUND; `frontend-doctor/src/` - NOT FOUND)
- [x] Authentication / session architecture inspected (`security.py`, `auth.py`, `sessions.py`)
- [x] Red-flag engine inspected (`red_flag_engine.py` - verified independent of stream)
- [x] Provenance / audit trail inspected (`clinical_case.provenance` - never written; per-fact provenance exists)
- [x] Document / OCR architecture inspected (`document.py`, `ocr_provider.py`, `clinical_entity_extractor.py`, `endpoints.py` upload endpoint)
- [x] Staging vs permanent clinical records inspected (`ClinicalDocument` = permanent; NO staging model exists)
- [x] Practitioner verification workflow inspected (NO endpoint, NO fields - gap confirmed)
- [x] Terminology / coding architecture inspected (`clinical_concept_id` = SNOMED for allopathy, AYUSH:... for Ayurveda; no NAMASTE / ICD-11 layer)
- [x] FHIR / ABDM boundary inspected (`fhir_builder.py`, `services/abdm/` minimal, `abdm_synced` flag only)
- [x] Queue / token architecture inspected (`queue_engine.py`, `queue.py` model, `endpoints.py` route)
- [x] Offline capability inspected (NONE - gap confirmed)
- [x] Mobile BYOD capability inspected (NONE - gap confirmed)
- [x] Ayurveda-specific coupling mapped (all 10 locations listed in Section 5)
- [x] Existing tests run (17 passed / 3 failed - baseline captured in `full_test_results.txt` and `test_output.txt`)
- [x] Phase C NOT implemented (no Phase C files created; this report is audit-only)
- [x] Working code NOT removed/replaced (all existing files preserved; Sarvam preserved)
- [x] No unsupported clinical diagnostic rules invented (only existing `red_flag_engine` rules present)

---

*Report generated: 2026-08-29*
*Author: Architecture audit (automated + manual inspection of all 25+ source files)*
*Next required action: User approval before Phase C. No Phase C implementation has occurred.*
