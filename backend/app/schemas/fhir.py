"""
FHIR schemas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class FHIRPatient(BaseModel):
    """FHIR Patient resource."""
    resourceType: str = "Patient"
    id: Optional[str] = None
    identifier: Optional[List[Dict[str, Any]]] = None
    name: Optional[List[Dict[str, Any]]] = None
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    telecom: Optional[List[Dict[str, Any]]] = None


class FHIREncounter(BaseModel):
    """FHIR Encounter resource."""
    resourceType: str = "Encounter"
    id: Optional[str] = None
    status: str = "finished"
    class_: Optional[Dict[str, Any]] = None
    subject: Optional[Dict[str, str]] = None
    period: Optional[Dict[str, str]] = None


class FHIRCondition(BaseModel):
    """FHIR Condition resource."""
    resourceType: str = "Condition"
    id: Optional[str] = None
    subject: Optional[Dict[str, str]] = None
    code: Optional[Dict[str, Any]] = None
    onsetDateTime: Optional[str] = None


class FHIRObservation(BaseModel):
    """FHIR Observation resource."""
    resourceType: str = "Observation"
    id: Optional[str] = None
    status: str = "final"
    code: Optional[Dict[str, Any]] = None
    subject: Optional[Dict[str, str]] = None
    valueString: Optional[str] = None
    valueQuantity: Optional[Dict[str, Any]] = None


class FHIRMedicationStatement(BaseModel):
    """FHIR MedicationStatement resource."""
    resourceType: str = "MedicationStatement"
    id: Optional[str] = None
    status: str = "active"
    medicationCodeableConcept: Optional[Dict[str, Any]] = None
    subject: Optional[Dict[str, str]] = None
    dosage: Optional[List[Dict[str, Any]]] = None


class FHIRAllergyIntolerance(BaseModel):
    """FHIR AllergyIntolerance resource."""
    resourceType: str = "AllergyIntolerance"
    id: Optional[str] = None
    patient: Optional[Dict[str, str]] = None
    code: Optional[Dict[str, Any]] = None
    reaction: Optional[List[Dict[str, Any]]] = None


class FHIRComposition(BaseModel):
    """FHIR Composition resource."""
    resourceType: str = "Composition"
    id: Optional[str] = None
    status: str = "final"
    type: Optional[Dict[str, Any]] = None
    subject: Optional[Dict[str, str]] = None
    date: Optional[str] = None
    author: Optional[List[Dict[str, str]]] = None
    title: str = "Clinical History"
    section: Optional[List[Dict[str, Any]]] = None


class FHIRBundle(BaseModel):
    """FHIR Bundle resource."""
    resourceType: str = "Bundle"
    id: Optional[str] = None
    type: str = "document"
    timestamp: Optional[str] = None
    entry: List[Dict[str, Any]] = []


class FHIRBundleResponse(BaseModel):
    """FHIR bundle response."""
    bundle: FHIRBundle
    generated_at: datetime
    session_id: str
    case_id: str
