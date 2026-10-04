"""Queue management service."""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.queue import QueueToken
from app.models.clinical_case import ClinicalCase


class QueueService:
    """Manage OPD queue tokens."""

    def __init__(self, db: Session):
        self.db = db

    def create_token(
        self,
        token_number: str,
        department: str,
        mode: str = None,
        session_id: str = None
    ) -> QueueToken:
        """Create a new queue token."""
        token = QueueToken(
            token_id=str(uuid.uuid4()),
            token_number=token_number,
            department=department,
            mode=mode,
            session_id=session_id,
            status="waiting",
            priority="normal",
            has_red_flags=False
        )

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def update_from_clinical_case(self, session_id: str) -> None:
        """Update queue status based on clinical case."""
        case = self.db.query(ClinicalCase).filter(
            ClinicalCase.session_id == session_id
        ).first()

        token = self.db.query(QueueToken).filter(
            QueueToken.session_id == session_id
        ).first()

        if not case or not token:
            return

        # Update based on case status
        if case.status == "submitted":
            token.status = "history_ready"

        # Update red flags
        if case.has_red_flags:
            token.has_red_flags = True
            token.priority = "high"
            token.status = "triage_required"

        self.db.commit()

    def get_queue_list(self, department: str = None) -> list:
        """Get queue list."""
        query = self.db.query(QueueToken)

        if department:
            query = query.filter(QueueToken.department == department)

        return query.order_by(QueueToken.created_at).all()
