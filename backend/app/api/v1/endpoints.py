"""AYUSH, OCR, Queue, Doctor, and FHIR endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import require_patient, require_physician, verify_session_ownership
from app.models.clinical_case import ClinicalCase
from app.models.document import ClinicalDocument
from app.models.queue import QueueToken
from app.schemas.ayush import AyushAnswerSubmit, AyushProfileResponse
from app.schemas.ocr import OCRUploadResponse, OCRDocumentListResponse, OCRDocumentDetailResponse
from app.schemas.queue import QueueListResponse, QueueTokenResponse
from app.schemas.fhir import FHIRBundleResponse
from app.services.ayush.ayush_engine import AyushEngine, get_ayush_questionnaire
from app.services.ocr.ocr_provider import get_ocr_provider
from app.services.ocr.clinical_entity_extractor import entity_extractor
from app.services.fhir.fhir_builder import fhir_builder

ayush_router = APIRouter()
ocr_router = APIRouter()
queue_router = APIRouter()
doctor_router = APIRouter()
fhir_router = APIRouter()


# AYUSH Endpoints
@ayush_router.post("/cases/{session_id}/ayush/answer")
async def submit_ayush_answer(
    session_id: str,
    answer: AyushAnswerSubmit,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Submit AYUSH answer."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    # Initialize ayush_profile if needed
    if not case.ayush_profile:
        case.ayush_profile = {"answers": []}

    # Look up question_text from the central questionnaire definition
    questionnaire = get_ayush_questionnaire()
    question_text = None
    matched_question = next(
        (q for q in questionnaire if q.question_id == answer.question_id),
        None
    )
    if matched_question is not None:
        question_text = matched_question.text

    # Add answer with question_text from questionnaire
    case.ayush_profile["answers"].append({
        "question_id": answer.question_id,
        "question_text": question_text,
        "answer": answer.answer_text,
        "answer_text": answer.answer_text,
        "timestamp": datetime.utcnow().isoformat(),
        "input_mode": answer.input_mode,
        "language": answer.language
    })

    # Calculate profile
    engine = AyushEngine()
    profile = engine.calculate_profile(case.ayush_profile["answers"])
    case.ayush_profile = profile

    db.commit()

    # Get next question
    answered_ids = [a["question_id"] for a in case.ayush_profile["answers"]]
    next_q = engine.get_next_question(answered_ids)

    return {"next_question": next_q, "profile": profile}


@ayush_router.get("/cases/{session_id}/ayush/profile", response_model=AyushProfileResponse)
async def get_ayush_profile(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Get AYUSH profile."""
    verify_session_ownership(session_id, current_user)

    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")

    return AyushProfileResponse(
        session_id=session_id,
        ayush_profile=case.ayush_profile,
        status=case.status,
        completion_percentage=case.ayush_profile.get("completion_percentage", 0) if case.ayush_profile else 0
    )


# OCR Endpoints
@ocr_router.post("/cases/{session_id}/ocr", response_model=OCRUploadResponse)
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    document_type: str = "prescription",
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Upload and process document with OCR."""
    verify_session_ownership(session_id, current_user)

    # Read file
    file_bytes = await file.read()

    # Create document record
    doc_id = str(uuid.uuid4())
    document = ClinicalDocument(
        document_id=doc_id,
        session_id=session_id,
        document_type=document_type,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_size_bytes=len(file_bytes),
        processing_status="processing"
    )

    db.add(document)
    db.commit()

    # Process with OCR
    try:
        ocr_provider = get_ocr_provider()
        ocr_result = await ocr_provider.extract_text(file_bytes)

        document.raw_text = ocr_result["raw_text"]
        document.ocr_confidence = ocr_result["confidence"]
        document.ocr_provider = ocr_result["provider"]

        # Extract clinical entities
        entities = entity_extractor.extract_entities(
            document.raw_text,
            document.ocr_confidence
        )
        document.structured_entities = entities.model_dump()

        # Generate warnings
        warnings = []
        if document.ocr_confidence < 0.7:
            warnings.append("Low OCR confidence - verify extracted information")
        if document.ocr_provider == "tesseract" and "handwritten" in document_type.lower():
            warnings.append("Handwritten text recognition may be inaccurate")

        document.warnings = warnings
        document.processing_status = "completed"

        db.commit()

        return OCRUploadResponse(
            document_id=doc_id,
            document_type=document_type,
            original_filename=file.filename,
            processing_status="completed"
        )

    except Exception as e:
        document.processing_status = "failed"
        document.warnings = [str(e)]
        db.commit()
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {e}")


@ocr_router.get("/cases/{session_id}/ocr")
async def list_documents(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """List documents for a session."""
    verify_session_ownership(session_id, current_user)

    documents = db.query(ClinicalDocument).filter(
        ClinicalDocument.session_id == session_id
    ).all()

    return {"documents": documents, "total": len(documents)}


# Queue Endpoints
@queue_router.get("/queue", response_model=QueueListResponse)
async def get_queue(
    department: str = None,
    db: Session = Depends(get_db)
):
    """Get queue list."""
    query = db.query(QueueToken)
    if department:
        query = query.filter(QueueToken.department == department)

    tokens = query.order_by(QueueToken.created_at).all()

    waiting = sum(1 for t in tokens if t.status == "waiting")
    in_progress = sum(1 for t in tokens if t.status == "in_progress")
    completed = sum(1 for t in tokens if t.status == "completed")

    return QueueListResponse(
        tokens=[QueueTokenResponse.model_validate(t) for t in tokens],
        total=len(tokens),
        waiting=waiting,
        in_progress=in_progress,
        completed=completed
    )


# Doctor Endpoints
@doctor_router.get("/doctor/cases")
async def get_doctor_cases(
    current_user: Dict[str, Any] = Depends(require_physician),
    db: Session = Depends(get_db)
):
    """Get all cases for doctor dashboard."""
    cases = db.query(ClinicalCase).filter(
        ClinicalCase.status.in_(["submitted", "review", "completed"])
    ).all()

    result = []
    for case in cases:
        patient = db.query(PatientSession).filter(
            PatientSession.session_id == case.session_id
        ).first()

        result.append({
            "case_id": case.case_id,
            "session_id": case.session_id,
            "patient_name": patient.patient_name if patient else "Unknown",
            "department": case.department,
            "mode": case.mode,
            "language": case.language_code,
            "status": case.status,
            "has_red_flags": case.has_red_flags,
            "priority": case.priority,
            "created_at": case.created_at,
            "updated_at": case.updated_at
        })

    return {"cases": result, "total": len(result)}


@doctor_router.get("/doctor/cases/{session_id}/summary")
async def get_case_summary(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_physician),
    db: Session = Depends(get_db)
):
    """Get detailed case summary for doctor."""
    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    patient = db.query(PatientSession).filter(
        PatientSession.session_id == session_id
    ).first()

    documents = db.query(ClinicalDocument).filter(
        ClinicalDocument.session_id == session_id
    ).all()

    return {
        "case": case,
        "patient": patient,
        "clinical_history": case.clinical_history,
        "ayush_profile": case.ayush_profile,
        "red_flags": case.red_flags,
        "provenance": case.provenance,
        "documents": documents
    }


# FHIR Endpoints
@fhir_router.get("/cases/{session_id}/fhir", response_model=FHIRBundleResponse)
async def get_fhir_bundle(
    session_id: str,
    current_user: Dict[str, Any] = Depends(require_physician),
    db: Session = Depends(get_db)
):
    """Generate FHIR bundle."""
    case = db.query(ClinicalCase).filter(ClinicalCase.session_id == session_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    patient = db.query(PatientSession).filter(
        PatientSession.session_id == session_id
    ).first()

    bundle = fhir_builder.build_bundle(
        session_id=session_id,
        case_id=case.case_id,
        patient_data=patient.__dict__ if patient else {},
        clinical_history=case.clinical_history,
        ayush_profile=case.ayush_profile
    )

    return FHIRBundleResponse(
        bundle=bundle,
        generated_at=datetime.utcnow(),
        session_id=session_id,
        case_id=case.case_id
    )


# Fix import
from app.models.patient import PatientSession
