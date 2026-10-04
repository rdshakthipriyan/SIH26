"""Clinical history and conversation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import require_patient, verify_session_ownership
from app.models.clinical_case import ClinicalCase
from app.models.patient import PatientSession
from app.schemas.clinical_history import ClinicalHistoryResponse, DraftAnswerUpdate
from app.schemas.conversation import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationResponse,
    NextQuestionResponse,
    ConversationState
)
from app.schemas.languages import get_supported_languages, LanguageListResponse
from app.services.conversation.conversation_engine import ConversationEngine
from app.services.conversation.speech import get_speech_provider
from app.services.conversation.tts import get_tts_provider
from app.services.conversation.questionnaire_schema import get_questionnaire_schema
from app.services.triage.red_flag_engine import red_flag_engine
from app.services.queue.queue_engine import QueueService
from datetime import datetime

router = APIRouter()


@router.get("/languages", response_model=LanguageListResponse)
async def get_languages():
    """Get supported languages."""
    return get_supported_languages()


@router.get("/questionnaire/schema")
async def get_questionnaire():
    """Get questionnaire schema."""
    return get_questionnaire_schema()


@router.get("/cases/{session_id}/history", response_model=ClinicalHistoryResponse)
async def get_clinical_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Get clinical history for a session."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    return ClinicalHistoryResponse(
        case_id=case.case_id,
        session_id=case.session_id,
        clinical_history=case.clinical_history,
        status=case.status,
        completion_percentage=case.completion_percentage,
        has_red_flags=case.has_red_flags,
        updated_at=case.updated_at
    )


@router.post("/cases/{session_id}/conversation/start", response_model=ConversationStartResponse)
async def start_conversation(
    session_id: str,
    request: ConversationStartRequest,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Start conversation."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    # Update language, mode and stream on the clinical case
    case.language_code = request.language_code
    case.mode = request.mode
    if request.stream:
        case.mode_stream = request.stream  # store selected AYUSH stream separately
    db.commit()

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

    return ConversationStartResponse(
        conversation_id=case.case_id,
        session_id=session_id,
        mode=request.mode,
        stream=getattr(case, 'mode_stream', request.stream) or None,
        language_code=request.language_code,
        first_question=first_question
    )


@router.post("/cases/{session_id}/conversation/respond", response_model=NextQuestionResponse)
async def respond_to_conversation(
    session_id: str,
    response: ConversationResponse,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Respond to conversation question."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

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

    # CRITICAL: Validate question_id if provided by frontend
    # Reject stale question IDs to prevent data corruption
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

    # Debug logging
    print(f"\n=== API RESPOND DEBUG ===")
    print(f"Session: {session_id}")
    print(f"Mode: {case.mode}, Stream: {getattr(case, 'mode_stream', None)}")
    print(f"Current question ID from state: {current_question_id}")
    print(f"Question ID from request: {response.question_id if hasattr(response, 'question_id') else 'NOT PROVIDED'}")
    print(f"Answer text: {response.answer_text[:50] if response.answer_text else 'NONE'}...")
    print(f"Answer value: {response.answer_value}")
    print(f"Answered questions BEFORE: {conv_state.get('answered_questions', [])}")
    print(f"Question ID validation: {'PASSED' if not response.question_id or response.question_id == current_question_id else 'REJECTED'}")
    print(f"========================\n")

    # Get engine from stored case mode/stream
    engine = ConversationEngine(db, mode=case.mode or "allopathy", stream=getattr(case, 'mode_stream', None))
    result = engine.process_answer(
        session_id=session_id,
        question_id=current_question_id,
        answer_text=response.answer_text,
        language=case.language_code or "en",
        input_mode=response.input_mode,
        raw_transcript=response.raw_transcript,
        answer_value=response.answer_value,
    )

    # Check red flags
    db.refresh(case)
    if case.clinical_history:
        red_flags = red_flag_engine.check_red_flags(case.clinical_history)
        if red_flags:
            for flag in red_flags:
                flag["detected_at"] = datetime.utcnow().isoformat()

            case.red_flags = red_flags
            case.has_red_flags = True
            case.triage_required = True
            case.priority = "high"
            db.commit()

            # Update queue
            queue_service = QueueService(db)
            queue_service.update_from_clinical_case(session_id)

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


@router.get("/cases/{session_id}/conversation/state", response_model=ConversationState)
async def get_conversation_state(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Get conversation state."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    conv_state = case.conversation_state or {}

    return ConversationState(
        session_id=session_id,
        current_question_id=conv_state.get("current_question_id"),
        current_section=conv_state.get("current_section"),
        answered_questions=conv_state.get("answered_questions", []),
        completion_percentage=conv_state.get("completion_percentage", 0.0),
        is_complete=conv_state.get("is_complete", False),
        mode=case.mode or "allopathy",
        language_code=case.language_code or "en"
    )


@router.post("/cases/{session_id}/voice/transcribe")
async def transcribe_voice(
    session_id: str,
    audio: UploadFile = File(...),
    language_code: str = "en",
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Transcribe voice input."""
    verify_session_ownership(session_id, current_user)

    # Read audio file
    audio_bytes = await audio.read()

    # Transcribe
    speech_provider = get_speech_provider()
    try:
        result = await speech_provider.transcribe(
            audio_file=audio_bytes,
            language_code=language_code,
            mime_type=audio.content_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/cases/{session_id}/conversation/speak")
async def text_to_speech(
    session_id: str,
    text: str,
    language_code: str = "en",
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Convert text to speech."""
    verify_session_ownership(session_id, current_user)

    tts_provider = get_tts_provider()
    try:
        result = await tts_provider.synthesize(
            text=text,
            language_code=language_code
        )
        return result
    except Exception as e:
        return {
            "audio_base64": None,
            "status": "unavailable",
            "message": str(e)
        }


@router.post("/cases/{session_id}/history/submit")
async def submit_clinical_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Submit clinical history for review."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    case.status = "submitted"
    db.commit()

    # Update queue
    queue_service = QueueService(db)
    queue_service.update_from_clinical_case(session_id)

    return {"message": "Clinical history submitted successfully", "case_id": case.case_id}
