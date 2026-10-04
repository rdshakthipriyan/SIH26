"""
Text-to-Speech schemas.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Text-to-speech request."""
    text: str = Field(..., max_length=2000)
    language_code: str = Field(..., max_length=10)
    voice: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    """Text-to-speech response."""
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    duration_seconds: Optional[float] = None
    provider: str
    language_code: str
    status: Literal["success", "fallback", "unavailable"] = "success"
    message: Optional[str] = None
