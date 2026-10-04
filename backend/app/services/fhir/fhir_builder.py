"""FHIR bundle builder for MediKiosk."""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class FHIRBuilder:
    """Build FHIR-compliant bundles from clinical cases."""

    def build_bundle(
        self,
        session_id: str,
        case_id: str,
        patient_data: Dict[str, Any],
        clinical_history: Optional[Dict[str, Any]] = None,
        ayush_profile: Optional[Dict[str, Any]] = None,
        documents: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Build FHIR Bundle."""
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "document",
            "timestamp": timestamp,
            "entry": []
        }

        # Patient resource
        patient_resource = self._build_patient_resource(patient_data)
        bundle["entry"].append({"resource": patient_resource})

        # Encounter resource
        encounter_resource = self._build_encounter_resource(session_id)
        bundle["entry"].append({"resource": encounter_resource})

        # Composition resource
        composition_resource = self._build_composition_resource(
            session_id, clinical_history, ayush_profile
        )
        bundle["entry"].append({"resource": composition_resource})

        # Clinical observations
        if clinical_history:
            observations = self._build_observations(clinical_history, session_id)
            for obs in observations:
                bundle["entry"].append({"resource": obs})

        return bundle

    def _build_patient_resource(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build FHIR Patient resource."""
        patient = {
            "resourceType": "Patient",
            "id": str(uuid.uuid4()),
            "identifier": []
        }

        if patient_data.get("abha_id"):
            patient["identifier"].append({
                "system": "https://healthid.ndhm.gov.in",
                "value": patient_data["abha_id"]
            })

        if patient_data.get("patient_name"):
            patient["name"] = [{
                "text": patient_data["patient_name"]
            }]

        if patient_data.get("patient_gender"):
            patient["gender"] = patient_data["patient_gender"].lower()

        return patient

    def _build_encounter_resource(self, session_id: str) -> Dict[str, Any]:
        """Build FHIR Encounter resource."""
        return {
            "resourceType": "Encounter",
            "id": str(uuid.uuid4()),
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "period": {
                "start": datetime.utcnow().isoformat() + "Z"
            }
        }

    def _build_composition_resource(
        self,
        session_id: str,
        clinical_history: Optional[Dict[str, Any]],
        ayush_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build FHIR Composition resource."""
        composition = {
            "resourceType": "Composition",
            "id": str(uuid.uuid4()),
            "status": "final",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "11488-4",
                    "display": "Consult note"
                }]
            },
            "date": datetime.utcnow().isoformat() + "Z",
            "title": "Clinical History",
            "section": []
        }

        if clinical_history:
            composition["section"].append({
                "title": "Chief Complaint",
                "text": {
                    "status": "generated",
                    "div": f"<div>{self._extract_text_summary(clinical_history)}</div>"
                }
            })

        if ayush_profile:
            composition["section"].append({
                "title": "AYUSH Constitutional Assessment",
                "text": {
                    "status": "generated",
                    "div": f"<div>AYUSH Profile - AI/ML generated indicators</div>"
                }
            })

        return composition

    def _build_observations(
        self,
        clinical_history: Dict[str, Any],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Build FHIR Observation resources."""
        observations = []

        # Severity observation
        if clinical_history.get("severity"):
            severity_data = clinical_history["severity"]
            if isinstance(severity_data, dict) and severity_data.get("status") == "positive":
                observations.append({
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "text": "Pain severity"
                    },
                    "valueQuantity": {
                        "value": severity_data.get("value", 0),
                        "unit": "score",
                        "system": "http://unitsofmeasure.org",
                        "code": "{score}"
                    }
                })

        return observations

    def _extract_text_summary(self, clinical_history: Dict[str, Any]) -> str:
        """Extract text summary from clinical history."""
        summary_parts = []

        if clinical_history.get("chief_complaint"):
            cc = clinical_history["chief_complaint"]
            if isinstance(cc, dict):
                summary_parts.append(f"Chief Complaint: {cc.get('value', 'N/A')}")

        return " ".join(summary_parts)


fhir_builder = FHIRBuilder()
