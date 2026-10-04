"""
Conversation engine for guided clinical interviews.

Manages the flow of questions and integrates answer extraction.
Supports both Allopathy and AYUSH streams (ayurveda, siddha, unani, homoeopathy, yoga_naturopathy).
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.clinical_case import ClinicalCase
from app.services.conversation.stream_questionnaire import get_questionnaire
from app.services.conversation.answer_extractor import answer_extractor
from app.services.ayush.ayush_engine import AyushEngine


class ConversationEngine:
    """Manages conversational clinical history taking."""

    def __init__(self, db: Session, mode: str = "allopathy", stream: Optional[str] = None):
        """
        Args:
            db: SQLAlchemy session
            mode: 'allopathy' or 'ayush'
            stream: AYUSH stream (required when mode='ayush').
                    One of: 'ayurveda' | 'siddha' | 'unani' | 'homoeopathy' | 'yoga_naturopathy'
        """
        self.db = db
        self.mode = (mode or "allopathy").lower()
        self.stream = (stream or None) if self.mode == "ayush" else None
        self.questionnaire = get_questionnaire(self.mode, self.stream)

    def get_next_question(
        self,
        session_id: str,
        current_conversation_state: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next question based on conversation state.

        Args:
            session_id: Patient session ID
            current_conversation_state: Current state of conversation

        Returns:
            Next question dict or None if complete
        """
        if not current_conversation_state:
            current_conversation_state = {
                "answered_questions": [],
                "current_section": self.questionnaire[0].section if self.questionnaire else "chief_complaint"
            }

        answered = set(current_conversation_state.get("answered_questions", []))
        answers: Dict[str, str] = current_conversation_state.get("answers", {}) or {}

        # Find next unanswered question, evaluating conditional_rules
        for question in self.questionnaire:
            if question.question_id in answered:
                continue

            if question.conditional_rules:
                depends_on = question.conditional_rules.get("depends_on")
                show_if_value = question.conditional_rules.get("show_if_value")
                if depends_on and depends_on not in answered:
                    continue
                if depends_on in answered and show_if_value is not None:
                    if answers.get(depends_on) != show_if_value:
                        continue

            return {
                "question_id": question.question_id,
                "section": question.section,
                "text": question.text,
                "field_type": question.field_type,
                "options": [opt.model_dump() for opt in question.options] if question.options else None,
                "required": question.required,
            }

        return None

    def process_answer(
        self,
        session_id: str,
        question_id: str,
        answer_text: str,
        language: str,
        input_mode: str = "touch",
        raw_transcript: Optional[str] = None,
        confidence: Optional[float] = None,
        answer_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process patient answer and extract clinical facts.

        Args:
            session_id: Patient session ID
            question_id: Question ID being answered
            answer_text: Display text (may be localized); used for clinical extraction
            answer_value: Language-independent internal value (e.g. 'SLIM'). Preferred over answer_text.
            language: Language code
            input_mode: Input mode ('voice' | 'touch' | 'voice_edited')
            raw_transcript: Raw STT transcript if voice
            confidence: STT confidence (0..1)

        Returns:
            Extraction results and next question
        """
        # Extract clinical facts from the display text (handles free-form questions)
        extracted_facts = answer_extractor.extract_from_answer(
            answer_text=answer_text or answer_value or "",
            question_id=question_id,
            language=language,
        )

        # Provenance: capture both display and internal value
        provenance = {
            "input_mode": input_mode,
            "language": language,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_transcript": raw_transcript,
            "question_id": question_id,
            "answer_value": answer_value,
            "answer_text": answer_text,
            "confidence": confidence,
        }

        # Get clinical case
        case = self.db.query(ClinicalCase).filter(
            ClinicalCase.session_id == session_id
        ).first()

        if not case:
            raise ValueError(f"Clinical case not found for session {session_id}")

        # Initialize clinical_history and conversation_state
        if not case.clinical_history:
            case.clinical_history = {}
        if not case.conversation_state:
            case.conversation_state = {"answered_questions": [], "answers": {}, "mode": self.mode, "stream": self.stream}

        # CRITICAL FIX: Work with a copy to avoid SQLAlchemy JSON mutation issues
        conversation_state = dict(case.conversation_state)
        answers = conversation_state.setdefault("answers", {})

        # Store answer with both display and internal value.
        # LANGUAGE-INDEPENDENT SCORING: answer_value (e.g. SLIM) is used for clinical
        # scoring; answer_text (localized) is for display/provenance only.
        answers[question_id] = answer_value or answer_text
        conversation_state["answers"] = answers

        # Also store a raw answer record for provenance
        answer_records: List[Dict[str, Any]] = conversation_state.setdefault("answer_records", [])
        answer_records.append({
            "question_id": question_id,
            "answer_value": answer_value,
            "answer_text": answer_text,
            "raw_transcript": raw_transcript,
            "input_mode": input_mode,
            "language": language,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        })
        conversation_state["answer_records"] = answer_records

        # Update clinical history with extracted facts
        for key, value in extracted_facts.items():
            if isinstance(value, dict) and "value" in value:
                case.clinical_history[key] = {**value, "provenance": provenance}
            else:
                case.clinical_history[key] = {
                    "value": value,
                    "status": "positive",
                    "provenance": provenance,
                }

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

        # CRITICAL FIX: Assign the entire dict to force SQLAlchemy change detection
        case.conversation_state = conversation_state

        # Debug logging
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

        if is_complete:
            case.conversation_state["is_complete"] = True
            case.status = "review"
            self.db.commit()

        # ── AYUSH profile integration ───────────────────────────────────────────
        # Only Ayurveda has a scoring engine; other streams store structured answers only.
        ayush_profile: Optional[Dict[str, Any]] = None
        if self.mode == "ayush" and self.stream == "ayurveda":
            # Build answer list in the format AyushEngine expects.
            # Use the structured answer_records already stored in conversation_state.
            answer_records_for_ayush: List[Dict[str, Any]] = conversation_state.get("answer_records", [])
            ayush_answers = []
            for rec in answer_records_for_ayush:
                # The answer_value (internal option value) is the scoring key.
                # Fall back to answer_text if not provided (e.g. free-text questions).
                normalized = rec.get("answer_value") or rec.get("answer_text") or ""
                ayush_answers.append({
                    "question_id": rec["question_id"],
                    "answer": normalized,           # AyushEngine checks "answer" as fallback
                    "answer_text": rec.get("answer_text", ""),
                    "normalized_value": rec.get("answer_value"),   # explicit key — AyushEngine checks this first
                    "input_mode": rec.get("input_mode", "touch"),
                    "language": rec.get("language", "en"),
                    "timestamp": rec.get("timestamp", ""),
                })

            # Call AyushEngine to calculate the profile
            engine = AyushEngine()
            profile = engine.calculate_profile(ayush_answers)
            # Store profile on the clinical case for persistence and doctor access
            case.ayush_profile = profile
            self.db.commit()
            ayush_profile = profile
        # ── End AYUSH integration ────────────────────────────────────────────────

        return {
            "extracted_facts": extracted_facts,
            "next_question": next_question,
            "is_complete": is_complete,
            "completion_percentage": case.completion_percentage,
            "ayush_profile": ayush_profile,
            "mode": self.mode,
            "stream": self.stream,
        }

    def get_conversation_state(self, session_id: str) -> Dict[str, Any]:
        """Get current conversation state."""
        case = self.db.query(ClinicalCase).filter(
            ClinicalCase.session_id == session_id
        ).first()

        if not case:
            raise ValueError(f"Clinical case not found for session {session_id}")

        return case.conversation_state or {
            "answered_questions": [],
            "answers": {},
            "completion_percentage": 0,
            "is_complete": False,
        }
