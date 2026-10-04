"""
Clinical answer extraction engine.

Extracts structured clinical facts from patient responses.
Supports multiple languages and handles negation properly.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class AnswerExtractor:
    """Extract clinical facts from natural language patient answers."""

    # Symptom patterns (English, Hindi, Tamil, Telugu, Malayalam)
    SYMPTOM_PATTERNS = {
        "chest_pain": [
            r"chest\s+pain", r"pain\s+in\s+chest",
            r"सीने\s*में\s*दर्द", r"छाती\s*में\s*दर्द",
            r"நெஞ்சு\s*வலி", r"நெஞ்சில்\s*வலி",
            r"ఛాతీ\s*నొప్పి", r"రొమ్ము\s*నొప్పి",
            r"നെഞ്ച്\s*വേദന", r"നെഞ്ചിൽ\s*വേദന"
        ],
        "headache": [
            r"headache", r"head\s+pain",
            r"सिरदर्द", r"सिर\s*में\s*दर्द",
            r"தலைவலி", r"தலை\s*வலி",
            r"తలనొప్పి", r"తల\s*నొప్పి",
            r"തലവേദന"
        ],
        "fever": [
            r"fever", r"temperature",
            r"बुखार", r"ज्वर",
            r"காய்ச்சல்", r"ஜுரம்",
            r"జ్వరం", r"కాబోలు",
            r"പനി", r"ജ്വരം"
        ],
        "cough": [
            r"cough", r"coughing",
            r"खांसी",
            r"இருமல்",
            r"దగ్గు",
            r"ചുമ"
        ],
        "breathlessness": [
            r"breathless", r"shortness\s+of\s+breath", r"difficulty\s+breathing",
            r"सांस\s*की\s*तकलीफ", r"सांस\s*फूलना",
            r"மூச்சுத்\s*திணறல்", r"மூச்சு\s*விடுவதில்\s*சிரமம்",
            r"ఊపిరితిత్తు", r"శ్వాస\s*ఇబ్బంది",
            r"ശ്വാസതടസ്സം", r"ശ്വസിക്കാൻ\s*ബുദ്ധിമുട്ട്"
        ],
        "abdominal_pain": [
            r"abdominal\s+pain", r"stomach\s+pain", r"belly\s+pain",
            r"पेट\s*में\s*दर्द", r"पेट\s*दर्द",
            r"வயிற்று\s*வலி", r"வயிற்றில்\s*வலி",
            r"కడుపు\s*నొప్పి", r"కడుపులో\s*నొప్పి",
            r"വയറുവേദന", r"വയറിൽ\s*വേദന"
        ],
        "vomiting": [
            r"vomit", r"vomiting",
            r"उल्टी", r"उलटी",
            r"வாந்தி",
            r"వాంతులు",
            r"ഛർദ്ദി"
        ],
        "diarrhea": [
            r"diarrhea", r"loose\s+stools", r"loose\s+motion",
            r"दस्त", r"लूज\s*मोशन",
            r"வயிற்றுப்போக்கு", r"பேதி",
            r"అతిసారం", r"విరేచనం",
            r"വയറിളക്കം", r"വിരേചനം"
        ],
    }

    # Negation patterns
    NEGATION_PATTERNS = {
        "en": [r"no\s+", r"not\s+", r"don't\s+have", r"do\s+not\s+have", r"without", r"never"],
        "hi": [r"नहीं", r"नही", r"कोई\s+नहीं"],
        "ta": [r"இல்லை", r"இல்ல", r"கிடையாது"],
        "te": [r"లేదు", r"కాదు"],
        "ml": [r"ഇല്ല", r"അല്ല"]
    }

    # Duration patterns
    DURATION_PATTERNS = [
        (r"(\d+)\s*(?:days?|நாட்கள்|రోజులు|ദിവസം|दिन)", "days"),
        (r"(\d+)\s*(?:weeks?|வாரங்கள்|వారాలు|ആഴ്ച|सप्ताह)", "weeks"),
        (r"(\d+)\s*(?:months?|மாதங்கள்|నెలలు|മാസം|महीने)", "months"),
        (r"(\d+)\s*(?:years?|ஆண்டுகள்|సంవత్సరాలు|വർഷം|साल|वर्ष)", "years"),
        (r"(\d+)\s*(?:hours?|மணி|గంటలు|മണിക്കൂർ|घंटे)", "hours"),
    ]

    # Severity patterns
    SEVERITY_PATTERNS = [
        r"(\d+)\s*(?:out\s+of\s+10|/10|scale)",
        r"(\d+)\s*(?:தி்ல்|లో|ൽ)\s*10",
        r"severity\s*[:\-]?\s*(\d+)",
    ]

    def extract_from_answer(
        self,
        answer_text: str,
        question_id: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Extract clinical facts from patient answer.

        Args:
            answer_text: Patient's answer text
            question_id: ID of the question being answered
            language: Language code

        Returns:
            Dictionary of extracted facts
        """
        answer_lower = answer_text.lower()
        extracted = {}

        # Check for negation first
        is_negated = self._detect_negation(answer_lower, language)

        # Extract based on question type
        if question_id == "cc_main":
            # Chief complaint
            symptom = self._extract_symptom(answer_lower)
            if symptom:
                extracted["chief_complaint"] = {
                    "value": symptom,
                    "status": "negative" if is_negated else "positive"
                }

        elif question_id in ["onset", "duration"]:
            # Duration extraction
            duration = self._extract_duration(answer_lower)
            if duration:
                extracted["duration_value"] = duration[0]
                extracted["duration_unit"] = duration[1]

        elif question_id == "severity":
            # Severity extraction
            severity = self._extract_severity(answer_lower)
            if severity is not None:
                extracted["severity"] = {
                    "value": severity,
                    "status": "positive"
                }

        elif question_id == "location":
            extracted["location"] = {
                "value": answer_text,
                "status": "positive"
            }

        elif question_id == "character":
            extracted["character"] = {
                "value": answer_text,
                "status": "positive"
            }

        elif question_id == "pmh_any":
            # Past medical history flag
            if "yes" in answer_lower or "हाँ" in answer_lower or "ஆம்" in answer_lower:
                extracted["pmh_flag"] = "yes"
            elif "no" in answer_lower or "नहीं" in answer_lower or "இல்லை" in answer_lower:
                extracted["pmh_flag"] = "no"

        elif question_id == "psh_any":
            # Past surgical history flag
            if "yes" in answer_lower or "हाँ" in answer_lower or "ஆம்" in answer_lower:
                extracted["psh_flag"] = "yes"
            elif "no" in answer_lower or "नहीं" in answer_lower or "இல்லை" in answer_lower:
                extracted["psh_flag"] = "no"

        elif question_id == "allergy_any":
            # Allergy flag
            if "yes" in answer_lower or "हाँ" in answer_lower or "ஆம்" in answer_lower:
                extracted["allergy_flag"] = "yes"
            elif "no" in answer_lower or "नहीं" in answer_lower or "இல்லை" in answer_lower:
                extracted["allergy_flag"] = "no"
            elif "don't know" in answer_lower or "தெரியாது" in answer_lower:
                extracted["allergy_flag"] = "unknown"

        # Also try to extract multi-fact information
        # For example, "chest pain for 2 days, severity 7"
        all_symptoms = self._extract_all_symptoms(answer_lower)
        for symptom in all_symptoms:
            if symptom not in extracted:
                extracted[f"symptom_{symptom}"] = {
                    "value": symptom,
                    "status": "negative" if is_negated else "positive"
                }

        # Extract duration from any answer
        duration = self._extract_duration(answer_lower)
        if duration and "duration_value" not in extracted:
            extracted["duration_value"] = duration[0]
            extracted["duration_unit"] = duration[1]

        # Extract severity from any answer
        severity = self._extract_severity(answer_lower)
        if severity is not None and "severity" not in extracted:
            extracted["severity"] = {
                "value": severity,
                "status": "positive"
            }

        return extracted

    def _detect_negation(self, text: str, language: str) -> bool:
        """Detect if the statement is negated."""
        # Check language-specific negation patterns
        patterns = self.NEGATION_PATTERNS.get(language, [])
        patterns.extend(self.NEGATION_PATTERNS.get("en", []))  # Always check English too

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _extract_symptom(self, text: str) -> Optional[str]:
        """Extract primary symptom from text."""
        for symptom, patterns in self.SYMPTOM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return symptom
        return None

    def _extract_all_symptoms(self, text: str) -> List[str]:
        """Extract all symptoms mentioned in text."""
        symptoms = []
        for symptom, patterns in self.SYMPTOM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    symptoms.append(symptom)
                    break
        return symptoms

    def _extract_duration(self, text: str) -> Optional[Tuple[int, str]]:
        """Extract duration value and unit."""
        for pattern, unit in self.DURATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                return (value, unit)
        return None

    def _extract_severity(self, text: str) -> Optional[int]:
        """Extract severity rating (0-10)."""
        for pattern in self.SEVERITY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                severity = int(match.group(1))
                if 0 <= severity <= 10:
                    return severity
        return None


# Global extractor instance
answer_extractor = AnswerExtractor()
