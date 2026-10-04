"""
Session management endpoints for patient and physician authentication.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.patient import PatientSession
from app.models.physician import Physician
from app.models.clinical_case import ClinicalCase
from app.models.queue import QueueToken
from app.schemas.auth import (
    PatientSessionStart,
    PatientSessionResponse,
    PhysicianRegister,
    PhysicianLogin,
    TokenResponse
)

router = APIRouter()


@router.post("/start", response_model=PatientSessionResponse)
async def start_patient_session(
    request: PatientSessionStart,
    db: Session = Depends(get_db)
):
    """Start a new patient session."""
    session_id = str(uuid.uuid4())

    # Generate temp ID if guest mode
    temp_id = None
    if request.is_guest:
        temp_id = f"TEMP-OPD-{str(uuid.uuid4())[:8].upper()}"

    # Create patient session
    patient_session = PatientSession(
        session_id=session_id,
        abha_id=request.abha_id,
        abha_address=request.abha_address,
        is_guest=request.is_guest,
        temp_id=temp_id,
        patient_name=request.patient_name,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender,
        patient_phone=request.patient_phone,
        consent_given=request.consent_given,
        consent_scope=request.consent_scope,
        consent_timestamp=datetime.utcnow() if request.consent_given else None,
        token_number=request.token_number,
        department=request.department,
        mode=request.mode,
        language_code=request.language_code,
        status="active"
    )

    db.add(patient_session)

    # Create clinical case
    case = ClinicalCase(
        case_id=str(uuid.uuid4()),
        session_id=session_id,
        language_code=request.language_code,
        department=request.department,
        mode=request.mode,
        status="in_progress"
    )

    db.add(case)

    # Create queue token if token_number provided
    if request.token_number:
        token = QueueToken(
            token_id=str(uuid.uuid4()),
            token_number=request.token_number,
            department=request.department or "General",
            mode=request.mode,
            session_id=session_id,
            status="history_pending"
        )
        db.add(token)

    db.commit()

    # Create JWT token
    token_data = {
        "sub": session_id,
        "role": "patient",
        "session_id": session_id
    }
    access_token = create_access_token(token_data)

    return PatientSessionResponse(
        session_id=session_id,
        temp_id=temp_id,
        token=access_token,
        token_type="bearer"
    )


@router.post("/physician/register", response_model=TokenResponse)
async def register_physician(
    request: PhysicianRegister,
    db: Session = Depends(get_db)
):
    """Register a new physician."""
    # Check if email already exists
    existing = db.query(Physician).filter(Physician.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    physician_id = str(uuid.uuid4())

    physician = Physician(
        physician_id=physician_id,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        specialization=request.specialization,
        registration_number=request.registration_number,
        department=request.department,
        role="physician",
        is_active=True,
        is_verified=True  # Auto-verify for prototype
    )

    db.add(physician)
    db.commit()

    # Create token
    token_data = {
        "sub": physician_id,
        "role": "physician"
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=physician_id,
        role="physician"
    )


@router.post("/physician/login", response_model=TokenResponse)
async def login_physician(
    request: PhysicianLogin,
    db: Session = Depends(get_db)
):
    """Physician login."""
    physician = db.query(Physician).filter(Physician.email == request.email).first()

    if not physician:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, physician.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not physician.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    # Create token
    token_data = {
        "sub": physician.physician_id,
        "role": "physician"
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=physician.physician_id,
        role="physician"
    )
