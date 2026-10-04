# MediKiosk

### Intelligent Pre-Consultation for Faster, Safer & Inclusive Healthcare

**Smart India Hackathon 2026 · SIH26047 · Patient Case-Taking Software · Team Care Catalysts**

> **Patient speaks/taps → MediKiosk structures the history → Practitioner verifies → Standardized clinical record**

MediKiosk is a multilingual, voice-first patient pre-consultation platform designed to reduce repetitive history-taking, improve accessibility, structure clinical information before consultation, and help practitioners spend more consultation time on clinical decision-making.

The project combines guided **Allopathy and AYUSH intake**, multilingual voice/touch interaction, clinical fact extraction, red-flag triage, document OCR, queue prioritization, practitioner review, provenance tracking, and FHIR-based structured records.

> **“AI prepares the clinical story. The practitioner makes the clinical decision.”**

---

## Problem Statement

Healthcare consultations often begin with the practitioner spending valuable time collecting basic patient history. This creates several practical problems:

- **Long queues** — patients spend time waiting and repeatedly explaining basic information.
- **Short consultation time** — practitioners must manually collect history before focusing on clinical decisions.
- **Language and literacy barriers** — text-heavy digital systems are difficult for many patients.
- **Unstructured records** — prescriptions, reports and handwritten documents are difficult to digitize and reuse reliably.

MediKiosk moves structured case-taking **before the consultation** while keeping the practitioner in control of the clinical decision.

---

## Solution

MediKiosk provides a guided pre-consultation workflow through a kiosk or compatible web/mobile interface.

```text
Patient
   │
   ▼
Language Selection
   │
   ▼
Identity / Consent
   │
   ▼
Allopathy / AYUSH Stream
   │
   ▼
Voice + Touch Guided Intake
   │
   ├────► Clinical Fact Extraction
   │
   ├────► Red-Flag Triage
   │
   ▼
Optional Document Upload
   │
   ▼
OCR + Structured Entity Extraction
   │
   ▼
Practitioner Review
   │
   ▼
Queue / Priority + Structured Clinical Record
   │
   ▼
FHIR Export
```

The core principle is **human-in-the-loop healthcare AI**: automated components prepare and structure information, while the practitioner remains responsible for verification and clinical decisions.

---

## Key Features

### Multilingual Voice + Touch Intake

MediKiosk maintains a registry for **23 supported language options** and provides language-aware intake. Patients can interact using voice or touch/text, reducing dependence on conventional text-heavy forms.

The speech layer uses a provider abstraction with mock and Sarvam-backed implementations, allowing development without depending on a live external service.

### Allopathy Case-Taking

The conversation engine conducts guided clinical history collection using structured questions and conditional flow.

The extraction layer can capture information such as:

- chief complaint
- duration
- severity
- location
- symptom character
- associated information
- negated symptoms
- provenance of captured facts

### Multi-AYUSH Intake

MediKiosk includes stream-specific AYUSH workflows rather than treating AYUSH as a generic questionnaire.

The architecture supports:

- Ayurveda
- Siddha
- Unani
- Homoeopathy
- Yoga & Naturopathy

The AYUSH engine includes structured assessment logic such as Prakriti-oriented scoring and related patient-friendly assessment fields.

### Red-Flag Triage

A rule-based safety layer checks structured history for urgent patterns and can escalate the patient's priority.

Implemented rule categories include:

- severe chest-pain patterns
- acute breathlessness
- stroke-pattern symptoms
- severe abdominal pain
- gastrointestinal bleeding
- suicidal ideation

The engine also incorporates negation handling so statements such as *“I don't have chest pain”* are not treated as positive symptoms.

> Red-flag detection is a prioritization aid, not a diagnosis engine.

### OCR + Clinical Entity Extraction

Patients can upload prescriptions, reports and other supported clinical documents.

The OCR architecture supports:

- mock OCR for development
- Tesseract-based OCR
- a vision-provider path for handwritten-document processing

Extracted text can be processed into structured entities such as medications, laboratory results and diagnoses, together with confidence/warning information.

The intended safety workflow is:

```text
Document → OCR → Structured Extraction → Verification → Clinical Record
```

Uncertain OCR output should remain subject to human verification rather than being treated as authoritative clinical data.

### Practitioner Dashboard

The practitioner side provides access to submitted cases and structured case details, including:

- clinical history
- red flags and priority
- AYUSH profile where applicable
- document/OCR information
- provenance information
- FHIR export

### Queue & Priority Management

MediKiosk creates and manages queue tokens, tracks status transitions and integrates red-flag information into patient priority.

### Provenance Tracking

Clinical facts can retain information about how they were captured—for example voice or touch input—helping the practitioner distinguish structured output from its source.

### FHIR-Based Structured Records

The backend contains a FHIR builder that produces structured bundles using resources such as:

- Patient
- Encounter
- Composition
- Observation
- Provenance-related metadata

This provides a standards-oriented path toward interoperability with digital-health systems.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       PATIENT LAYER                         │
│                                                             │
│   Kiosk / Web Client → Language → Identity → Intake        │
│                            │                                │
│                      Voice / Touch                          │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                         │
│                                                             │
│  Session Management     Conversation Engine                 │
│  Answer Extraction      AYUSH Engine                        │
│  Speech / TTS           Red-Flag Engine                     │
│  OCR Pipeline           Clinical Entity Extraction          │
│  Queue Service          FHIR Builder                        │
│  JWT / Access Control                                       │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
                ▼                              ▼
        ┌───────────────┐              ┌────────────────┐
        │   Database    │              │ External       │
        │ SQLAlchemy /  │              │ Providers      │
        │ SQLite / DB   │              │ Sarvam / OCR   │
        └───────┬───────┘              └────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRACTITIONER LAYER                       │
│                                                             │
│ Case Queue → Case Detail → Verification → FHIR Export      │
└─────────────────────────────────────────────────────────────┘
```

---

## Patient Journey

```text
Start
  ↓
Choose Language
  ↓
Consent / Patient Identity
  ↓
Select Allopathy or AYUSH
  ↓
Guided Questionnaire
  ↓
Voice / Touch Response
  ↓
Transcription (for voice)
  ↓
Structured Fact Extraction
  ↓
Red-Flag Evaluation
  ↓
Continue Adaptive Questions
  ↓
Upload Documents (optional)
  ↓
OCR + Entity Extraction
  ↓
Submit History
  ↓
Queue / Priority
  ↓
Practitioner Reviews Structured Case
```

A typical voice answer is converted into a transcript, passed through the answer extractor, stored as structured clinical information with provenance, evaluated by the red-flag engine, and then used by the conversation engine to determine the next question.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Patient UI | React 18, TypeScript, Vite, Tailwind CSS, Lucide React |
| Practitioner UI | React 18, TypeScript, Vite |
| Backend | Python, FastAPI, Pydantic |
| ORM / Database | SQLAlchemy, SQLite; database configuration supports migration toward production DBs |
| Migrations | Alembic |
| Authentication | JWT, password hashing, role-based access |
| Speech | Provider abstraction, Sarvam integration path |
| TTS | Sarvam Bulbul integration path + fallback |
| OCR | Tesseract, provider-based vision integration |
| Clinical Logic | Conversation engine, answer extractor, AYUSH engine, red-flag rules |
| Interoperability | FHIR R4-style bundle generation |
| Testing | pytest |
| Deployment | Docker Compose support |

---

## Repository Structure

```text
SIH26/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST API routes
│   │   ├── core/                # Configuration, DB and security
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/
│   │   │   ├── conversation/    # Intake, ASR, TTS, extraction
│   │   │   ├── ayush/           # AYUSH assessment logic
│   │   │   ├── ocr/             # OCR + entity extraction
│   │   │   ├── triage/          # Red-flag detection
│   │   │   ├── fhir/            # FHIR bundle generation
│   │   │   └── queue/           # Queue management
│   │   ├── tests/
│   │   └── main.py
│   └── requirements.txt
│
├── frontend-patient/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── services/
│       └── types/
│
├── frontend-doctor/
│   └── src/
│       ├── pages/
│       ├── services/
│       └── types/
│
├── alembic/
├── alembic.ini
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Backend Services

### Conversation Engine
Controls question progression for Allopathy and AYUSH flows and evaluates conditional rules to determine the next question.

### Answer Extractor
Transforms patient responses into structured facts. The static analysis identifies multilingual symptom-pattern handling, severity/duration extraction and negation processing.

### Speech Provider
Abstracts speech-to-text so the application can run against mock services during development or a configured external provider.

### Text-to-Speech Provider
Provides TTS abstraction with a Sarvam Bulbul integration path and graceful fallback behavior.

### AYUSH Engine
Processes AYUSH-specific responses and produces structured assessment information.

### OCR Provider
Provides interchangeable mock, Tesseract and vision-provider OCR paths.

### Clinical Entity Extractor
Extracts structured information such as medications, laboratory results and diagnoses from OCR output.

### Red-Flag Engine
Evaluates six critical rule categories and feeds urgent results into queue priority.

### Queue Service
Handles token creation, status transitions, queue position and priority.

### FHIR Builder
Converts structured case information into an interoperable FHIR-oriented bundle.

---

## API Overview

FastAPI automatically exposes interactive API documentation when the backend is running.

Common API groups include:

```text
/api/v1/sessions/...       Session and practitioner authentication
/api/v1/languages          Supported language registry
/api/v1/questionnaire/...  Questionnaire definitions
/api/v1/cases/...          Conversation and clinical history
/api/v1/queue/...          Queue management
/api/v1/doctor/...         Practitioner case access
```

Backend service endpoints also cover speech, TTS, document processing, AYUSH profiles and FHIR export.

After starting the backend, open:

```text
http://localhost:8000/docs
```

---

## Local Development

### Prerequisites

Install:

- Python 3.x
- Node.js + npm
- Git
- Docker / Docker Compose if using the containerized services
- Tesseract if using the local Tesseract OCR provider

### 1. Clone the repository

```bash
git clone https://github.com/rdshakthipriyan/SIH26.git
cd SIH26
```

### 2. Configure environment variables

Create your local environment file from the template.

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Important configuration areas include:

```env
DATABASE_URL=sqlite:///./medikiosk.db

JWT_SECRET=replace-with-a-secure-random-secret
JWT_ALGORITHM=HS256

SPEECH_PROVIDER=mock
SARVAM_API_KEY=

TTS_PROVIDER=mock

OCR_PROVIDER=mock
VISION_API_KEY=

ABHA_PROVIDER=mock
ABDM_PROVIDER=mock
```

**Never commit real API keys, JWT secrets or production credentials.**

### 3. Start the backend

```bash
cd backend

python -m venv .venv
```

Activate the environment.

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies and start FastAPI:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

### 4. Start the patient frontend

Open another terminal:

```bash
cd frontend-patient
npm install
npm run dev
```

The Vite configuration is designed for local development with the backend API.

### 5. Start the practitioner frontend

Open another terminal:

```bash
cd frontend-doctor
npm install
npm run dev
```

The static analysis identifies the patient and practitioner development servers around ports **5173** and **5174**, respectively.

---

## Testing

Run the backend tests from the backend environment:

```bash
cd backend
pytest
```

The code-analysis report identifies broad backend coverage across critical paths including authentication, extraction, isolation and AYUSH logic.

For frontend verification:

```bash
cd frontend-patient
npm run build
```

and:

```bash
cd frontend-doctor
npm run build
```

---

## Security & Safety Design

MediKiosk includes several application-level safeguards:

- JWT-based authentication
- hashed practitioner passwords
- role-aware access control
- patient/session ownership checks
- server-side API credentials
- consent-aware intake architecture
- provenance tracking
- red-flag escalation
- OCR confidence/warning handling
- practitioner verification before clinical use

This project is a **prototype / decision-support and case-taking system**, not an autonomous diagnostic system. Clinical output must be reviewed by qualified healthcare professionals.

---

## Implementation Status

| Capability | Status |
|---|---|
| Allopathy intake engine | ✅ Implemented |
| AYUSH intake engine | ✅ Implemented |
| 23-language registry | ✅ Implemented |
| Multilingual extraction logic | ✅ Implemented |
| Speech provider architecture | ✅ Implemented |
| Text-to-speech architecture | ✅ Implemented |
| Printed-document OCR pipeline | ✅ Implemented |
| Handwritten OCR | 🟡 Architecture/provider path ready |
| Clinical entity extraction | ✅ Implemented |
| Red-flag rules | ✅ Implemented |
| Negation handling | ✅ Implemented |
| Queue management | ✅ Implemented |
| FHIR bundle generation | ✅ Implemented |
| Provenance tracking | ✅ Implemented |
| Session resume | ✅ Implemented |
| JWT authentication | ✅ Implemented |
| Cross-patient isolation | ✅ Implemented |
| Backend tests | ✅ Present |
| Patient frontend | 🟡 Requires completion/validation |
| Practitioner frontend | 🟡 Requires completion/validation |
| ABHA production integration | 🟡 Mock / architecture ready |
| ABDM production integration | 🟡 Mock / architecture ready |

The distinction above is important: **FHIR generation exists in the application, while live production ABHA/ABDM connectivity is not claimed as complete.**

---

## Current Limitations

MediKiosk is currently a prototype and still requires work before real clinical deployment.

Key limitations include:

- production ABHA/ABDM connectivity is pending
- some external-service flows depend on mock/configurable providers
- handwritten OCR quality requires real-world validation
- regional-language speech recognition requires broader testing
- frontend flows require final implementation/validation
- clinical red-flag and AYUSH logic requires practitioner-led validation
- integration with hospital information systems requires deployment-specific work
- privacy, consent, security and regulatory controls require production hardening

---

## Feasibility & Deployment Path

The project is designed around a web-based, modular architecture so it can be used through kiosk and compatible web/mobile interfaces without requiring a heavy client installation.

The proposed progression is:

```text
Prototype
    ↓
Controlled Pilot
    ↓
Hospital Integration
    ↓
Scaled Deployment
```

Major engineering risks include regional-language speech accuracy, handwritten OCR errors, privacy/consent requirements, incorrect automated interpretation and integration with existing hospital systems.

MediKiosk addresses these at the design level through voice/touch fallback, staged OCR verification, rule-based safety checks, practitioner oversight and FHIR-oriented interoperability.

---

## Expected Impact

### For Patients

- voice-first interaction
- local-language accessibility
- less repetitive history narration
- faster routing
- more inclusive pre-consultation

### For Practitioners

- structured history before consultation
- verified document information
- stream-specific assessment
- visible red-flag information
- more consultation time for clinical decision-making

### For Healthcare Systems

- structured clinical data
- standardized records
- interoperability-oriented output
- reusable digital patient information
- scalable pre-consultation workflow

> **From waiting-room conversation → structured clinical intelligence.**

---

## Standards & Domain References

The project concept is informed by:

- Ministry of AYUSH healthcare systems and terminology
- NAMASTE — National AYUSH Morbidity & Standardized Terminologies
- Ayushman Bharat Digital Mission (ABDM)
- HL7 FHIR R4
- WHO ICD-11 Traditional Medicine Chapter 2 (TM2)

The SIH proposal also records practitioner input/validation from Ayurveda and Homoeopathy practitioners.

---

## Smart India Hackathon 2026

| Field | Details |
|---|---|
| Problem Statement ID | **SIH26047** |
| Problem Statement | **Patient Case-Taking Software** |
| Theme | **Healthcare** |
| Category | **Software** |
| Team | **Care Catalysts** |
| Team ID | **RMKSIH26SW151** |
| Project | **MediKiosk** |

---

## Future Work

Planned engineering and validation work includes:

- production ABHA authentication
- production ABDM health-information exchange
- stronger handwritten-document recognition
- expanded regional-language validation
- practitioner-supervised clinical validation
- hospital/HIS integration
- stronger production security and audit controls
- controlled-pilot usability testing
- scalable deployment infrastructure

---

## Disclaimer

MediKiosk is an academic/hackathon prototype intended to assist **pre-consultation case-taking and information structuring**.

It is **not a medical device, diagnostic engine, emergency service or replacement for a qualified healthcare professional**. Red-flag detection and automatically extracted information must not be treated as a final diagnosis or independent clinical decision.

---

<p align="center">
  <b>MediKiosk</b><br/>
  Intelligent Pre-Consultation for Faster, Safer & Inclusive Healthcare
</p>

<p align="center">
  Built by <b>Team Care Catalysts</b> for Smart India Hackathon 2026
</p>
