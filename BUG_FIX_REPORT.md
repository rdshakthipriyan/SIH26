# CONVERSATION FLOW BUG FIX REPORT

**Date:** 2026-09-01  
**Status:** FIXED - REQUIRES MANUAL TESTING

---

## EXECUTIVE SUMMARY

Two critical bugs in the patient conversation flow have been identified and fixed:

1. **AYUSH progression completing after 1 question** (should progress through all 15)
2. **Allopathy repeating the same question** (should advance to next question)

**Root Cause:** SQLAlchemy JSON field mutation detection failure

---

## BUG #1: AYUSH QUESTION PROGRESSION

### Symptoms
- Patient selects AYUSH → Ayurveda
- Conversation starts with `ayurveda_body_build`
- After answering, immediately goes to Documents page
- Expected: Progress through all 15 questions

### Root Cause Analysis

**File:** `backend/app/services/conversation/conversation_engine.py`

The issue was **SQLAlchemy JSON field mutation detection**. When code directly mutates nested JSON fields:

```python
# BROKEN CODE (before fix)
case.conversation_state["answered_questions"] = list(answered_set)
case.conversation_state["answers"] = answers
case.conversation_state["current_question_id"] = next_question_id
self.db.commit()
```

SQLAlchemy does **NOT** detect these changes because it tracks the dictionary object reference, not the contents. After `db.commit()`, the changes are NOT persisted to the database.

On the next request:
- `conversation_state` is read from database (unchanged)
- `answered_questions` is still `[]`
- The same question is returned
- OR the system thinks all questions are answered (depending on timing)

### The Fix

**Changed:** Work with a copy of `conversation_state` and reassign the entire dictionary:

```python
# FIXED CODE
# Work with a copy
conversation_state = dict(case.conversation_state)

# Mutate the copy
conversation_state["answered_questions"] = answered_questions_list
conversation_state["current_question_id"] = next_question_id
conversation_state["completion_percentage"] = percentage
conversation_state["is_complete"] = is_complete

# Reassign to trigger SQLAlchemy change detection
case.conversation_state = conversation_state

self.db.commit()  # Now changes ARE persisted
```

### Files Modified

1. **`backend/app/services/conversation/conversation_engine.py`**
   - Lines 138-145: Create copy of `conversation_state` at start
   - Lines 176-220: Refactored answer processing to work with copy
   - Added comprehensive debug logging
   - Removed redundant `get_next_question()` call

2. **`backend/app/api/v1/clinical_history.py`**
   - Lines 115-130: Improved `current_question_id` fallback logic
   - Added debug logging to trace request/response

---

## BUG #2: ALLOPATHY QUESTION REPETITION

### Symptoms
- Patient selects Allopathy
- Answers first question: "What is the main problem..."
- Next question appears: "Can you describe this problem in more detail?"
- After answering, SAME question appears again
- Loop continues indefinitely

### Root Cause Analysis

**File:** `backend/app/api/v1/clinical_history.py` line 117

**Same SQLAlchemy JSON mutation issue**, PLUS:

```python
# BROKEN CODE (before fix)
current_question_id = conv_state.get("current_question_id", "cc_main")
```

The default value `"cc_main"` is the FIRST Allopathy question. When `conversation_state` doesn't persist (due to mutation bug), the API endpoint always uses `"cc_main"` as the current question, causing it to:

1. Mark `"cc_main"` as answered
2. Return next question (e.g., `"cc_details"`)
3. On next request, read `current_question_id` from DB
4. DB still has empty `conversation_state` (mutation not detected)
5. Default to `"cc_main"` again
6. Repeat

### The Fix

1. **Fixed SQLAlchemy mutation** (same as AYUSH fix above)

2. **Improved default logic** in `clinical_history.py`:

```python
# FIXED CODE
current_question_id = conv_state.get("current_question_id")

if not current_question_id:
    # Dynamically determine first question based on mode
    temp_engine = ConversationEngine(db, mode=case.mode, stream=case.mode_stream)
    first_q = temp_engine.get_next_question(session_id, conv_state)
    if first_q:
        current_question_id = first_q["question_id"]
    else:
        current_question_id = "cc_main"  # Final fallback
```

This ensures:
- AYUSH gets `ayurveda_body_build` (not `cc_main`)
- Even if state is empty, correct first question is used
- No hardcoded assumptions about question IDs

---

## DETAILED CODE CHANGES

### `backend/app/services/conversation/conversation_engine.py`

**Lines 138-170:** Initialize and work with copy
```python
# CRITICAL FIX: Work with a copy to avoid SQLAlchemy JSON mutation issues
conversation_state = dict(case.conversation_state)
answers = conversation_state.setdefault("answers", {})

# Store answer
answers[question_id] = answer_value or answer_text
conversation_state["answers"] = answers

# Store answer records
answer_records: List[Dict[str, Any]] = conversation_state.setdefault("answer_records", [])
answer_records.append({...})
conversation_state["answer_records"] = answer_records
```

**Lines 176-220:** Mark answered and get next question
```python
# Mark question as answered
answered_set = set(conversation_state.get("answered_questions", []))
answered_set.add(question_id)
answered_questions_list = list(answered_set)
conversation_state["answered_questions"] = answered_questions_list

# Get next question
next_question_data = self.get_next_question(session_id, conversation_state)
is_complete = next_question_data is None

if next_question_data:
    conversation_state["current_question_id"] = next_question_data["question_id"]

# Update completion
total_required = sum(1 for q in self.questionnaire if q.required)
answered_required = sum(
    1 for q in self.questionnaire
    if q.required and q.question_id in answered_questions_list
)
case.completion_percentage = int((answered_required / total_required) * 100) if total_required > 0 else 0
conversation_state["completion_percentage"] = case.completion_percentage
conversation_state["is_complete"] = is_complete

# CRITICAL: Assign the entire dict to force SQLAlchemy change detection
case.conversation_state = conversation_state

# Debug logging (can be removed in production)
print(f"\n=== CONVERSATION DEBUG ===")
print(f"Session: {session_id}")
print(f"Mode: {self.mode}, Stream: {self.stream}")
print(f"Questionnaire length: {len(self.questionnaire)}")
print(f"Question answered: {question_id}")
print(f"Answer value: {answer_value}")
print(f"Answered questions: {answered_questions_list}")
print(f"Total answered: {len(answered_questions_list)}/{len(self.questionnaire)}")
print(f"Next question: {next_question_data['question_id'] if next_question_data else 'NONE'}")
print(f"Is complete: {is_complete}")
print(f"Completion %: {case.completion_percentage}")
print(f"========================\n")

if is_complete:
    case.status = "review"

self.db.commit()

next_question = next_question_data
```

**Line 234:** Fixed variable name collision
```python
answer_records_for_ayush: List[Dict[str, Any]] = conversation_state.get("answer_records", [])
```

---

### `backend/app/api/v1/clinical_history.py`

**Lines 87-98:** Added debug logging for conversation start
```python
# Get first question using unified loader with mode + stream
engine = ConversationEngine(db, mode=request.mode, stream=request.stream)
first_question = engine.get_next_question(session_id)

# Debug logging
print(f"\n=== API START DEBUG ===")
print(f"Session: {session_id}")
print(f"Mode: {request.mode}, Stream: {request.stream}")
print(f"Language: {request.language_code}")
print(f"First question: {first_question['question_id'] if first_question else 'NONE'}")
print(f"========================\n")
```

**Lines 115-132:** Improved current question detection
```python
# Get current question from conversation state
conv_state = case.conversation_state or {}
current_question_id = conv_state.get("current_question_id")

# If no current_question_id is set, determine the first question based on mode
if not current_question_id:
    # Get engine to determine first question
    temp_engine = ConversationEngine(db, mode=case.mode or "allopathy", stream=getattr(case, 'mode_stream', None))
    first_q = temp_engine.get_next_question(session_id, conv_state)
    if first_q:
        current_question_id = first_q["question_id"]
    else:
        current_question_id = "cc_main"  # Final fallback

# Debug logging
print(f"\n=== API RESPOND DEBUG ===")
print(f"Session: {session_id}")
print(f"Mode: {case.mode}, Stream: {getattr(case, 'mode_stream', None)}")
print(f"Current question ID from state: {current_question_id}")
print(f"Question ID from request: {response.question_id if hasattr(response, 'question_id') else 'NOT PROVIDED'}")
print(f"Answer text: {response.answer_text[:50] if response.answer_text else 'NONE'}...")
print(f"Answer value: {response.answer_value}")
print(f"Answered questions BEFORE: {conv_state.get('answered_questions', [])}")
print(f"========================\n")
```

---

## TESTING INSTRUCTIONS

### Prerequisites
1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. Ensure database is initialized

### Test 1: AYUSH Progression (15 Questions)

**Using the test script:**
```bash
cd "D:\Projects\New folder"
python test_conversation_flow.py
```

**Manual API Testing:**

1. **Create session:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Test Patient",
    "patient_age": 35,
    "is_guest": true,
    "consent_given": true,
    "mode": "ayush",
    "language_code": "en"
  }'
```

Save the `session_id` and `token`.

2. **Start conversation:**
```bash
curl -X POST "http://localhost:8000/api/v1/cases/{SESSION_ID}/conversation/start" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ayush",
    "stream": "ayurveda",
    "language_code": "en"
  }'
```

**Expected:**
```json
{
  "first_question": {
    "question_id": "ayurveda_body_build",
    "text": {"en": "How would you describe your general body build?"},
    "options": [...]
  }
}
```

3. **Answer first question:**
```bash
curl -X POST "http://localhost:8000/api/v1/cases/{SESSION_ID}/conversation/respond" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_text": "Slim and light",
    "answer_value": "SLIM",
    "input_mode": "touch"
  }'
```

**Expected:**
```json
{
  "next_question": {
    "question_id": "ayurveda_thermal",
    "text": {"en": "Do you usually feel comfortable in cool weather or warm weather?"}
  },
  "is_complete": false,
  "completion_percentage": 7
}
```

4. **Repeat for all 15 questions**

**Expected question sequence:**
1. `ayurveda_body_build`
2. `ayurveda_thermal`
3. `ayurveda_skin`
4. `ayurveda_appetite`
5. `ayurveda_digestion`
6. `ayurveda_bowel`
7. `ayurveda_sleep`
8. `ayurveda_stress` (optional)
9. `ayurveda_activity` (optional)
10. `ayurveda_food_preference` (optional)
11. `ayurveda_routine` (optional)
12. `ayurveda_chief_complaint`
13. `ayurveda_complaint_duration`
14. `ayurveda_complaint_severity`
15. `ayurveda_associated_symptoms` (optional)

**After question 15:**
```json
{
  "next_question": null,
  "is_complete": true,
  "completion_percentage": 100,
  "ayush_profile": {
    "prakriti": {...},
    "agni": {...},
    ...
  }
}
```

---

### Test 2: Allopathy Progression (No Repetition)

1. **Create session** (same as above, `mode: "allopathy"`)

2. **Start conversation:**
```bash
curl -X POST "http://localhost:8000/api/v1/cases/{SESSION_ID}/conversation/start" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "allopathy",
    "language_code": "en"
  }'
```

**Expected:**
```json
{
  "first_question": {
    "question_id": "cc_main",
    "text": {"en": "What is the main problem or complaint that brings you here today?"}
  }
}
```

3. **Answer Q1:**
```bash
curl -X POST "http://localhost:8000/api/v1/cases/{SESSION_ID}/conversation/respond" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_text": "I have a headache",
    "input_mode": "touch"
  }'
```

**Expected:**
```json
{
  "next_question": {
    "question_id": "cc_details",
    "text": {"en": "Can you describe this problem in more detail?"}
  },
  "is_complete": false
}
```

4. **Answer Q2:**
```bash
curl -X POST "http://localhost:8000/api/v1/cases/{SESSION_ID}/conversation/respond" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_text": "It is a throbbing pain on the left side",
    "input_mode": "touch"
  }'
```

**Expected:**
```json
{
  "next_question": {
    "question_id": "onset",  // <-- DIFFERENT QUESTION
    "text": {"en": "When did this problem start?"}
  },
  "is_complete": false
}
```

**❌ FAILURE:** If `question_id` is still `"cc_details"`, the bug persists

**✅ SUCCESS:** If each response returns a NEW `question_id`

5. **Continue for at least 5 questions** to verify no repetition

---

## DEBUG OUTPUT

When the backend runs, you should see console output like:

```
=== API START DEBUG ===
Session: abc123
Mode: ayush, Stream: ayurveda
Language: en
First question: ayurveda_body_build
========================

=== API RESPOND DEBUG ===
Session: abc123
Mode: ayush, Stream: ayurveda
Current question ID from state: ayurveda_body_build
Answer text: Slim and light...
Answer value: SLIM
Answered questions BEFORE: []
========================

=== CONVERSATION DEBUG ===
Session: abc123
Mode: ayush, Stream: ayurveda
Questionnaire length: 15
Question answered: ayurveda_body_build
Answer value: SLIM
Answered questions: ['ayurveda_body_build']
Total answered: 1/15
Next question: ayurveda_thermal
Is complete: False
Completion %: 7
========================
```

**This confirms:**
- Questionnaire has 15 questions
- Question was marked as answered
- Next question advances correctly
- Completion percentage increases

---

## VERIFICATION CHECKLIST

### AYUSH Progression
- [ ] Conversation starts with `ayurveda_body_build`
- [ ] After answer, returns `ayurveda_thermal` (not complete)
- [ ] Progress continues through all 15 questions
- [ ] `is_complete = false` until question 15
- [ ] After question 15, `is_complete = true`
- [ ] `ayush_profile` is returned on completion
- [ ] `completion_percentage` increases: 7%, 14%, 21%, ..., 100%

### Allopathy Progression
- [ ] Conversation starts with `cc_main`
- [ ] After answer, returns `cc_details`
- [ ] After answer, returns `onset` (NOT `cc_details` again)
- [ ] Each answer advances to a new question
- [ ] No question ID repeats (except for clarifications)
- [ ] `completion_percentage` increases with each answer

### Database Persistence
- [ ] Check database after answering questions
- [ ] `conversation_state` column should contain:
  - `answered_questions`: `["ayurveda_body_build", "ayurveda_thermal", ...]`
  - `current_question_id`: Last answered question ID
  - `answers`: Map of question IDs to values
- [ ] Restart backend, answer continues from correct question

---

## KNOWN LIMITATIONS

1. **Debug logging is enabled** - Remove print statements before production
2. **No transaction rollback** on errors - May leave partial state
3. **Frontend must be rebuilt** - These are backend fixes only
4. **Language/Voice providers** - Still mock (separate task)

---

## NEXT STEPS

After confirming these fixes work:

1. **Remove debug logging** from production build
2. **Update frontend** to properly handle `next_question`
3. **Add progress UI** showing "Question X of Y"
4. **Configure real TTS/STT** providers (Sarvam AI)
5. **Add Tamil translations** verification (already present, just rebuild frontend)
6. **Integration tests** with Pytest

---

## TECHNICAL NOTES

### Why SQLAlchemy Doesn't Detect JSON Mutations

SQLAlchemy tracks changes by comparing object identity:

```python
# This DOES NOT work:
case.conversation_state["key"] = "value"
# SQLAlchemy sees: same dict object → no change

# This DOES work:
new_dict = dict(case.conversation_state)
new_dict["key"] = "value"
case.conversation_state = new_dict
# SQLAlchemy sees: different dict object → mark as changed
```

**Alternative solution:** Use `flag_modified()`:

```python
from sqlalchemy.orm.attributes import flag_modified

case.conversation_state["key"] = "value"
flag_modified(case, "conversation_state")
db.commit()
```

We chose the "reassign entire dict" approach because it's more explicit and doesn't require importing additional SQLAlchemy utilities.

---

**END OF REPORT**
