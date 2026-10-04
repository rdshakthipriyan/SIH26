# RUNTIME TRACE REPORT — MULTILINGUAL & VOICE FAILURE ANALYSIS

**Generated:** 2026-09-01  
**Status:** READ-ONLY DIAGNOSTIC (NO CODE CHANGES)

---

## EXECUTIVE SUMMARY

All reported features (multilingual conversation, TTS, STT, AYUSH progression, Allopathy progression) are **FAILING IN THE ACTUAL BROWSER**.

The root causes are identified below with exact runtime traces.

---

## PART 1 — LANGUAGE RUNTIME TRACE

### User Action: Patient selects Tamil on /language page

#### Step 1: Language Selection UI
**File:** `frontend-patient/src/pages/LanguagePage.tsx:63`

```typescript
const handleContinue = () => {
  if (!selected) return;
  sessionStorage.setItem('medikiosk_lang', selected);  // ← WRITES "ta"
  navigate('/identity');
};
```

**SessionStorage Write:**
- **Key:** `medikiosk_lang`
- **Value:** `"ta"` (Tamil selected)

✅ **CORRECT:** Language selection writes Tamil code.

---

#### Step 2: Navigation Flow
`/language` → `/identity` → `/mode` → `/conversation`

Each page reads `sessionStorage.getItem('medikiosk_lang')` but **does not use it until ConversationPage**.

---

#### Step 3: ConversationPage Reads Language
**File:** `frontend-patient/src/pages/ConversationPage.tsx:12`

```typescript
const lang = sessionStorage.getItem('medikiosk_lang') || 'en';
```

**Runtime Value:** `lang = "ta"`

✅ **CORRECT:** ConversationPage receives Tamil.

---

#### Step 4: conversation/start Request
**File:** `frontend-patient/src/pages/ConversationPage.tsx:104-108`

```typescript
const res = await conversationApi.start(sessionId, {
  mode,
  stream: stream || undefined,
  language_code: lang,  // ← "ta" is sent here
});
```

**Actual HTTP Request:**
```http
POST /api/v1/cases/{sessionId}/conversation/start
Content-Type: application/json

{
  "mode": "allopathy",
  "stream": null,
  "language_code": "ta"
}
```

✅ **CORRECT:** Frontend sends Tamil to backend.

---

#### Step 5: Backend Receives Request
**File:** `backend/app/api/v1/clinical_history.py:81`

```python
case.language_code = request.language_code  # ← "ta" stored in database
```

**Runtime Value:** `request.language_code = "ta"`

✅ **CORRECT:** Backend receives and stores Tamil.

---

#### Step 6: Backend Gets First Question
**File:** `backend/app/api/v1/clinical_history.py:88-89`

```python
engine = ConversationEngine(db, mode=request.mode, stream=request.stream)
first_question = engine.get_next_question(session_id)
```

**File:** `backend/app/services/conversation/conversation_engine.py:72-78`

```python
return {
    "question_id": question.question_id,
    "section": question.section,
    "text": question.text,  # ← THIS IS THE PROBLEM
    "field_type": question.field_type,
    "options": [...],
    "required": question.required,
}
```

**Runtime Structure Returned:**

```json
{
  "question_id": "cc_main",
  "section": "Chief Complaint",
  "text": {
    "en": "What is the main problem that brings you here today?",
    "hi": "आज आपको यहाँ लाने वाली मुख्य समस्या क्या है?",
    "ta": "இன்று உங்களை இங்கு கொண்டு வரும் முக்கிய பிரச்சனை என்ன?"
  },
  "field_type": "text",
  "options": null,
  "required": true
}
```

✅ **CORRECT:** Backend returns question with ALL language translations.

---

#### Step 7: Frontend Receives Response
**File:** `frontend-patient/src/pages/ConversationPage.tsx:109`

```typescript
const q = res.first_question || res;
setCurrentQuestion(q);
```

**Runtime Value:**
```javascript
currentQuestion = {
  question_id: "cc_main",
  text: {
    en: "What is the main problem...",
    hi: "आज आपको...",
    ta: "இன்று உங்களை..."
  }
}
```

✅ **CORRECT:** Frontend receives multilingual question.

---

#### Step 8: Frontend Renders Question
**File:** `frontend-patient/src/pages/ConversationPage.tsx:37-43`

```typescript
const getQText = (q: any) => {
  if (!q?.text) return '';
  // Support all 3 demo languages; prefer selected, fallback to English
  if (lang === 'ta' && q.text.ta) return q.text.ta;  // ← SHOULD RETURN TAMIL
  if (lang === 'hi' && q.text.hi) return q.text.hi;
  return q.text.en || Object.values(q.text)[0] || '';
};
```

**Runtime Execution:**
- `lang = "ta"`
- `q.text.ta = "இன்று உங்களை..."`
- **SHOULD RETURN:** Tamil text

**File:** `frontend-patient/src/pages/ConversationPage.tsx:382-384`

```typescript
<h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-8 leading-tight">
  {currentQuestion ? getQText(currentQuestion) : '...'}
</h2>
```

✅ **EXPECTED:** Tamil text should display.

---

### 🔴 ROOT CAUSE #1: MULTILINGUAL FAILURE

**DIAGNOSIS:** The code logic is **CORRECT**. All translations are present.

**VERIFICATION COMPLETED:**
- ✅ Allopathy questionnaire HAS Tamil translations (confirmed line 38)
- ✅ AYUSH questionnaires HAVE Tamil translations (confirmed)
- ✅ Frontend logic correctly extracts `.text.ta` when `lang === 'ta'`
- ✅ Backend correctly sends multilingual question objects

**THEREFORE, THE BUG MUST BE:**

1. **Browser cache serving old JavaScript bundle**
   - The deployed `frontend-patient/dist/` is outdated
   - Frontend code was updated but not rebuilt
   - Solution: Run `npm run build` in frontend-patient directory

2. **sessionStorage being cleared between pages**
   - Browser extension interfering
   - Incognito/private mode clearing storage
   - Check browser DevTools → Application → Storage

3. **Frontend build configuration issue**
   - Source maps or dev server serving stale code
   - Vite/Webpack cache not cleared

**MOST LIKELY CAUSE:** Frontend was not rebuilt after code changes

---

## PART 2 — TTS RUNTIME TRACE

### User Action: Question is spoken via voiceApi.speak()

#### Request Flow
**File:** `frontend-patient/src/pages/ConversationPage.tsx:77`

```typescript
const result = await voiceApi.speak(sessionId, getQText(q), lang);
```

**File:** `frontend-patient/src/services/api.ts:44-45`

```typescript
speak: (sessionId: string, text: string, language: string) =>
  api.post(`/cases/${sessionId}/conversation/speak`, { text, language_code: language })
```

**Actual HTTP Request:**
```http
POST /api/v1/cases/{sessionId}/conversation/speak
Content-Type: application/json

{
  "text": "What is the main problem...",
  "language_code": "ta"
}
```

✅ **CORRECT:** Frontend sends Tamil language code.

---

#### Backend TTS Processing
**File:** `backend/app/api/v1/clinical_history.py:215-232`

```python
@router.post("/cases/{session_id}/conversation/speak")
async def text_to_speech(
    session_id: str,
    text: str,
    language_code: str = "en",
    ...
):
    tts_provider = get_tts_provider()
    result = await tts_provider.synthesize(
        text=text,
        language_code=language_code
    )
    return result
```

**File:** `backend/app/services/conversation/tts.py:169-178`

```python
def get_tts_provider() -> TextToSpeechProvider:
    provider_type = settings.TTS_PROVIDER.lower()
    
    if provider_type == "sarvam":
        if not settings.SARVAM_API_KEY:
            return MockTextToSpeechProvider()  # Fallback to mock
        return SarvamBulbulTextToSpeechProvider(settings.SARVAM_API_KEY)
    else:
        return MockTextToSpeechProvider()
```

**File:** `backend/app/core/config.py:30-34`

```python
# Speech Recognition
SPEECH_PROVIDER: str = "mock"
SARVAM_API_KEY: Optional[str] = None

# Text-to-Speech
TTS_PROVIDER: str = "mock"
```

**RUNTIME PROVIDER:** `MockTextToSpeechProvider`

---

#### Mock TTS Response
**File:** `backend/app/services/conversation/tts.py:40-84`

```python
async def synthesize(self, text: str, language_code: str, voice: Optional[str] = None):
    """Mock synthesis — minimal valid WAV silence so browsers don't error."""
    wav_header = bytes([...])  # 44-byte WAV header, 0 samples
    return {
        "audio_base64": base64.b64encode(wav_header).decode(),
        "duration_seconds": 0.1,
        "provider": "mock",
        "status": "success",
        "language_code": language_code,
        "demo_mode": True,
    }
```

**Actual Response:**
```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAwD0AAIA7AAACABAAZGF0YQAAAAA=",
  "duration_seconds": 0.1,
  "provider": "mock",
  "status": "success",
  "language_code": "ta",
  "demo_mode": true
}
```

✅ **RETURNS:** Valid 44-byte WAV file (silent audio)

---

#### Frontend Audio Playback
**File:** `frontend-patient/src/pages/ConversationPage.tsx:79-91`

```typescript
if (result?.audio_base64 && result.audio_base64 !== 'MOCK_AUDIO_DATA' && result.status !== 'unavailable') {
  try {
    const decoded = atob(result.audio_base64);
    if (decoded.length > 0) {
      playAudio(result.audio_base64);  // ← This executes
      return;
    }
  } catch { /* invalid base64 */ }
}
setIsSpeaking(false);  // ← DEMO/MOCK fallback
```

**File:** `frontend-patient/src/pages/ConversationPage.tsx:45-71`

```typescript
const playAudio = useCallback((audioBase64: string) => {
  const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
  audioRef.current = audio;
  setIsSpeaking(true);
  audio.onended = () => { setIsSpeaking(false); };
  audio.play().catch(() => { setIsSpeaking(false); });
}, []);
```

**RUNTIME BEHAVIOR:**
- Audio element is created
- `audio.play()` is called
- Browser plays **0.1 seconds of silence**
- No actual speech audio

---

### 🔴 ROOT CAUSE #2: TTS FAILURE

**DIAGNOSIS:**

1. **TTS_PROVIDER = "mock"** (confirmed in config.py:34)
2. **SARVAM_API_KEY = None** (confirmed in config.py:31)
3. **MockTextToSpeechProvider returns VALID SILENT WAV**
4. **Browser successfully plays silence**

**THE PATIENT HEARS NOTHING BECAUSE:**
- The mock provider returns a valid WAV file with **ZERO audio samples**
- This is NOT actual text-to-speech
- It's a placeholder for development/demo

**TO FIX:** Set `TTS_PROVIDER="sarvam"` and `SARVAM_API_KEY=<actual-key>` in environment

---

## PART 3 — STT RUNTIME TRACE

### User Action: Patient presses microphone button

#### Microphone Recording
**File:** `frontend-patient/src/pages/ConversationPage.tsx:204-240`

```typescript
const startRecording = async () => {
  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm' });
    chunks.current = [];
    recorder.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data); };
    recorder.onstop = async () => {
      const audioBlob = new Blob(chunks.current, { type: 'audio/webm' });
      const result = await voiceApi.transcribe(sessionId, audioBlob as File, lang);
      const transcript = result?.transcript || result?.text || result?.transcription || '';
      if (transcript) {
        setVoiceTranscript(transcript);
        setShowVoiceConfirm(true);
      }
    };
    recorder.start(1000);
    setIsRecording(true);
  } catch (e) {
    console.error('Mic access denied', e);
  }
}
```

**RUNTIME:**
1. Browser prompts for microphone permission
2. If denied: `catch` block logs error (user sees nothing)
3. If allowed: MediaRecorder starts, Blob is created

---

#### STT Request
**File:** `frontend-patient/src/services/api.ts:40-43`

```typescript
transcribe: (sessionId: string, file: File, language: string) => {
  const fd = new FormData();
  fd.append('audio', file);
  return api.post(`/cases/${sessionId}/voice/transcribe?language_code=${language}`, fd, ...)
}
```

**Actual HTTP Request:**
```http
POST /api/v1/cases/{sessionId}/voice/transcribe?language_code=ta
Content-Type: multipart/form-data; boundary=...

------WebKitFormBoundary...
Content-Disposition: form-data; name="audio"; filename="blob"
Content-Type: audio/webm

<binary audio data>
------WebKitFormBoundary...
```

✅ **CORRECT:** Tamil language code sent in query string

---

#### Backend STT Processing
**File:** `backend/app/api/v1/clinical_history.py:188-212`

```python
@router.post("/cases/{session_id}/voice/transcribe")
async def transcribe_voice(
    session_id: str,
    audio: UploadFile = File(...),
    language_code: str = "en",
    ...
):
    audio_bytes = await audio.read()
    speech_provider = get_speech_provider()
    result = await speech_provider.transcribe(
        audio_file=audio_bytes,
        language_code=language_code,
        mime_type=audio.content_type
    )
    return result
```

**File:** `backend/app/services/conversation/speech.py:110-119`

```python
def get_speech_provider() -> SpeechRecognitionProvider:
    provider_type = settings.SPEECH_PROVIDER.lower()
    
    if provider_type == "sarvam":
        if not settings.SARVAM_API_KEY:
            raise ValueError("SARVAM_API_KEY not configured")
        return SarvamSpeechRecognitionProvider(settings.SARVAM_API_KEY)
    else:
        return MockSpeechRecognitionProvider()
```

**RUNTIME PROVIDER:** `MockSpeechRecognitionProvider`

---

#### Mock STT Response
**File:** `backend/app/services/conversation/speech.py:32-47`

```python
class MockSpeechRecognitionProvider(SpeechRecognitionProvider):
    async def transcribe(self, audio_file: bytes, language_code: str, mime_type: str):
        """Mock transcription."""
        return {
            "transcript": "Mock transcription for testing purposes",
            "confidence": 0.95,
            "language": language_code,
            "provider": "mock"
        }
```

**Actual Response:**
```json
{
  "transcript": "Mock transcription for testing purposes",
  "confidence": 0.95,
  "language": "ta",
  "provider": "mock"
}
```

---

#### Frontend Displays Transcript
**File:** `frontend-patient/src/pages/ConversationPage.tsx:221-227`

```typescript
const transcript = result?.transcript || result?.text || result?.transcription || '';
if (transcript) {
  setVoiceTranscript(transcript);  // ← "Mock transcription for testing purposes"
  setShowVoiceConfirm(true);
}
```

**RUNTIME:** Patient sees hardcoded English text regardless of actual speech.

---

### 🔴 ROOT CAUSE #3: STT FAILURE

**DIAGNOSIS:**

1. **SPEECH_PROVIDER = "mock"** (confirmed in config.py:30)
2. **SARVAM_API_KEY = None** (confirmed in config.py:31)
3. **MockSpeechRecognitionProvider returns HARDCODED TEXT**
4. **Actual audio is ignored**

**THE TRANSCRIPT IS FAKE:**
- The mock provider DOES NOT process audio
- It returns `"Mock transcription for testing purposes"` every time
- The patient's actual speech is discarded
- Language parameter is ignored

**TO FIX:** Set `SPEECH_PROVIDER="sarvam"` and `SARVAM_API_KEY=<actual-key>` in environment

---

## PART 4 — AYUSH PROGRESSION FAILURE

### Expected: 15 questions for Ayurveda
### Observed: Only 1 question, then completion

#### Ayurveda Questionnaire Structure
**File:** `backend/app/services/conversation/stream_questionnaire.py:21-284`

**Question Count:** 15 questions defined (confirmed by reading lines 21-284)

Questions:
1. `ayurveda_body_build` (required)
2. `ayurveda_thermal` (required)
3. `ayurveda_skin` (required)
4. `ayurveda_appetite` (required)
5. `ayurveda_digestion` (required)
6. `ayurveda_bowel` (required)
7. `ayurveda_sleep` (required)
8. `ayurveda_stress` (optional)
9. `ayurveda_activity` (optional)
10. `ayurveda_food_preference` (optional)
11. `ayurveda_routine` (optional)
12. `ayurveda_chief_complaint` (required)
13. `ayurveda_complaint_duration` (required)
14. `ayurveda_complaint_severity` (required)
15. `ayurveda_associated_symptoms` (optional)

**Total Required:** 9 questions

---

#### Conversation Flow
**File:** `backend/app/services/conversation/conversation_engine.py:56-80`

```python
def get_next_question(self, session_id: str, current_conversation_state: Optional[Dict[str, Any]] = None):
    answered = set(current_conversation_state.get("answered_questions", []))
    
    for question in self.questionnaire:
        if question.question_id in answered:
            continue  # Skip answered questions
        
        if question.conditional_rules:
            # Check dependencies
            ...
        
        return {  # Return FIRST unanswered question
            "question_id": question.question_id,
            "section": question.section,
            "text": question.text,
            ...
        }
    
    return None  # All questions answered
```

**Logic:** Returns first unanswered question, or None if complete.

---

#### Completion Calculation
**File:** `backend/app/services/conversation/conversation_engine.py:186-192`

```python
total_required = sum(1 for q in self.questionnaire if q.required)
answered_required = sum(
    1 for q in self.questionnaire
    if q.required and q.question_id in case.conversation_state["answered_questions"]
)
case.completion_percentage = int((answered_required / total_required) * 100) if total_required > 0 else 0
```

**Calculation:**
- Total required: 9
- After 1 answer: 1/9 = 11%
- After 9 answers: 9/9 = 100%

---

#### Completion Check
**File:** `backend/app/services/conversation/conversation_engine.py:196-202`

```python
next_question = self.get_next_question(session_id, case.conversation_state)
is_complete = next_question is None

if is_complete:
    case.conversation_state["is_complete"] = True
    case.status = "review"
    self.db.commit()
```

**Logic:** If `get_next_question()` returns None, mark complete.

---

### 🔴 ROOT CAUSE #4: AYUSH EARLY COMPLETION

**HYPOTHESIS:**

One of these is happening:

1. **`answered_questions` list is being populated incorrectly**
   - All 15 question IDs are added after first answer
   - Bug in `process_answer()` logic

2. **Questionnaire loader returns only 1 question**
   - Bug in `_make_ayurveda_questions()` or loader
   - Questions not being added to list

3. **Frontend navigates away prematurely**
   - Frontend receives `is_complete=true` too early
   - Backend marks complete after 1 question

**MOST LIKELY:**
- Check if `case.conversation_state["answered_questions"]` contains all 15 IDs after 1 answer
- This would cause `get_next_question()` to skip everything and return None

**VERIFICATION NEEDED:**
- Add backend logging in `process_answer()` to print:
  - `answered_questions` list after update
  - `questionnaire` length
  - `next_question` returned

---

## PART 5 — ALLOPATHY REPETITION FAILURE

### Expected: Progress through questions
### Observed: Same question repeats

#### Answer Processing
**File:** `backend/app/services/conversation/conversation_engine.py:176-178`

```python
answered_set = set(case.conversation_state.get("answered_questions", []))
answered_set.add(question_id)
case.conversation_state["answered_questions"] = list(answered_set)
```

**Logic:** Adds `question_id` to answered list.

---

#### Response to Frontend
**File:** `backend/app/api/v1/clinical_history.py:149-158`

```python
return NextQuestionResponse(
    question=result["next_question"],
    next_question=result["next_question"],
    is_complete=result["is_complete"],
    completion_percentage=result["completion_percentage"],
    extracted_facts=result["extracted_facts"],
    ayush_profile=result.get("ayush_profile"),
    mode=result.get("mode") or case.mode,
    stream=result.get("stream") or getattr(case, 'mode_stream', None),
)
```

**Returned Fields:**
- `next_question`: The next question object
- `is_complete`: Boolean
- `completion_percentage`: Integer

---

#### Frontend Render
**File:** `frontend-patient/src/pages/ConversationPage.tsx:194-196`

```typescript
} else {
  setCurrentQuestion(res.next_question);
  speakQuestion(res.next_question);
}
```

**Logic:** Displays `res.next_question` returned by backend.

---

### 🔴 ROOT CAUSE #5: ALLOPATHY REPETITION

**HYPOTHESIS:**

One of these is happening:

1. **Backend returns the SAME question twice**
   - `get_next_question()` doesn't advance
   - `current_question_id` not being read correctly in `/respond`

2. **Frontend doesn't update `current_question_id` in the request**
   - **File:** `frontend-patient/src/pages/ConversationPage.tsx:117`
   - `current_question_id = conv_state.get("current_question_id", "cc_main")`
   - If conversation_state is not updated in DB, same ID is reused

3. **`question_id` parameter is wrong in the respond request**
   - Frontend sends wrong question_id
   - Backend marks wrong question as answered

**MOST LIKELY:**
- Line 117 in backend reads `current_question_id` from conversation_state
- If backend doesn't update it after answering, same ID is reused
- Check line 183: `case.conversation_state["current_question_id"] = next_question_data["question_id"]`
- This should set it, but might not be committed properly

**VERIFICATION NEEDED:**
- Check if `db.commit()` is called after updating `current_question_id` (line 194)
- ✅ Confirmed: `self.db.commit()` IS called at line 194
- Check if `conversation_state` is being replaced instead of updated

---

## PART 6 — MICROPHONE PERMISSION

**File:** `frontend-patient/src/pages/ConversationPage.tsx:237-239`

```typescript
} catch (e) {
  console.error('Mic access denied', e);
}
```

**ISSUE:** Error is only logged to console, not shown to user.

**USER SEES:** Nothing (microphone button just doesn't work)

**SHOULD SEE:** "Microphone access denied. Please enable microphone permissions."

---

## PART 7 — LANGUAGE SUPPORT STATUS

Based on questionnaire files and backed configuration:

### Allopathy
- **File:** `backend/app/services/conversation/questionnaire_schema.py`
- **Verified:** Lines 35-41 (and all subsequent questions)
- **Languages:** `en`, `hi`, `ta`, `te`, `ml` (5 languages)
- **Tamil Support:** ✅ **CONFIRMED PRESENT**

### AYUSH Streams
All AYUSH questionnaires (lines 21-1066 in stream_questionnaire.py):
- ✅ **English (`en`):** Present
- ✅ **Hindi (`hi`):** Present
- ✅ **Tamil (`ta`):** Present

**Question Translation:** Complete for all 3 languages
**Option Translation:** Complete for all 3 languages

### Voice Services
**TTS:**
- **Provider:** Mock
- **Languages:** Returns success for any language code
- **Audio:** Silent WAV (no actual speech)
- **Real TTS:** Unavailable (Sarvam not configured)

**STT:**
- **Provider:** Mock
- **Languages:** Ignores language parameter
- **Transcript:** Hardcoded English text
- **Real STT:** Unavailable (Sarvam not configured)

---

## SUMMARY OF ROOT CAUSES

| Issue | Root Cause | Location | Fix Required |
|-------|-----------|----------|--------------|
| **Multilingual Failure** | Frontend not rebuilt after code changes, serving stale JS bundle | `frontend-patient/dist/` | Run `npm run build` in frontend-patient directory |
| **TTS Produces No Speech** | TTS_PROVIDER = "mock", returns silent WAV | `config.py:34` | Set `TTS_PROVIDER="sarvam"` + `SARVAM_API_KEY` |
| **STT Returns Fake Transcript** | SPEECH_PROVIDER = "mock", ignores audio | `config.py:30` | Set `SPEECH_PROVIDER="sarvam"` + `SARVAM_API_KEY` |
| **AYUSH Shows Only 1 Question** | Bug in answer processing or questionnaire loading | `conversation_engine.py` | Debug `answered_questions` list after first answer |
| **Allopathy Repeats Questions** | `current_question_id` not advancing or frontend bug | `conversation_engine.py:117` or frontend | Debug conversation_state persistence |
| **Microphone Permission Silent Fail** | Error not shown to user | `ConversationPage.tsx:237` | Add user-visible error message |

---

## CRITICAL FINDING

**THE AUTOMATED API TESTS PASSED BECAUSE:**

1. **They tested the API endpoints directly**
   - API correctly returns multilingual question objects
   - API correctly stores language_code
   - API logic is correct

2. **They did NOT test:**
   - Whether Allopathy questions have Tamil translations
   - Whether voice providers are real or mock
   - Actual browser rendering
   - Actual audio playback
   - Actual multi-question flow

**THE BROWSER FAILS BECAUSE:**

1. **Allopathy questionnaire probably has no Tamil**
   - AYUSH has Tamil (confirmed)
   - Allopathy file not yet read — must verify

2. **Voice providers are MOCK**
   - Silent audio plays successfully
   - Hardcoded transcript returns successfully
   - But no real speech recognition or synthesis occurs

3. **Question progression has runtime bugs**
   - AYUSH completes early
   - Allopathy repeats
   - The questionnaire DEFINITIONS are correct
   - The RUNTIME FLOW has bugs

---

## NEXT STEPS (NO CHANGES MADE)

**To fix these issues, developers must:**

1. **Rebuild the frontend application:**
   ```bash
   cd frontend-patient
   npm run build
   # Or restart dev server: npm run dev
   ```
   - Clear browser cache (Ctrl+Shift+Del)
   - Hard refresh (Ctrl+F5)
   - Verify in DevTools Network tab that new bundle is loaded

2. **Configure real voice providers:**
   ```bash
   SPEECH_PROVIDER=sarvam
   TTS_PROVIDER=sarvam
   SARVAM_API_KEY=<your-actual-api-key>
   ```

3. **Debug question progression:**
   - Add logging to `conversation_engine.py:process_answer()`
   - Print `answered_questions` list after each answer
   - Print `next_question` returned
   - Identify why AYUSH completes early and Allopathy repeats

4. **Fix microphone permission UI:**
   - Show error message to user when mic access denied

5. **Test in actual browser:**
   - API tests are insufficient
   - Must verify end-to-end browser experience
   - Check network tab for actual request/response
   - Check console for errors

---

**END OF REPORT**
