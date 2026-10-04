# AUDIT_STATUS.md — MediKiosk Repository Audit

## Existing Working Components
- Backend FastAPI app with 50+ API endpoints
- SQLAlchemy models (PatientSession, ClinicalCase, QueueToken, Document, Physician)
- Pydantic schemas (languages 23, clinical_history, fhir, ocr, conversation)
- Database (SQLite + Alembic)
- Conversation engine + answer extractor + red flag engine
- Speech (mock + Sarvam interface) / TTS (mock + Sarvam interface)
- OCR provider abstraction (Mock / Tesseract / Vision)
- Clinical entity extractor
- FHIR builder (Bundle with Patient/Encounter/Observation/Composition)
- Queue engine (token creation, status, priority)
- AYUSH engine (profile scoring, 8 questions)
- JWT auth with role-based access
- Provider abstractions for all external services
- Backend tests (pytest suite exists)

## Existing Incomplete Components
- Patient frontend: React scaffold exists but UI screens need implementation (language, intake, document upload, review, token, complete flows partially scaffolded)
- Doctor frontend: React scaffold exists but dashboard/summary/OCR verification/case detail screens need real data binding
- Some pages have routes but may lack full backend integration (e.g., OCR verification page)
- No live Sarvam / Vision / ABDM integration configured (mock providers active)

## Missing / Broken Components
- Full end-to-end patient flow from welcome → language → identify → stream → adaptive intake → red flag → token → upload → OCR staging → doctor verification
- Some frontend pages need working API connections (conversation respond, voice transcribe, document upload, OCR staging, doctor case list, FHIR download)
- Language selection UI needs actual translation display and TTS invocation
- Microphone / voice transcript flow needs real display and clinical extraction
- Red flag display needs clear emergency state in UI
- Document upload needs multi-file + multi-page + staging status display
- Doctor verification gate needs actual edit/accept/reject + commit
- FHIR generation endpoint may need fixing / verification
- Accessibility: large buttons, persistent Listen, touch alternatives must be visible
- Mobile/BYOD flow needs basic continuation

## Changes Required (Minimum)
1. Ensure backend routes respond correctly for session, conversation, voice, AYUSH, OCR, queue, doctor, FHIR
2. Fix/complete patient frontend pages (Welcome, Language, Identity, Stream, Intake, Triage, Documents, Upload, Processing, Complete)
3. Fix/complete doctor frontend pages (Login, Dashboard, CaseDetail, Summary, OCR, AYUSH, Provenance, FHIR)
4. Add clear provider labeling (MOCK / SANDBOX / DEMO) in UI
5. Ensure no fake/mock data is presented as real
6. Run tests and fix failures
7. Build both frontends
8. Create E2E_DEMO_REPORT.md + FINAL_SYSTEM_STATUS.md
