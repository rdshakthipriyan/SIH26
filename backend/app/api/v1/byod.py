"""
BYOD endpoint for QR code session generation.
"""
import base64
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.byod import BYODSessionCreate, BYODSessionResponse
from app.models.patient import PatientSession
from app.models.clinical_case import ClinicalCase

router = APIRouter()


def generate_qr_code_base64(data: str) -> str:
    """Generate a base64-encoded PNG QR code from string data."""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        # Fallback if qrcode package not installed
        return ""


@router.post("/byod/session", response_model=BYODSessionResponse)
async def create_byod_session(
    request: BYODSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new BYOD session and generate QR code for mobile access."""
    session_id = str(uuid.uuid4())

    # Build session URL (assumes frontend hosted at localhost:5173 for BYOD)
    session_url = f"http://localhost:5173/identity?session={session_id}"

    # Create minimal patient session for BYOD
    patient_session = PatientSession(
        session_id=session_id,
        is_guest=True,
        temp_id=f"BYOD-{str(uuid.uuid4())[:8].upper()}",
        consent_given=True,
        department=request.department or "General",
        mode=request.mode or "allopathy",
        language_code=request.language_code or "en",
        status="byod_active"
    )
    db.add(patient_session)

    # Create associated clinical case
    case = ClinicalCase(
        case_id=str(uuid.uuid4()),
        session_id=session_id,
        language_code=request.language_code or "en",
        department=request.department or "General",
        mode=request.mode or "allopathy",
        status="in_progress"
    )
    db.add(case)
    db.commit()

    # Generate QR code
    qr_base64 = generate_qr_code_base64(session_url)

    return BYODSessionResponse(
        session_id=session_id,
        session_url=session_url,
        qr_code_base64=qr_base64,
        expires_in_seconds=600
    )
