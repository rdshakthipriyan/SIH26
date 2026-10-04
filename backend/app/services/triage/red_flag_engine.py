"""
Red flag detection engine.

Detects dangerous clinical patterns requiring urgent attention.
Respects negation - negated symptoms don't trigger flags.
"""
from typing import Dict, Any, List, Optional
import re


class RedFlagEngine:
    """Detect red flag conditions requiring urgent triage."""

    RED_FLAG_RULES = [
        {
            "flag_id": "chest_pain_emergency",
            "category": "cardiovascular",
            "description": "Severe chest pain pattern suggesting cardiac emergency",
            "triggers": [
                {"field": "chief_complaint", "value": "chest_pain", "status": "positive"},
                {"field": "severity", "min_value": 7}
            ],
            "message": "Severe chest pain detected. Urgent evaluation required."
        },
        {
            "flag_id": "acute_breathlessness",
            "category": "respiratory",
            "description": "Acute severe breathlessness",
            "triggers": [
                {"field": "chief_complaint", "value": "breathlessness", "status": "positive"},
                {"field": "severity", "min_value": 7}
            ],
            "message": "Severe breathlessness detected. Urgent evaluation required."
        },
        {
            "flag_id": "stroke_pattern",
            "category": "neurological",
            "description": "Possible stroke symptoms",
            "triggers": [
                {"field": "associated_symptoms", "contains_any": ["weakness", "numbness", "speech_difficulty", "vision_loss"]}
            ],
            "message": "Stroke-like symptoms detected. Immediate evaluation required."
        },
        {
            "flag_id": "severe_abdominal_pain",
            "category": "gastrointestinal",
            "description": "Severe abdominal pain with concerning features",
            "triggers": [
                {"field": "chief_complaint", "value": "abdominal_pain", "status": "positive"},
                {"field": "severity", "min_value": 8}
            ],
            "message": "Severe abdominal pain detected. Urgent evaluation required."
        },
        {
            "flag_id": "gi_bleeding",
            "category": "gastrointestinal",
            "description": "Gastrointestinal bleeding",
            "triggers": [
                {"field": "associated_symptoms", "contains_any": ["blood_in_vomit", "blood_in_stool", "black_stool"]}
            ],
            "message": "Possible GI bleeding detected. Urgent evaluation required."
        },
        {
            "flag_id": "suicidal_ideation",
            "category": "psychiatric",
            "description": "Suicidal thoughts or self-harm risk",
            "triggers": [
                {"field": "any_text", "contains_keywords": ["suicide", "kill myself", "end my life", "self harm"]}
            ],
            "message": "Mental health crisis detected. Immediate psychiatric evaluation required."
        }
    ]

    def check_red_flags(self, clinical_history: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check clinical history for red flags.

        Args:
            clinical_history: Clinical history dictionary

        Returns:
            List of detected red flags
        """
        detected_flags = []

        for rule in self.RED_FLAG_RULES:
            if self._check_rule(clinical_history, rule):
                detected_flags.append({
                    "flag_id": rule["flag_id"],
                    "category": rule["category"],
                    "description": rule["description"],
                    "message": rule["message"],
                    "detected_at": None,  # Will be set by caller
                    "triggers": rule["triggers"]
                })

        return detected_flags

    def _check_rule(self, clinical_history: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if a single rule is satisfied."""
        triggers = rule["triggers"]

        for trigger in triggers:
            if not self._check_trigger(clinical_history, trigger):
                return False  # All triggers must be satisfied

        return True

    def _check_trigger(self, clinical_history: Dict[str, Any], trigger: Dict[str, Any]) -> bool:
        """Check if a single trigger condition is met."""
        field = trigger.get("field")

        if field == "any_text":
            # Check keywords in any text field
            keywords = trigger.get("contains_keywords", [])
            return self._check_keywords_in_history(clinical_history, keywords)

        field_data = clinical_history.get(field)

        if not field_data:
            return False

        # Check status (NEVER trigger on negative/unknown/not_provided)
        if isinstance(field_data, dict):
            status = field_data.get("status", "not_provided")

            # CRITICAL: Only positive findings can trigger red flags
            if status != "positive":
                return False

            value = field_data.get("value")
        else:
            value = field_data

        # Check value match
        if "value" in trigger:
            if value != trigger["value"]:
                return False

        # Check minimum value
        if "min_value" in trigger:
            try:
                if isinstance(value, (int, float)):
                    if value < trigger["min_value"]:
                        return False
                elif isinstance(value, dict):
                    # Handle nested clinical fact structure: {value, status, ...}
                    nested_value = value.get("value")
                    if isinstance(nested_value, (int, float)):
                        if nested_value < trigger["min_value"]:
                            return False
                    else:
                        return False
                else:
                    return False
            except (ValueError, TypeError):
                return False

        # Check contains_any
        if "contains_any" in trigger:
            keywords = trigger["contains_any"]
            if isinstance(value, str):
                value_lower = value.lower()
                if not any(keyword in value_lower for keyword in keywords):
                    return False
            elif isinstance(value, list):
                if not any(keyword in str(item).lower() for keyword in keywords for item in value):
                    return False
            else:
                return False

        return True

    def _check_keywords_in_history(self, clinical_history: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if any keywords appear in clinical history text."""
        # Convert history to searchable text
        def extract_text(data):
            if isinstance(data, dict):
                if data.get("status") != "positive":
                    return ""  # Don't search in negated content
                return str(data.get("value", ""))
            elif isinstance(data, str):
                return data
            elif isinstance(data, list):
                return " ".join(str(item) for item in data)
            return str(data)

        all_text = " ".join(extract_text(v) for v in clinical_history.values()).lower()

        return any(keyword.lower() in all_text for keyword in keywords)


# Global red flag engine instance
red_flag_engine = RedFlagEngine()
