TRACED EXECUTION PATH (actual source inspection, no edits made)
====================================================================
First answer trace (appetite = HIGH, via ayush_engine path):
  Endpoint: POST /cases/{sid}/ayush/answer (endpoints.py:30)
  → reads case.ayush_profile (JSON, line 45)
  → append answer {question_id, answer_text, timestamp, input_mode, language}
  → engine = AyushEngine(); profile = engine.calculate_profile(case.ayush_profile["answers"])
  → calculate_profile (line 572) loops answers, builds normalized_answers via _normalize_answer
  → _assess_agni sees qid "ayush_appetite", normalized="strong" (HIGH maps to strong via patterns line 249)
  → assessment = "strong", confidence = 1.0 (line 428)
  → profile written to case.ayush_profile (line 72)
  → returned in response: {next_question, profile}

Second answer trace: same endpoint, same path. Profile is recalculated from full answers list including first.

ACTUAL DATA TRANSFORMATIONS (from source):
  - Ayurveda answer storage: case.ayush_profile JSON (endpoints.py:45-72)
  - Answer extraction: _normalize_answer() in ayush_engine.py (line 215) maps text -> option value
  - Ayurvedic scoring: AyushEngine.calculate_profile() -> _score_prakriti / _assess_agni / _assess_koshtha / _assess_satva / _assess_ahara_vihara
  - Prakriti: raw_scores vata/pitta/kapha from SCORING_RULES (line 331) + normalization (line 387)
  - Agni: _assess_agni (line 413) from appetite/digestion -> strong/irregular/weak/mandagni
  - Koshtha: _assess_koshtha (line 461) from bowel -> normal/constipated/loose
  - Satva: _assess_satva (line 500) from sleep/stress -> stress_response + sleep_quality
  - Ahara-Vihara: _assess_ahara_vihara (line 542) from activity -> high/medium/low

PROFILE OUTPUT FORMAT (actual return from calculate_profile, line 611-628):
  {
    "prakriti": { "vata_score": ..., "pitta_score": ..., "kapha_score": ..., "dominant_type": ..., "confidence": ..., "raw_scores": ..., "indicators": ... },
    "agni": { "assessment": ..., "confidence": ..., "indicators": ... },
    "koshtha": { "assessment": ..., "confidence": ..., "indicators": ... },
    "satva": { "stress_response": ..., "sleep_quality": ..., "confidence": ..., "indicators": ... },
    "ahara_vihara": { "activity_level": ..., "confidence": ..., "indicators": ... },
    "answers": [...],
    "is_complete": bool, "completion_percentage": int
  }

FRONTEND PROFILE DISPLAY: NOT CONNECTED
  - No component in frontend references ayush_profile or calculates profile.
  - ConversationPage only stores currentQuestion, progress, redFlags — never reads profile.
  - /ayush/profile endpoint exists (endpoints.py:83) but frontend does not call it.
  - No profile display in App.tsx routes.

BACKEND PROFILE API: WORKING (separate endpoint, not wired to conversation)
  - GET /cases/{session_id}/ayush/profile returns AyushProfileResponse (line 83-101)
  - Uses case.ayush_profile which was computed by submit_ayush_answer

NOT CONNECTED TO CONVERSATION ENGINE:
  - conversation_engine.process_answer (conversation_engine.py:81) never calls AyushEngine or references ayush_profile.
  - conversation_engine stores answers in conversation_state["answers"] (line 145), not case.ayush_profile.
  - The two paths (conversation/ vs ayush/) are independent.

VERDICT (actual source, not intended):
- Ayurveda answer storage: WORKING (via /ayush/answer endpoint)
- Answer extraction: WORKING (via _normalize_answer + option lookup)
- Ayurvedic scoring: WORKING (AyushEngine.calculate_profile exists and executes)
- Prakriti calculation: WORKING (_score_prakriti produces vata/pitta/kapha scores)
- Agni calculation: WORKING (_assess_agni produces assessment + confidence)
- Koshtha calculation: WORKING (_assess_koshtha produces assessment + confidence)
- Satva calculation: WORKING (_assess_satva produces stress/sleep + confidence)
- Ahara-Vihara calculation: WORKING (_assess_ahara_vihara produces activity + confidence)
- Frontend profile display: NOT CONNECTED
- Backend profile API: WORKING (separate endpoint, not integrated with conversation flow)
