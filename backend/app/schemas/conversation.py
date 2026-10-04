"""
Conversation engine schemas.
"""
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    """Option for a question."""
    option_id: str
    text: Dict[str, str]  # language_code -> text
    value: Any


class Question(BaseModel):
    """Clinical questionnaire question."""
    question_id: str
    section: str
    text: Dict[str, str]  # language_code -> text
    field_type: Literal["text", "single_choice", "multiple_choice", "number", "date", "boolean"]
    options: Optional[List[QuestionOption]] = None
    required: bool = True
    conditional_rules: Optional[Dict[str, Any]] = None
    extraction_hints: Optional[List[str]] = None
    clinical_concept_id: Optional[str] = None


class QuestionnaireSchema(BaseModel):
    """Complete questionnaire schema."""
    questionnaire_id: str
    version: str
    mode: Literal["allopathy", "ayush"]
    sections: List[str]
    questions: List[Question]


class ConversationStartRequest(BaseModel):
    """Start conversation request."""
    language_code: str = Field(..., max_length=10)
    mode: Literal["allopathy", "ayush"] = "allopathy"
    stream: Optional[str] = Field(
        None,
        max_length=30,
        description="AYUSH stream when mode='ayush': ayurveda | siddha | unani | homoeopathy | yoga_naturopathy"
    )


class ConversationStartResponse(BaseModel):
    """Start conversation response."""
    conversation_id: str
    session_id: str
    mode: str
    stream: Optional[str] = None
    language_code: str
    first_question: Optional[Question] = None
    audio_url: Optional[str] = None


class ConversationResponse(BaseModel):
    """Respond to conversation question."""
    answer_text: str = Field(..., max_length=5000)
    input_mode: Literal["voice", "touch", "voice_edited"] = "touch"
    raw_transcript: Optional[str] = None
    language: Optional[str] = None
    answer_value: Optional[str] = Field(
        None,
        description="Language-independent internal option value (e.g. 'SLIM', 'HEAVY'). "
                    "For AYUSH mode single-choice questions, this should be the stable option value "
                    "selected by the patient, not the displayed/translated text."
    )
    question_id: Optional[str] = Field(
        None,
        description="Explicit question ID — useful when the frontend knows which question is being answered "
                    "rather than relying on server-side conversation state."
    )


class NextQuestionResponse(BaseModel):
    """Next question in conversation."""
    question: Optional[Question] = None
    next_question: Optional[Question] = None
    is_complete: bool = False
    completion_percentage: float = 0.0
    extracted_facts: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None
    # AYUSH profile (only populated for mode == 'ayush' when an answer is processed)
    ayush_profile: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    stream: Optional[str] = None


class ConversationState(BaseModel):
    """Current conversation state."""
    session_id: str
    current_question_id: Optional[str] = None
    current_section: Optional[str] = None
    answered_questions: List[str] = []
    completion_percentage: float = 0.0
    is_complete: bool = False
    mode: str
    language_code: str


class TranscriptConfirmRequest(BaseModel):
    """Confirm or edit transcript."""
    transcript: str = Field(..., max_length=5000)
    is_edited: bool = False
    language: Optional[str] = None
