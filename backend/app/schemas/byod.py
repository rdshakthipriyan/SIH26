"""
BYOD (Bring Your Own Device) schemas for QR code session generation.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BYODSessionCreate(BaseModel):
    """Request to create a BYOD session and generate QR code."""
    mode: Optional[str] = Field(None, max_length=20, description="Initial mode: allopathy or ayush")
    language_code: Optional[str] = Field(None, max_length=10, description="Preferred language code")
    department: Optional[str] = Field(None, max_length=100, description="Department")

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v and v not in ['allopathy', 'ayush']:
            raise ValueError('mode must be either "allopathy" or "ayush"')
        return v


class BYODSessionResponse(BaseModel):
    """Response containing session ID, URL, and base64 QR code."""
    session_id: str
    session_url: str
    qr_code_base64: str
    expires_in_seconds: int = 600

    class Config:
        from_attributes = True
