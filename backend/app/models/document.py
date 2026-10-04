"""
Clinical document model for OCR-processed documents.
"""
from sqlalchemy import Column, String, Text, JSON, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ClinicalDocument(Base, TimestampMixin):
    """
    Clinical document model for uploaded and OCR-processed documents.

    Supports prescriptions, lab reports, discharge summaries, etc.
    """
    __tablename__ = "clinical_documents"

    # Primary identifier
    document_id = Column(String(50), primary_key=True, index=True)

    # Link to patient session
    session_id = Column(String(50), ForeignKey("patient_sessions.session_id"), nullable=False, index=True)

    # Document metadata
    document_type = Column(String(50), nullable=False)
    # Types: prescription, lab_report, discharge_summary, medical_report, other

    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size_bytes = Column(Float, nullable=True)

    # OCR results
    ocr_provider = Column(String(50), nullable=True)  # mock, tesseract, vision
    raw_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)  # 0.0 to 1.0

    # Structured clinical entities extracted from OCR
    structured_entities = Column(JSON, nullable=True)
    """
    Structure:
    {
        "medications": [
            {
                "name": str,
                "dosage": str,
                "frequency": str,
                "duration": str,
                "confidence": float
            }
        ],
        "labs": [
            {
                "test_name": str,
                "value": str,
                "unit": str,
                "reference_range": str,
                "abnormal_flag": bool,
                "confidence": float
            }
        ],
        "diagnoses": [
            {
                "diagnosis": str,
                "icd_code": str (if matched),
                "confidence": float
            }
        ],
        "dates": {
            "report_date": str,
            "prescription_date": str,
            "encounter_date": str
        }
    }
    """

    # Processing status
    processing_status = Column(String(30), default="pending", nullable=False)
    # Statuses: pending, processing, completed, failed

    # Warnings and flags
    warnings = Column(JSON, nullable=True)
    """
    List of warnings:
    [
        "Handwriting recognition uncertain",
        "Medication name unclear",
        "Missing dosage information",
        etc.
    ]
    """
    requires_verification = Column(Boolean, default=True, nullable=False)

    # Document date (if extractable)
    document_date = Column(DateTime, nullable=True)

    # Relationships
    patient_session = relationship("PatientSession", back_populates="documents")
