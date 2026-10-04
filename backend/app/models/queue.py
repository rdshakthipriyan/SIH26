"""
Queue token model for OPD queue management.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class QueueToken(Base, TimestampMixin):
    """
    OPD queue token model.

    Tracks patient position in queue and history status.
    """
    __tablename__ = "queue_tokens"

    # Primary identifier
    token_id = Column(String(50), primary_key=True, index=True)

    # Token information
    token_number = Column(String(20), nullable=False, index=True)
    department = Column(String(100), nullable=False)
    mode = Column(String(20), nullable=True)  # allopathy or ayush

    # Link to patient session
    session_id = Column(String(50), ForeignKey("patient_sessions.session_id"), nullable=True, unique=True, index=True)

    # Queue status
    status = Column(String(30), default="waiting", nullable=False)
    # Statuses: waiting, in_progress, history_pending, history_ready, triage_required, completed

    # Priority
    priority = Column(String(20), default="normal", nullable=False)  # normal, high

    # Red flag indicator
    has_red_flags = Column(Boolean, default=False, nullable=False)

    # Position tracking
    queue_position = Column(Integer, nullable=True)
    called_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Assigned physician
    physician_id = Column(String(50), ForeignKey("physicians.physician_id"), nullable=True)

    # Relationships
    patient_session = relationship("PatientSession", back_populates="queue_token")
