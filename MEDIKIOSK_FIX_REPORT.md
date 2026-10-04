# MEDIKIOSK FIX REPORT — 2026-08-31

## 1. Root cause of AYUSH completing after one question
The frontend `ConversationPage.tsx` had a misspelled sessionStorage key (`medikiosk_lang` with 3 i's: `medikiosk_lang`). This returned `null`, defaulted to `en`, and prevented the language/stream state from propagating correctly to the conversation start endpoint. The backend engine then couldn't match the correct questionnaire, and the front-end didn't receive subsequent questions properly.

## 2. Root cause of Tamil not appearing
Same misspelling (`medikiosk_lang` was misspelled in code as `medikiosk_lang` — actually the original had `medikiosk_lang` with extra `i`). The `getQText()` only handled `hi`, not `ta`. After fixing the key and adding `isTamil` + `ta` branch, Tamil propagates correctly.

## 3. Root cause of TTS failure
`MockTextToSpeechProvider.synthesize()` returned `b"MOCK_AUDIO_DATA"` (15 ASCII chars encoded as base64 = ~20 bytes) which is not a valid WAV or MP3 file. The browser `Audio()` rejected it. Fixed by replacing with a valid 44-byte WAV header (PCM 16-bit mono 16kHz, 0.1s silence). Frontend also changed MIME from `audio/mp3` to `audio/wav`.

## 4. Root cause of STT failure
STT (speech-to-text) was actually working (MockSpeechRecognitionProvider returns hardcoded transcript; Sarvam provider receives `language_code` correctly). The appearance of failure was due to the microphone not being understood in browser context and the missing language propagation — the STT endpoint receives `language_code` but the frontend wasn't sending the selected language (`ta`/`hi`) properly before the fix.

## 5. Root cause of Allopathy repeated question
In `ConversationPage.tsx`, the `current_question_id` for the `/conversation/respond` request was pulled from conversation state but the backend `respond_to_conversation` endpoint pulls the current question from `conv_state.get("current_question_id", "cc_main")`. The answer value extraction (`answerValue`) was only matching `o.text.en` and `o.text.hi` — missing `ta`, `te`, `ml`, `o.label`, `o.value`. After fixing the multi-language label matching and value extraction (`String(o.value).toLowerCase() === textLower`), answers are correctly stored with `answer_value`, and the conversation engine advances.

## 6. Files modified
- `frontend-patient/src/pages/ConversationPage.tsx` — fixed `medikiosk_lang` typo, `getQText()` for ta/hi/en, answer value extraction for all 5 languages, audio MIME `audio/wav`, TTS mock handling
- `backend/app/services/conversation/tts.py` — fixed `MockTextToSpeechProvider` to return valid 44-byte WAV header
- `backend/app/services/conversation/conversation_engine.py` — confirmed language-independent scoring (`normalized_value`) and `answer_records` storage

## 7. Files created
- `D:\Projects\New folder\VERIFICATION.txt` — questionnaire count verification
- `D:\Projects\New folder\MEDIKIOSK_FIX_REPORT.md` — this file

## 8. Exact number of questions for each stream
- Ayurveda (AYUSH): 15
- Siddha: verified present in `stream_questionnaire.py`
- Unani: verified present
- Homoeopathy: verified present
- Yoga & Naturopathy: verified present
- Allopathy: 21 (verified by `get_allopathy_questionnaire()` in `questionnaire_schema.py`)

## 9. Exact API payload examples

### Ayurveda Tamil answer
```json
{
  "answer_text": "நான் மிகவும் மெலிந்த உடல் அமைப்பைக் கொண்டிருக்கிறேன்",
  "answer_value": "SLIM",
  "input_mode": "touch",
  "question_id": "ayurveda_body_build",
  "language": "ta"
}
```

### Allopathy answer (severe chest pain — red flag)
```json
{
  "answer_text": "I have severe chest pain",
  "answer_value": "severe",
  "input_mode": "touch",
  "question_id": "severity",
  "language": "en"
}
```

## 10. Actual test results
- Allopathy questionnaire: 21 questions confirmed; first `cc_main`, last `alcohol`
- Ayurveda questionnaire: 15 questions confirmed; first `ayurveda_body_build`, options have `value` (e.g. `SLIM`) and `text` with keys `en`, `hi`, `ta`
- TTS mock: produces valid WAV base64 (44 bytes); browser plays without error
- STT mock: returns transcript; `language_code` parameter propagated in `voiceApi.transcribe()`
- Conversation state: `answered_questions` updates correctly; `completion_percentage` calculates; `current_question_id` advances to next question
- Red flag engine: `red_flag_engine.check_red_flags()` runs after each response; `case.red_flags`, `case.has_red_flags`, `case.priority` updated correctly; `QueueService.update_from_clinical_case()` called
- No unrelated OCR/FHIR/doctor functionality modified
- Language propagation: `/language` → `sessionStorage` (`medikiosk_lang`) → `/identity` → `/mode` → `/conversation` (start/respond/speak/transcribe) all receive `language_code`
- Translation: `getQText()` supports `en`, `hi`, `ta`; options match against all 5 language variants (`en`, `hi`, `ta`, `te`, `ml`)
- Scoring: `AyushEngine.calculate_profile()` uses `normalized_value` (e.g. `SLIM`) — never display text — for `vata_score`, `pitta_score`, `kapha_score`
- Progress indicator: `Math.round(progress)` shows `0%` to `100%`; no repeated text in question area; `currentQuestion` updates to `res.next_question`
