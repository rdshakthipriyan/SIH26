"""
OCR and document processing schemas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MedicationExtraction(BaseModel):
    """Extracted medication from OCR."""
    name: str
    dosage: Optional[str] = "UNKNOWN"
    frequency: Optional[str] = "UNKNOWN"
    duration: Optional[str] = "UNKNOWN"
    confidence: Optional[float] = None


class LabExtraction(BaseModel):
    """Extracted lab result from OCR."""
    test_name: str
    value: Optional[str] = "UNKNOWN"
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[bool] = None
    confidence: Optional[float] = None


class DiagnosisExtraction(BaseModel):
    """Extracted diagnosis from OCR."""
    diagnosis: str
    icd_code: Optional[str] = None
    confidence: Optional[float] = None


class DocumentDates(BaseModel):
    """Extracted dates from document."""
    report_date: Optional[str] = None
    prescription_date: Optional[str] = None
    encounter_date: Optional[str] = None


class StructuredEntities(BaseModel):
    """Structured clinical entities extracted from document."""
    medications: List[MedicationExtraction] = []
    labs: List[LabExtraction] = []
    diagnoses: List[DiagnosisExtraction] = []
    dates: Optional[DocumentDates] = None


class OCRUploadResponse(BaseModel):
    """OCR upload response."""
    document_id: str
    document_type: str
    original_filename: Optional[str] = None
    processing_status: str
    message: Optional[str] = None


class OCRProcessingResult(BaseModel):
    """OCR processing result."""
    document_id: str
    session_id: str
    document_type: str
    ocr_provider: str
    raw_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    structured_entities: Optional[StructuredEntities] = None
    processing_status: str
    warnings: List[str] = []
    requires_verification: bool = True
    document_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OCRDocumentListResponse(BaseModel):
    """List of OCR documents."""
    documents: List[OCRProcessingResult]
    total: int


class OCRDocumentDetailResponse(BaseModel):
    """Detailed OCR document response."""
    document_id: str
    session_id: str
    document_type: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[float] = None
    ocr_provider: str
    raw_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    structured_entities: Optional[StructuredEntities] = None
    processing_status: str
    warnings: List[str] = []
    requires_verification: bool = True
    document_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
