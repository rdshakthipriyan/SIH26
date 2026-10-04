"""
Clinical case model - the main patient intake data.
"""
from sqlalchemy import Column, String, Boolean, JSON, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ClinicalCase(Base, TimestampMixin):
    """
    Clinical case containing all patient intake data.

    Includes clinical history, AYUSH profile, conversation state, and metadata.
    """
    __tablename__ = "clinical_cases"

    # Primary identifier
    case_id = Column(String(50), primary_key=True, index=True)

    # Link to patient session
    session_id = Column(String(50), ForeignKey("patient_sessions.session_id"), nullable=False, unique=True, index=True)

    # Basic information
    language_code = Column(String(10), nullable=True)
    department = Column(String(100), nullable=True)
    mode = Column(String(20), nullable=True)  # allopathy or ayush
    mode_stream = Column(String(30), nullable=True)  # AYUSH stream when mode=ayush

    # Clinical history (Allopathy) - structured JSON
    clinical_history = Column(JSON, nullable=True)
    """
    Structure:
    {
        "chief_complaint": {"value": str, "status": "positive|negative|unknown|not_provided", "provenance": {...}},
        "chief_complaint_details": {...},
        "onset": {...},
        "duration_value": {...},
        "duration_unit": {...},
        "severity": {...},
        "location": {...},
        "character": {...},
        "radiation": {...},
        "progression": {...},
        "associated_symptoms": [...],
        "past_medical_history": [...],
        "past_surgical_history": [...],
        "medications": [...],
        "allergies": [...],
        "family_history": {...},
        "personal_history": {...},
        "review_of_systems": {...}
    }
    """

    # AYUSH profile - structured JSON
    ayush_profile = Column(JSON, nullable=True)
    """
    Structure:
    {
        "prakriti": {
            "vata_score": float,
            "pitta_score": float,
            "kapha_score": float,
            "indicators": [...]
        },
        "agni": {"assessment": str, "indicators": [...]},
        "koshtha": {"assessment": str, "indicators": [...]},
        "ahara_vihara": {...},
        "satva": {...},
        "answers": [...]  # Original patient answers
    }
    """

    # Conversation state - separate from clinical facts
    conversation_state = Column(JSON, nullable=True)
    """
    Structure:
    {
        "current_question_id": str,
        "current_section": str,
        "answered_questions": [str],
        "completion_percentage": float,
        "is_complete": bool
    }
    """

    # Draft answers - temporary storage during conversation
    draft_answers = Column(JSON, nullable=True)

    # Red flags and triage
    red_flags = Column(JSON, nullable=True)
    """
    Structure:
    [
        {
            "flag_id": str,
            "category": str,
            "description": str,
            "detected_at": str,
            "triggers": [...]
        }
    ]
    """
    has_red_flags = Column(Boolean, default=False, nullable=False)
    triage_required = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="normal", nullable=False)  # normal, high

    # Provenance tracking
    provenance = Column(JSON, nullable=True)
    """
    Tracks how each clinical fact was captured:
    {
        "field_name": {
            "input_mode": "voice|touch|voice_edited|ocr",
            "language": str,
            "timestamp": str,
            "raw_transcript": str (if voice),
            "question_id": str
        }
    }
    """

    # Case status
    status = Column(String(20), default="in_progress", nullable=False)
    # Statuses: in_progress, review, submitted, completed

    completion_percentage = Column(Integer, default=0, nullable=False)

    # FHIR metadata
    fhir_bundle_generated = Column(Boolean, default=False, nullable=False)
    fhir_bundle_id = Column(String(100), nullable=True)
    abdm_synced = Column(Boolean, default=False, nullable=False)

    # Clinical summary (generated for doctor)
    clinical_summary = Column(Text, nullable=True)

    # Relationships
    patient_session = relationship("PatientSession", back_populates="clinical_case")
