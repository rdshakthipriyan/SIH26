"""
Authentication and session schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class PhysicianRegister(BaseModel):
    """Physician registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=200)
    specialization: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class PhysicianLogin(BaseModel):
    """Physician login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    session_id: Optional[str] = None


class PatientSessionStart(BaseModel):
    """Patient session start request."""
    abha_id: Optional[str] = Field(None, max_length=100)
    abha_address: Optional[str] = Field(None, max_length=100)
    is_guest: bool = False
    patient_name: Optional[str] = Field(None, max_length=200)
    patient_age: Optional[str] = Field(None, max_length=10)
    patient_gender: Optional[str] = Field(None, max_length=20)
    patient_phone: Optional[str] = Field(None, max_length=20)
    consent_given: bool = False
    consent_scope: Optional[List[str]] = None
    token_number: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    mode: Optional[str] = Field(None, max_length=20)
    stream: Optional[str] = Field(None, max_length=30)  # AYUSH stream: ayurveda | siddha | unani | homoeopathy | yoga_naturopathy
    language_code: Optional[str] = Field(None, max_length=10)

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v and v not in ['allopathy', 'ayush']:
            raise ValueError('mode must be either "allopathy" or "ayush"')
        return v

    @field_validator('stream')
    @classmethod
    def validate_stream(cls, v):
        if v and v not in ['ayurveda', 'siddha', 'unani', 'homoeopathy', 'yoga_naturopathy']:
            raise ValueError('stream must be one of: ayurveda, siddha, unani, homoeopathy, yoga_naturopathy')
        return v


class PatientSessionResponse(BaseModel):
    """Patient session response."""
    session_id: str
    temp_id: Optional[str] = None
    token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True


class PhysicianResponse(BaseModel):
    """Physician information response."""
    physician_id: str
    email: str
    full_name: str
    specialization: Optional[str] = None
    registration_number: Optional[str] = None
    department: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
