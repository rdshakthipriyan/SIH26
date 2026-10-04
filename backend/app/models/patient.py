"""
Patient session model.
"""
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class PatientSession(Base, TimestampMixin):
    """
    Patient session/identity model.

    Supports ABHA authentication and guest mode.
    """
    __tablename__ = "patient_sessions"

    # Primary identifier
    session_id = Column(String(50), primary_key=True, index=True)

    # Identity
    abha_id = Column(String(100), nullable=True, index=True)
    abha_address = Column(String(100), nullable=True, index=True)
    is_guest = Column(Boolean, default=False, nullable=False)
    temp_id = Column(String(50), nullable=True)  # TEMP-OPD-XXXX

    # Patient information
    patient_name = Column(String(200), nullable=True)
    patient_age = Column(String(10), nullable=True)
    patient_gender = Column(String(20), nullable=True)
    patient_phone = Column(String(20), nullable=True)

    # Consent
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_scope = Column(JSON, nullable=True)  # List of consented items
    consent_timestamp = Column(DateTime, nullable=True)

    # Token/Queue
    token_number = Column(String(20), nullable=True, index=True)
    department = Column(String(100), nullable=True)
    mode = Column(String(20), nullable=True)  # allopathy or ayush

    # Language
    language_code = Column(String(10), nullable=True)

    # Session status
    status = Column(String(20), default="active", nullable=False)  # active, completed, abandoned

    # Relationships
    clinical_case = relationship("ClinicalCase", back_populates="patient_session", uselist=False)
    documents = relationship("ClinicalDocument", back_populates="patient_session")
    queue_token = relationship("QueueToken", back_populates="patient_session", uselist=False)
