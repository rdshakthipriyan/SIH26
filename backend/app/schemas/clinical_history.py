"""
Clinical history schemas.
"""
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Provenance(BaseModel):
    """Provenance information for a clinical fact."""
    input_mode: Literal["voice", "touch", "voice_edited", "ocr"]
    language: Optional[str] = None
    timestamp: datetime
    raw_transcript: Optional[str] = None
    question_id: Optional[str] = None
    source: Optional[str] = None


class ClinicalFact(BaseModel):
    """A clinical fact with value and status."""
    value: Any
    status: Literal["positive", "negative", "unknown", "not_provided"] = "not_provided"
    provenance: Optional[Provenance] = None


class SurgicalHistoryEntry(BaseModel):
    """Surgical history entry."""
    procedure: str
    year: str
    details: str = "N/A"


class MedicationEntry(BaseModel):
    """Medication entry."""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    indication: Optional[str] = None


class AllergyEntry(BaseModel):
    """Allergy entry."""
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[str] = None


class ClinicalHistoryData(BaseModel):
    """Complete clinical history data structure."""
    chief_complaint: Optional[ClinicalFact] = None
    chief_complaint_details: Optional[ClinicalFact] = None

    # HPI - History of Present Illness
    onset: Optional[ClinicalFact] = None
    duration_value: Optional[ClinicalFact] = None
    duration_unit: Optional[ClinicalFact] = None
    severity: Optional[ClinicalFact] = None
    location: Optional[ClinicalFact] = None
    character: Optional[ClinicalFact] = None
    radiation: Optional[ClinicalFact] = None
    progression: Optional[ClinicalFact] = None
    associated_symptoms: List[ClinicalFact] = []

    # Past history
    past_medical_history: List[ClinicalFact] = []
    past_surgical_history: List[SurgicalHistoryEntry] = []
    medications: List[MedicationEntry] = []
    allergies: List[AllergyEntry] = []

    # Family and personal history
    family_history: Optional[ClinicalFact] = None
    personal_history: Optional[Dict[str, ClinicalFact]] = None

    # Review of systems
    review_of_systems: Optional[Dict[str, ClinicalFact]] = None


class DraftAnswerUpdate(BaseModel):
    """Update draft answer for a specific field."""
    field_name: str = Field(..., max_length=100)
    value: Any
    input_mode: Literal["voice", "touch", "voice_edited", "ocr"] = "touch"
    language: Optional[str] = None
    raw_transcript: Optional[str] = None


class ClinicalHistoryUpdate(BaseModel):
    """Update clinical history."""
    clinical_history: Dict[str, Any]


class ClinicalHistoryResponse(BaseModel):
    """Clinical history response."""
    case_id: str
    session_id: str
    clinical_history: Optional[Dict[str, Any]] = None
    status: str
    completion_percentage: int
    has_red_flags: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class TouchAnswerSubmit(BaseModel):
    """Submit answer via touch interface."""
    question_id: str = Field(..., max_length=100)
    answer_value: Any
    language: Optional[str] = None

    @field_validator('answer_value')
    @classmethod
    def validate_answer(cls, v, info):
        """Validate answer value based on question type."""
        # Basic validation - specific validation happens in service layer
        return v


class SeverityUpdate(BaseModel):
    """Update severity rating."""
    severity: int = Field(..., ge=0, le=10)

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Severity must be between 0 and 10')
        return v
