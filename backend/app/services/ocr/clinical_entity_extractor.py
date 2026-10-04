"""Clinical entity extraction from OCR text."""
import re
from typing import Dict, Any, List
from app.schemas.ocr import MedicationExtraction, LabExtraction, DiagnosisExtraction, StructuredEntities


class ClinicalEntityExtractor:
    """Extract structured clinical entities from OCR text."""

    MEDICATION_PATTERNS = [
        r"(?:tablet|tab|cap|capsule|syrup|injection|mg|gm)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"([A-Za-z]+(?:cillin|mycin|prazole|formin|pressin|olol|pine|statin|ide))",
    ]

    def extract_entities(self, raw_text: str, confidence: float) -> StructuredEntities:
        """Extract structured entities from raw OCR text."""
        medications = self._extract_medications(raw_text, confidence)
        labs = self._extract_labs(raw_text, confidence)
        diagnoses = self._extract_diagnoses(raw_text, confidence)

        return StructuredEntities(
            medications=medications,
            labs=labs,
            diagnoses=diagnoses
        )

    def _extract_medications(self, text: str, confidence: float) -> List[MedicationExtraction]:
        """Extract medication information."""
        medications = []
        lines = text.split('\n')

        for line in lines:
            line_lower = line.lower()

            # Look for medication keywords
            if any(keyword in line_lower for keyword in ['tablet', 'tab', 'cap', 'mg', 'syrup', 'injection']):
                # Extract medication name (simplified)
                words = line.split()
                med_name = None

                for i, word in enumerate(words):
                    if any(drug in word.lower() for drug in ['formin', 'pressin', 'cillin', 'mycin', 'prazole']):
                        med_name = word
                        break

                if med_name:
                    # Try to extract dosage
                    dosage_match = re.search(r'(\d+\s*(?:mg|gm|ml))', line, re.IGNORECASE)
                    dosage = dosage_match.group(1) if dosage_match else "UNKNOWN"

                    # Try to extract frequency
                    frequency = "UNKNOWN"
                    if any(freq in line_lower for freq in ['once', 'twice', 'thrice', 'daily', 'bd', 'tid']):
                        if 'twice' in line_lower or 'bd' in line_lower:
                            frequency = "Twice daily"
                        elif 'once' in line_lower or 'od' in line_lower:
                            frequency = "Once daily"
                        elif 'thrice' in line_lower or 'tid' in line_lower:
                            frequency = "Three times daily"

                    medications.append(MedicationExtraction(
                        name=med_name,
                        dosage=dosage,
                        frequency=frequency,
                        duration="UNKNOWN",
                        confidence=confidence * 0.8  # Lower confidence for extracted details
                    ))

        return medications

    def _extract_labs(self, text: str, confidence: float) -> List[LabExtraction]:
        """Extract lab results."""
        labs = []
        lines = text.split('\n')

        lab_keywords = ['glucose', 'hba1c', 'hemoglobin', 'creatinine', 'cholesterol']

        for line in lines:
            line_lower = line.lower()

            for lab_name in lab_keywords:
                if lab_name in line_lower:
                    # Try to extract value
                    value_match = re.search(r'(\d+\.?\d*)', line)
                    if value_match:
                        labs.append(LabExtraction(
                            test_name=lab_name.capitalize(),
                            value=value_match.group(1),
                            unit="UNKNOWN",
                            confidence=confidence * 0.7
                        ))
                        break

        return labs

    def _extract_diagnoses(self, text: str, confidence: float) -> List[DiagnosisExtraction]:
        """Extract diagnoses."""
        diagnoses = []
        lines = text.split('\n')

        diagnosis_keywords = ['diagnosis', 'impression', 'assessment']

        for i, line in enumerate(lines):
            line_lower = line.lower()

            for keyword in diagnosis_keywords:
                if keyword in line_lower:
                    # Next line might contain the diagnosis
                    if i + 1 < len(lines):
                        diagnosis_text = lines[i + 1].strip()
                        if diagnosis_text:
                            diagnoses.append(DiagnosisExtraction(
                                diagnosis=diagnosis_text,
                                confidence=confidence * 0.6
                            ))
                    break

        return diagnoses


entity_extractor = ClinicalEntityExtractor()
