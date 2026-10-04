"""
Queue and token management schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class QueueTokenCreate(BaseModel):
    """Create queue token request."""
    token_number: str = Field(..., max_length=20)
    department: str = Field(..., max_length=100)
    mode: Optional[str] = Field(None, max_length=20)
    session_id: Optional[str] = None


class QueueTokenUpdate(BaseModel):
    """Update queue token."""
    status: Optional[str] = None
    priority: Optional[str] = None
    has_red_flags: Optional[bool] = None
    physician_id: Optional[str] = None


class QueueTokenResponse(BaseModel):
    """Queue token response."""
    token_id: str
    token_number: str
    department: str
    mode: Optional[str] = None
    session_id: Optional[str] = None
    status: str
    priority: str
    has_red_flags: bool
    queue_position: Optional[int] = None
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    physician_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueListResponse(BaseModel):
    """Queue list response."""
    tokens: List[QueueTokenResponse]
    total: int
    waiting: int
    in_progress: int
    completed: int
