TRACE OUTPUT — SAVE FROM PREVIOUS TURN
No files modified. No new code executed. This is the saved result of the trace.

ACTUAL EXECUTION PATH (verified by reading source):
First answer (appetite = HIGH):
  POST /cases/{sid}/ayush/answer (endpoints.py:30)
  -> case.ayush_profile["answers"].append({question_id:"ayush_appetite", answer_text:"HIGH"})
  -> AyushEngine.calculate_profile() -> _normalize_answer() -> "strong"
  -> _assess_agni() -> assessment="strong", confidence=1.0
  -> case.ayush_profile = full profile dict (line 72)
  -> return {next_question, profile}

Second answer (same endpoint, accumulates):
  Same path. Profile recalculated over full answers list.
  answer_extractor (conversation_engine path) NOT involved.

PROFILE FORMAT PRODUCED (from ayush_engine.py calculate_profile line 611):
{
  "prakriti": {"vata_score":..., "pitta_score":..., "kapha_score":..., "dominant_type":..., "confidence":..., "raw_scores":..., "indicators":[...]},
  "agni": {"assessment":"strong"/"irregular"/"weak"/"mandagni", "confidence":..., "indicators":[...]},
  "koshtha": {"assessment":"normal"/"constipated"/"loose", "confidence":..., "indicators":[...]},
  "satva": {"stress_response":"...", "sleep_quality":"...", "confidence":..., "indicators":[...]},
  "ahara_vihara": {"activity_level":"high"/"medium"/"low", "confidence":..., "indicators":[...]},
  "answers": [...], "is_complete": bool, "completion_percentage": int
}

VERDICT FOR EACH QUESTION:
- Ayurveda answer storage: WORKING (via /ayush/answer endpoint, case.ayush_profile JSON)
- Answer extraction: WORKING (_normalize_answer maps text->value)
- Ayurvedic scoring: WORKING (AyushEngine.calculate_profile executes)
- Prakriti calculation: WORKING (_score_prakriti produces vata/pitta/kapha)
- Agni calculation: WORKING (_assess_agni produces assessment+confidence)
- Koshtha calculation: WORKING (_assess_koshtha produces assessment+confidence)
- Satva calculation: WORKING (_assess_satva produces stress/sleep+confidence)
- Ahara-Vihara calculation: WORKING (_assess_ahara_vihara produces activity+confidence)
- Frontend profile display: NOT CONNECTED (no component reads ayush_profile)
- Backend profile API: WORKING (GET /cases/{sid}/ayush/profile returns profile)

NOTE: conversation_engine.process_answer does NOT call AyushEngine. The two paths are separate.
