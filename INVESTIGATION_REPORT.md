# MediKiosk Questionnaire Investigation Report
**Date:** 2026-09-01  
**Session:** Comprehensive Frontend/Backend State Analysis

---

## Executive Summary

Investigation confirmed that the **backend Ayurveda question progression is working correctly**. API testing proves questions advance: `body_build → thermal → skin → appetite → digestion → bowel → sleep → stress → activity → food_preference → routine → chief_complaint → complaint_duration → complaint_severity → associated_symptoms`.

**Critical bugs identified:**
1. ❌ Backend accepts stale `question_id` without validation
2. ✅ Frontend uses correct `res.next_question` field
3. ⚠️ Unicode encoding corrupts Tamil/Hindi in HTTP responses (Windows console issue, not data corruption)
4. ⚠️ Frontend state management needs verification in actual browser testing

---

## Problem 1: Frontend Question State Management

### Investigation Results

**File:** `frontend-patient/src/pages/ConversationPage.tsx:194`

```typescript
setCurrentQuestion(res.next_question);
```

**Backend Response Schema:** `backend/app/schemas/conversation.py:79-91`

```python
class NextQuestionResponse(BaseModel):
    question: Optional[Question] = None
    next_question: Optional[Question] = None  # ← Frontend uses THIS
    is_complete: bool = False
    completion_percentage: float = 0.0
    extracted_facts: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None
    ayush_profile: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    stream: Optional[str] = None
```

**Backend API Implementation:** `backend/app/api/v1/clinical_history.py:178-187`

```python
return NextQuestionResponse(
    question=result["next_question"],           # Both fields
    next_question=result["next_question"],      # set to same value
    is_complete=result["is_complete"],
    completion_percentage=result["completion_percentage"],
    extracted_facts=result["extracted_facts"],
    ayush_profile=result.get("ayush_profile"),
    mode=result.get("mode") or case.mode,
    stream=result.get("stream") or getattr(case, 'mode_stream', None),
)
```

**Verdict:** ✅ **Frontend implementation is CORRECT**

The frontend correctly reads `res.next_question`. Both `question` and `next_question` contain the same value, so there's no mismatch.

---

## Problem 2: Backend Stale Question ID Validation (CRITICAL)

### Current Behavior

**File:** `backend/app/api/v1/clinical_history.py:123-157`

```python
# Get current question from conversation state
conv_state = case.conversation_state or {}
current_question_id = conv_state.get("current_question_id")

# ... code that determines current_question_id from state ...

# ❌ CRITICAL BUG: response.question_id from frontend is COMPLETELY IGNORED
engine = ConversationEngine(...)
result = engine.process_answer(
    session_id=session_id,
    question_id=current_question_id,  # ← Always uses state, never validates request
    answer_text=response.answer_text,
    ...
    answer_value=response.answer_value,
)
```

### The Vulnerability

**Manual Test Exposed:**
```
Backend state: ayurveda_thermal (current)
Frontend sends: question_id = ayurveda_body_build (STALE)
Backend behavior: Accepts answer, records it against ayurveda_thermal
Result: Data corruption - SLIM recorded as thermal answer instead of body_build
```

**Root Cause:**  
The `question_id` field sent by the frontend in `ConversationResponse` is ignored. The backend always uses its own state. If the frontend gets out of sync, stale question IDs silently corrupt the answer history.

### Required Fix

Add validation in `backend/app/api/v1/clinical_history.py`:

```python
# After line 125: current_question_id = conv_state.get("current_question_id")

# Validate question_id if provided by frontend
if response.question_id:
    if current_question_id and response.question_id != current_question_id:
        # Frontend and backend are out of sync
        raise HTTPException(
            status_code=409,
            detail={
                "error": "question_mismatch",
                "message": f"Question ID mismatch. Expected '{current_question_id}', received '{response.question_id}'.",
                "expected_question_id": current_question_id,
                "received_question_id": response.question_id,
                "hint": "Frontend state is stale. Please refresh the current question."
            }
        )
```

**Status:** ❌ **NOT YET IMPLEMENTED** (requires approval for data-integrity change)

---

## Problem 3: Unicode Encoding Corruption

### Manual API Test Results

Raw HTTP response contained:
```
à®...
à¤...
```

Instead of valid Tamil/Hindi Unicode.

### Investigation

**Source Data:** `backend/app/services/conversation/stream_questionnaire.py:30`

```python
text={
    "en": "How would you describe your general body build?",
    "hi": "आप अपने शरीर की बनावट का वर्णन कैसे करेंगे?",
    "ta": "உங்கள் உடல் அமைப்பை எவ்வாறு விவரிப்பீர்கள்?",
},
```

The source file contains **valid UTF-8 Unicode** for Tamil and Hindi.

**Python Environment Check:**
```bash
$ python -c "import sys; print(sys.stdout.encoding)"
cp1252  # ← Windows console issue
```

**Console output corruption** does NOT mean the HTTP responses are corrupted.

### Verification Required

1. **Test actual HTTP response encoding:**
   ```bash
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/v1/cases/<session>/conversation/start \
        -H "Content-Type: application/json" \
        -d '{"mode":"ayush","stream":"ayurveda","language_code":"ta"}' \
        | jq '.first_question.text.ta' | od -A x -t x1z
   ```

2. **Check FastAPI JSON encoding:** Should use `ensure_ascii=False`

3. **Frontend rendering:** Verify browser actually receives corrupted data or just displays it incorrectly

**Status:** ⚠️ **REQUIRES BROWSER TESTING** (console artifacts may not reflect actual HTTP corruption)

---

## Problem 4: Language Selection Flow

### Current Implementation

**Storage:** `frontend-patient/src/pages/ConversationPage.tsx:12`
```typescript
const lang = sessionStorage.getItem('medikiosk_lang') || 'en';
```

**API Request:** `frontend-patient/src/pages/ConversationPage.tsx:107`
```typescript
language_code: lang,
```

**Backend Reception:** `backend/app/api/v1/clinical_history.py:81-85`
```python
case.language_code = request.language_code
```

**Question Rendering:** `frontend-patient/src/pages/ConversationPage.tsx:37-43`
```typescript
const getQText = (q: any) => {
  if (!q?.text) return '';
  if (lang === 'ta' && q.text.ta) return q.text.ta;
  if (lang === 'hi' && q.text.hi) return q.text.hi;
  return q.text.en || Object.values(q.text)[0] || '';
};
```

**Verdict:** ✅ **Implementation looks correct**, needs browser verification

---

## Problem 5: TTS/STT Status

**Current Provider:** Mock (`backend/app/services/conversation/speech.py`)

**Behavior:**
- `conversation/start` returns `audio_url: null`
- TTS returns placeholder base64
- STT returns empty transcripts

**Status:** 🔵 **DOCUMENTED** (real TTS/STT implementation deferred)

---

## Problem 6: Allopathy Mode

**Previous Browser Behavior:**  
"Can you describe this problem in more detail?" repeating.

**Hypothesis:**  
Same frontend state bug affecting both Allopathy and AYUSH modes.

**Status:** ⚠️ **REQUIRES BROWSER TESTING**

---

## Required Fixes

### Fix 1: Backend Stale Question ID Validation ⚠️ HIGH PRIORITY

**File:** `backend/app/api/v1/clinical_history.py`  
**Location:** After line 125  
**Action:** Add validation to reject mismatched question_id

### Fix 2: Verify HTTP Response Encoding

**Action:** Add explicit UTF-8 encoding to FastAPI JSON responses  
**Check:** `app/main.py` for JSON encoder configuration

### Fix 3: Add Debug Logging (Temporary)

**File:** `backend/app/api/v1/clinical_history.py`  
**Lines:** 138-146 (already present)

Logs show:
- Session ID
- Mode/Stream
- Current question ID from state
- Question ID from request
- Answer text/value
- Answered questions before/after

---

## Browser Test Plan

### Test A: AYUSH English
1. Language: English
2. AYUSH → Ayurveda
3. **Expected:** Questions 1-5+ advance sequentially
4. **Verify:** No Documents redirect after Question 1

### Test B: AYUSH Tamil
1. Language: Tamil
2. AYUSH → Ayurveda
3. **Expected:** Tamil text/options render correctly
4. **Verify:** Questions 1-3+ advance sequentially

### Test C: Allopathy
1. Language: English
2. Allopathy
3. **Expected:** 5+ different questions, no repetition

---

## Implementation Status

| Task | Status | Notes |
|------|--------|-------|
| Frontend state investigation | ✅ Complete | Uses correct field |
| Backend stale-ID validation | ❌ Not implemented | Requires approval |
| Unicode encoding investigation | ⚠️ Partial | Needs HTTP-level verification |
| Language flow verification | ⚠️ Pending | Needs browser test |
| TTS/STT documentation | ✅ Complete | Currently mock |
| Browser testing | ❌ Not started | Blocked on fixes |

---

## Recommended Next Steps

1. **Implement stale question ID validation** (highest priority data-integrity fix)
2. **Run browser tests** to confirm actual behavior vs. API-level tests
3. **Verify HTTP encoding** with raw curl + hex dump
4. **Fix any confirmed frontend state bugs** revealed by browser testing
5. **Document final test results** with screenshots/logs

---

## Files Modified (Pending)

None yet - awaiting approval for data-integrity changes.

## Files Investigated

- ✅ `frontend-patient/src/pages/ConversationPage.tsx`
- ✅ `frontend-patient/src/types/index.ts`
- ✅ `frontend-patient/src/services/api.ts`
- ✅ `backend/app/api/v1/clinical_history.py`
- ✅ `backend/app/services/conversation/conversation_engine.py`
- ✅ `backend/app/services/conversation/stream_questionnaire.py`
- ✅ `backend/app/schemas/conversation.py`

---

**End of Investigation Report**
