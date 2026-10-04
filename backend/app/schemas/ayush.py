"""
AYUSH schemas.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AyushAnswer(BaseModel):
    """Patient answer to AYUSH question."""
    question_id: str
    question_text: str | Dict[str, str]  # Accepts both plain string and multi-language dict
    answer: str
    timestamp: str
    language: Optional[str] = None


class PrakritiScore(BaseModel):
    """Prakriti (constitutional type) score."""
    vata_score: float = Field(default=0.0, ge=0.0, le=1.0)
    pitta_score: float = Field(default=0.0, ge=0.0, le=1.0)
    kapha_score: float = Field(default=0.0, ge=0.0, le=1.0)
    indicators: List[Dict[str, Any]] = []
    dominant_type: Optional[str] = None
    confidence: Optional[float] = None


class AgniAssessment(BaseModel):
    """Agni (digestive fire) assessment."""
    assessment: str  # strong, irregular, weak, balanced
    indicators: List[Dict[str, Any]] = []
    confidence: Optional[float] = None


class KoshthaAssessment(BaseModel):
    """Koshtha (bowel pattern) assessment."""
    assessment: str  # constipated, loose, normal
    indicators: List[Dict[str, Any]] = []
    confidence: Optional[float] = None


class AharaViharaProfile(BaseModel):
    """Ahara-Vihara (diet and lifestyle) profile."""
    dietary_pattern: Optional[str] = None
    meal_regularity: Optional[str] = None
    food_preferences: Optional[str] = None
    water_intake: Optional[str] = None
    activity_level: Optional[str] = None
    daily_routine: Optional[str] = None
    sleep_pattern: Optional[str] = None
    indicators: List[Dict[str, Any]] = []


class SatvaAssessment(BaseModel):
    """Satva (mental/emotional constitution) assessment."""
    stress_response: Optional[str] = None
    emotional_resilience: Optional[str] = None
    sleep_quality: Optional[str] = None
    concentration: Optional[str] = None
    indicators: List[Dict[str, Any]] = []


class AyushProfile(BaseModel):
    """Complete AYUSH constitutional profile."""
    prakriti: Optional[PrakritiScore] = None
    agni: Optional[AgniAssessment] = None
    koshtha: Optional[KoshthaAssessment] = None
    ahara_vihara: Optional[AharaViharaProfile] = None
    satva: Optional[SatvaAssessment] = None
    answers: List[AyushAnswer] = []
    completion_percentage: float = 0.0
    is_complete: bool = False


class AyushQuestionRequest(BaseModel):
    """Request next AYUSH question."""
    session_id: str
    language_code: str = Field(..., max_length=10)


class AyushQuestionResponse(BaseModel):
    """AYUSH question response."""
    question_id: Optional[str] = None
    question_text: Optional[Dict[str, str]] = None
    question_type: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    is_complete: bool = False
    completion_percentage: float = 0.0
    audio_url: Optional[str] = None


class AyushAnswerSubmit(BaseModel):
    """Submit AYUSH answer."""
    question_id: str
    answer_text: str = Field(..., max_length=5000)
    input_mode: str = "touch"
    language: Optional[str] = None
    raw_transcript: Optional[str] = None


class AyushProfileResponse(BaseModel):
    """AYUSH profile response."""
    session_id: str
    ayush_profile: Optional[AyushProfile] = None
    status: str
    completion_percentage: float


class AyushIndicator(BaseModel):
    """Individual AYUSH indicator."""
    domain: str  # prakriti_vata, prakriti_pitta, prakriti_kapha, agni, koshtha, etc.
    indicator_type: str
    value: Any
    weight: float = 1.0
    source_question: str
    source_answer: str
