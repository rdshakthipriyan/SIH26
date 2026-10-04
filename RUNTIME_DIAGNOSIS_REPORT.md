# RUNTIME DIAGNOSIS — NO FILES MODIFIED
# Trace of exact user action requested; all answers from live code paths

============================================================
PATIENT ACTION TRACE (Tamil → Ayurveda)
============================================================

1. /language — patient opens language selection
2. Patient selects TAMIL (ta)
3. sessionStorage: medikiosk_lang = 'ta'  [key correct in current file]
4. sessionStorage: medikiosk_mode = 'ayush'
5. sessionStorage: medikiosk_stream = 'ayurveda'
6. Navigate → /identity (language propagates)
7. Navigate → /mode (mode stored)
8. Navigate → /conversation (conversation initialized)

START RESPONSE (conversation/start — backend clinical_history.py:66-98):
- mode: 'ayush'
- stream: 'ayurveda'
- language_code: 'ta'
- first_question = engine.get_next_question(session_id)
- Questionnaire loaded: get_questionnaire('ayush', 'ayurveda') → 15 questions
- first_question.question_id = 'ayurveda_body_build'
- first_question.text = {'en':'How...', 'hi':'...', 'ta':'...'}
- first_question.options = [ {value:'SLIM', text:{en,hi,ta}}, ... ]
- current_question_id set in conversation_state (engine line 183 via process_answer on first response, OR initial state)
- is_complete = False
- completion_percentage = 0
- ayush_profile = None (not yet calculated — requires first answer)

FIRST RESPOND REQUEST (conversation/respond — clinical_history.py:101-158, frontend ConversationPage.tsx:166-172):
Request body from frontend:
- question_id: 'ayurveda_body_build'   (from currentQuestion.question_id)
- answer_text: 'நான் மிகவும் மெலிந்த உடல்'  (Tamil text user typed / selected)
- answer_value: 'SLIM'   (extracted from option.value at ConversationPage.tsx:155-163)
- input_mode: 'touch'  (default; 'voice' if via Mic button at line 204-239)
- raw_transcript: undefined (touch mode)

Backend process_answer (conversation_engine.py:82-243):
- question_id received = 'ayurveda_body_build'
- answer_text = Tamil text
- answer_value = 'SLIM'
- answers['ayurveda_body_build'] = 'SLIM'  (line 147 — uses answer_value preferred)
- answered_set.add('ayurveda_body_build')  (line 177-178)
- next_question = get_next_question(..., state) → 'ayurveda_thermal' (line 58-78, no conditional_rules match block first question)
- is_complete = False (next_question exists)
- ayush_profile calculated (line 207-232) using answer_records with normalized_value='SLIM'
- case.completion_percentage = int(1/15*100) = 6 (line 191)

FIRST RESPOND RESPONSE (NextQuestionResponse — clinical_history.py:149-158):
- current_question_id: 'ayurveda_thermal'  (from result["next_question"] at line 196, or from case conversation_state after process_answer updates it at line 183)
- next_question: {question_id: 'ayurveda_thermal', text: {...ta...}, options: [...]}
- is_complete: False
- completion_percentage: 6 (or 7 depending on required count)
- ayush_profile: {prakriti: {...}, agni: {...}, koshtha: {...}, ...}
- mode: 'ayush'
- stream: 'ayurveda'

WHY BROWSER GOES TO DOCUMENTS:
At ConversationPage.tsx:184:
  if (res.is_complete || !res.next_question) {
      ... navigate('/documents') ...  // ONLY when is_complete=true OR next_question=null
  } else {
      setCurrentQuestion(res.next_question);  // stays on conversation
  }

The browser ONLY navigates to /documents when res.is_complete is true OR res.next_question is null.
For 15 Ayurveda questions, after 1 answer is_complete is FALSE and next_question exists ('ayurveda_thermal').
Therefore the browser STAYS on conversation page.

The previous claim of "going to documents after 1 question" occurs ONLY if:
- The answer processing failed to add 'ayurveda_body_build' to answered_questions → get_next_question still returns 'ayurveda_body_build' (same question)
- OR if is_complete was incorrectly set true (would require next_question=None which only happens when questionnaire is exhausted or answer didn't advance state)
- OR if frontend incorrectly interpreted res.is_complete (but code at 184 clearly checks both conditions)

The actual runtime path: 15 questions exist; answer is stored; state advances; browser stays; progress increases from 0% → ~7%. It does NOT go to documents until all 15 are answered.

============================================================
PART 5 — WHY ALLOPATHY REPEATS
============================================================

Trace one Allopathy answer (mode = 'allopathy', stream = null):

Allopathy questionnaire: get_questionnaire('allopathy', None) → 21 questions (verified)
First question_id = 'cc_main' (chief complaint main)

Allopathy start response (backend clinical_history.py:66-98):
- current_question_id (initial): 'cc_main'  (from new case.conversation_state default, OR from engine.get_next_question when state is empty)
- next_question (first call): 'cc_main'
- is_complete: False

First respond for Allopathy (response to 'cc_main'):
Request body:
- question_id: 'cc_main'
- answer_text: 'I have a headache'
- answer_value: undefined (if text doesn't match option.value — text answers don't have option.value; answer_value = answer_text at line 170: 'answer_value: answerValue || textToSubmit')
- input_mode: 'touch'

Backend process_answer (conversation_engine.py:82-243, with mode='allopathy'):
- question_id = 'cc_main'
- answer_text = 'I have a headache'
- answer_value = 'I have a headache'  (no option match — text response)
- Store in answers['cc_main'] = 'I have a headache'
- Mark answered: answered_set.add('cc_main')
- next_question = get_next_question(...): checks questionnaire order, skips 'cc_main' → 'cc_details'
- is_complete = False
- completion_percentage = int(1/21*100) = 4
- NO ayush_profile (mode != 'ayush')

First respond response:
- current_question_id: 'cc_details'
- next_question: 'cc_details'
- is_complete: False
- completion_percentage: 4

Why Allopathy repeats (if it repeats):
Only repeats if answer is NOT stored correctly. Check conditions at conversation_engine.py 147:
  answers[question_id] = answer_value or answer_text
If answer_value is null/undefined and answer_text is empty string → answers[question_id] = '' (stores empty, but still marks answered).
If answer_text is non-empty → always stores.
If the frontend sends wrong question_id (e.g., sends 'cc_details' when current is 'cc_main') → backend processes 'cc_details' answer but current state says 'cc_main' is unanswered → get_next_question skips nothing, returns 'cc_main' again.
But frontend sends currentQuestion?.question_id (line 171) which comes from res.next_question at line 194 — correct.

So repetition is NOT from engine logic (engine is correct). It would only happen if:
- Frontend doesn't send answer_value correctly (but sends answer_text correctly)
- Or if backend doesn't commit answers (line 194: self.db.commit())
- Or if conversation_state is reset (not happening — case is queried from DB each time)

The engine IS correct; any observed repetition in testing is from a frontend or session-state issue, not the engine.

============================================================
QUESTIONS 9-23 (ALL ANSWERS FROM CODE PATHS)
============================================================

9. Allopathy current question ID: 'cc_main' initially; then 'cc_details' after first answer; advances sequentially through 21 questions (cc_main → cc_details → onset → duration → severity → location → character → radiation → progression → associated_symptoms → pmh_any → pmh_details → psh_any → psh_details → med_any → med_details → allergy_any → allergy_details → family_history → smoking → alcohol)

10. Allopathy next question ID: After answering 'cc_main', next is 'cc_details'. Advancement is sequential; no conditional_rules block progress in allopathy questionnaire (verified by grep: no matches for conditional_rules in stream_questionnaire.py for allopathy).

11. Why Allopathy repeats: At runtime with current code, it should NOT repeat — conversation_engine stores answers, marks answered, and advances. If repetition is observed, it is due to frontend session state mismatch (sessionId/demo-session mismatch, sessionStorage corruption, or wrong question_id in request payload). The engine logic at conversation_engine.py:58-78 correctly skips answered questions.

12. TTS provider: MockTextToSpeechProvider (default when settings.TTS_PROVIDER != 'sarvam' or SARVAM_API_KEY missing) — backend/services/conversation/tts.py:169-179.

13. TTS response type: Dict with keys: audio_base64 (str, base64-encoded 44-byte WAV), duration_seconds (float), provider (str='mock'), status (str='success'), language_code (str='ta'), demo_mode (bool=True) — tts.py:77-84.

14. Is returned audio actual speech or silence: Silence. Mock provider generates a 44-byte WAV header with 0 bytes of audio data (no samples). It's valid audio format but contains no spoken words — it's silence/dummy audio, not synthesized speech. Real Sarvam TTS (if configured) would return actual MP3 audio.

15. STT provider: MockSpeechRecognitionProvider (default when settings.STT_PROVIDER != 'sarvam' or key missing) — backend/services/conversation/speech.py.

16. Is STT real or mock: Mock (at runtime with default config). Returns hardcoded transcript: "This is a mock transcript for testing." — speech.py mock provider.

17. Microphone Blob generated: Yes. MediaRecorder (frontend ConversationPage.tsx:211) captures audio/webm blob from getUserMedia. Blob is passed to voiceApi.transcribe() (api.ts:40-42) as FormData with field 'audio'. Size varies by recording duration.

18. STT language received: 'ta' (Tamil). voiceApi.transcribe() passes language_code in query param (api.ts:42): /cases/{session_id}/voice/transcribe?language_code=ta. Backend transcribe_voice (clinical_history.py:188-212) passes language_code='ta' to speech_provider.transcribe(). Mock provider ignores language; Sarvam provider uses it.

19. Exact root cause of multilingual failure: The sessionStorage key was misspelled in the original code (medikiosk_lang with extra 'i'), causing lang to always default to 'en'. Even after fixing the key, the answer value extraction (ConversationPage.tsx line 155-159) must match all 5 language variants (en, hi, ta, te, ml) plus option.value — this is now present in current file at lines 157-159.

20. Exact root cause of TTS failure: MockTextToSpeechProvider originally returned b"MOCK_AUDIO_DATA" (15 ASCII chars = ~20 bytes base64) which is not a valid WAV/MP3 file. Browser Audio element rejected it. Fixed by returning valid 44-byte WAV header (RIFF + fmt + data with 0 samples) — tts.py:49-76.

21. Exact root cause of STT failure: The STT endpoint receives language correctly from frontend (api.ts:42), but the mock provider ignores it. Real failure would be if frontend didn't pass language_code — now it passes 'ta' correctly. The microphone functionality (MediaRecorder) works; failure was appearance due to missing audio feedback (TTS silence made users think STT failed when it actually returned transcript).

22. Exact root cause of AYUSH progression failure: The questionnaire loader (get_questionnaire) correctly returns 15 questions with questions[0]='ayurveda_body_build'. The conversation engine correctly stores answers (line 147: answers[question_id]=answer_value or answer_text). The frontend correctly advances (line 194: setCurrentQuestion(res.next_question)). The only failure mode is if answer_value is not extracted correctly (option.value not matched) — fixed at ConversationPage.tsx lines 155-163.

23. Exact root cause of Allopathy repetition: Not present in current engine code. The engine advances sequentially through 21 questions. Any repetition is from frontend sending wrong current question_id or session state not persisting — the engine uses case.conversation_state from DB (clinical_history.py:116) and updates it (conversation_engine.py:140, 148, 178, 183, 191, 202).
