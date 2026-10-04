"""
AYUSH adaptive questionnaire engine.

Patient-friendly questions that internally map to Ayurvedic concepts.
"""
from typing import Dict, Any, List, Optional
from app.schemas.conversation import Question, QuestionOption


AYUSH_QUESTIONS = [
    Question(
        question_id="ayush_body_build",
        section="prakriti",
        text={
            "en": "How would you describe your body build?",
            "hi": "आप अपने शरीर की बनावट का वर्णन कैसे करेंगे?",
            "ta": "உங்கள் உடல் அமைப்பை எவ்வாறு விவரிப்பீர்கள்?",
            "te": "మీ శరీర నిర్మాణాన్ని ఎలా వివరిస్తార్?",
            "ml": "നിങ്ങളുടെ ശരീര നിർമ്മാണം എങ്ങനെ വിവരിക്കും?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="build_thin", text={"en": "Thin/lean", "hi": "पतला/दुबला", "ta": "மெலிந்த", "te": "సన్నగా", "ml": "മെലിഞ്ഞ"}, value="thin"),
            QuestionOption(option_id="build_medium", text={"en": "Medium", "hi": "मध्यम", "ta": "நடுத்தர", "te": "మధ్యస్థ", "ml": "ഇടത്തരം"}, value="medium"),
            QuestionOption(option_id="build_heavy", text={"en": "Heavy/large", "hi": "भारी/बड़ा", "ta": "கனமான", "te": "బరువుగా", "ml": "ഭാരമുള്ള"}, value="heavy"),
        ],
        required=True,
        extraction_hints=["prakriti", "vata", "kapha"],
        clinical_concept_id="AYUSH:PRAKRITI:BUILD"
    ),
    Question(
        question_id="ayush_cold_sensitivity",
        section="prakriti",
        text={
            "en": "Do you usually feel cold easily?",
            "hi": "क्या आपको आमतौर पर आसानी से ठंड लगती है?",
            "ta": "பொதுவாக உங்களுக்கு எளிதில் குளிர் உணர்வீர்களா?",
            "te": "మీరు సాధారణంగా సులభంగా చల్లగా అనుభవిస్తారా?",
            "ml": "നിങ്ങൾക്ക് സാധാരണയായി എളുപ്പത്തിൽ തണുപ്പ് അനുഭവപ്പെടുമോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="cold_yes", text={"en": "Yes, very much", "hi": "हाँ, बहुत", "ta": "ஆம், மிகவும்", "te": "అవును, చాలా", "ml": "അതെ, വളരെ"}, value="high"),
            QuestionOption(option_id="cold_sometimes", text={"en": "Sometimes", "hi": "कभी-कभी", "ta": "சில சமயம்", "te": "కొన్నిసార్లు", "ml": "ചിലപ്പോൾ"}, value="medium"),
            QuestionOption(option_id="cold_no", text={"en": "No, not really", "hi": "नहीं, वास्तव में नहीं", "ta": "இல்லை, உண்மையில் இல்லை", "te": "కాదు, నిజంగా కాదు", "ml": "ഇല്ല, ശരിക്കും ഇല്ല"}, value="low"),
        ],
        required=True,
        extraction_hints=["prakriti", "vata"],
        clinical_concept_id="AYUSH:PRAKRITI:TEMPERATURE"
    ),
    Question(
        question_id="ayush_appetite",
        section="agni",
        text={
            "en": "How is your appetite?",
            "hi": "आपकी भूख कैसी है?",
            "ta": "உங்கள் பசி எப்படி உள்ளது?",
            "te": "మీ ఆకలి ఎలా ఉంది?",
            "ml": "നിങ്ങളുടെ വിശപ്പ് എങ്ങനെയാണ്?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="appetite_strong", text={"en": "Strong and regular", "hi": "मजबूत और नियमित", "ta": "வலுவான மற்றும் வழக்கமான", "te": "బలమైన మరియు క్రమబద్ధమైన", "ml": "ശക്തവും പതിവുമായ"}, value="strong"),
            QuestionOption(option_id="appetite_irregular", text={"en": "Irregular/variable", "hi": "अनियमित/परिवर्तनशील", "ta": "ஒழுங்கற்ற", "te": "క్రమరహిత", "ml": "ക്രമരഹിതം"}, value="irregular"),
            QuestionOption(option_id="appetite_weak", text={"en": "Weak/poor", "hi": "कमजोर/खराब", "ta": "பலவீனமான", "te": "బలహీన", "ml": "ദുർബലം"}, value="weak"),
        ],
        required=True,
        extraction_hints=["agni"],
        clinical_concept_id="AYUSH:AGNI:APPETITE"
    ),
    Question(
        question_id="ayush_digestion",
        section="agni",
        text={
            "en": "How is your digestion?",
            "hi": "आपका पाचन कैसा है?",
            "ta": "உங்கள் செரிமானம் எப்படி உள்ளது?",
            "te": "మీ జీర్ణక్రియ ఎలా ఉంది?",
            "ml": "നിങ്ങളുടെ ദഹനം എങ്ങനെയാണ്?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="digestion_good", text={"en": "Good, no problems", "hi": "अच्छा, कोई समस्या नहीं", "ta": "நல்லது, பிரச்சனை இல்லை", "te": "మంచిది, సమస్యలు లేవు", "ml": "നല്ലത്, പ്രശ്നങ്ങളില്ല"}, value="good"),
            QuestionOption(option_id="digestion_slow", text={"en": "Slow/heavy feeling", "hi": "धीमा/भारी महसूस", "ta": "மெதுவான", "te": "నెమ్మదిగా", "ml": "മന്ദഗതിയിലുള്ള"}, value="slow"),
            QuestionOption(option_id="digestion_gas", text={"en": "Gas/bloating", "hi": "गैस/सूजन", "ta": "வாயு", "te": "గ్యాస్", "ml": "വാതം"}, value="gas"),
        ],
        required=True,
        extraction_hints=["agni"],
        clinical_concept_id="AYUSH:AGNI:DIGESTION"
    ),
    Question(
        question_id="ayush_bowel",
        section="koshtha",
        text={
            "en": "How are your bowel movements?",
            "hi": "आपका मल त्याग कैसा है?",
            "ta": "உங்கள் குடல் இயக்கம் எப்படி உள்ளது?",
            "te": "మీ మల విసర్జన ఎలా ఉంది?",
            "ml": "നിങ്ങളുടെ മലവിസർജ്ജനം എങ്ങനെയാണ്?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="bowel_regular", text={"en": "Regular and normal", "hi": "नियमित और सामान्य", "ta": "வழக்கமான மற்றும் சாதாரணமான", "te": "క్రమబద్ధమైన మరియు సాధారణమైన", "ml": "പതിവും സാധാരണവുമായ"}, value="normal"),
            QuestionOption(option_id="bowel_constipated", text={"en": "Constipated/hard", "hi": "कब्ज/कठोर", "ta": "மலச்சிக்கல்", "te": "మలబద్ధకం", "ml": "മലബന്ധം"}, value="constipated"),
            QuestionOption(option_id="bowel_loose", text={"en": "Loose/frequent", "hi": "ढीला/लगातार", "ta": "தளர்வான", "te": "వదులుగా", "ml": "അയഞ്ഞ"}, value="loose"),
        ],
        required=True,
        extraction_hints=["koshtha"],
        clinical_concept_id="AYUSH:KOSHTHA:BOWEL"
    ),
    Question(
        question_id="ayush_sleep",
        section="satva",
        text={
            "en": "How is your sleep?",
            "hi": "आपकी नींद कैसी है?",
            "ta": "உங்கள் தூக்கம் எப்படி உள்ளது?",
            "te": "మీ నిద్ర ఎలా ఉంది?",
            "ml": "നിങ്ങളുടെ ഉറക്കം എങ്ങനെയാണ്?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="sleep_good", text={"en": "Deep and restful", "hi": "गहरी और आरामदायक", "ta": "ஆழமான மற்றும் அமைதியான", "te": "లోతైన మరియు విశ్రాంతి", "ml": "ആഴമേറിയതും വിശ്രമവുമുള്ള"}, value="good"),
            QuestionOption(option_id="sleep_light", text={"en": "Light/easily disturbed", "hi": "हल्की/आसानी से परेशान", "ta": "இலேசான", "te": "తేలికపాటి", "ml": "ലഘുവായ"}, value="light"),
            QuestionOption(option_id="sleep_difficult", text={"en": "Difficulty falling asleep", "hi": "सोने में कठिनाई", "ta": "தூங்குவதில் சிரமம்", "te": "నిద్రపోవడానికి కష్టం", "ml": "ഉറങ്ങാൻ ബുദ്ധിമുട്ട്"}, value="difficult"),
        ],
        required=True,
        extraction_hints=["satva"],
        clinical_concept_id="AYUSH:SATVA:SLEEP"
    ),
    Question(
        question_id="ayush_stress",
        section="satva",
        text={
            "en": "How do you usually react when you are stressed?",
            "hi": "तनाव में आप आमतौर पर कैसे प्रतिक्रिया करते हैं?",
            "ta": "மன அழுத்தத்தில் இருக்கும்போது நீங்கள் பொதுவாக எவ்வாறு எதிர்வினை செய்வீர்கள்?",
            "te": "ఒత్తిడిలో ఉన్నప్పుడు మీరు సాధారణంగా ఎలా స్పందిస్తారు?",
            "ml": "സമ്മർദ്ദത്തിലായിരിക്കുമ്പോൾ നിങ്ങൾ സാധാരണയായി എങ്ങനെ പ്രതികരിക്കും?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="stress_anxious", text={"en": "Anxious/worried", "hi": "चिंतित/चिंतित", "ta": "கவலையான", "te": "ఆత్రుతగా", "ml": "ഉത്കണ്ഠയോടെ"}, value="anxious"),
            QuestionOption(option_id="stress_angry", text={"en": "Irritable/angry", "hi": "चिड़चिड़ा/गुस्सा", "ta": "எரிச்சலான", "te": "కోపంగా", "ml": "കോപത്തോടെ"}, value="angry"),
            QuestionOption(option_id="stress_calm", text={"en": "Remain relatively calm", "hi": "अपेक्षाकृत शांत रहें", "ta": "அமைதியாக இருக்கும்", "te": "సాపేక్షంగా ప్రశాంతంగా ఉండండి", "ml": "താരതമ്യേന ശാന്തമായി തുടരുക"}, value="calm"),
        ],
        required=False,
        extraction_hints=["satva"],
        clinical_concept_id="AYUSH:SATVA:STRESS"
    ),
    Question(
        question_id="ayush_activity",
        section="ahara_vihara",
        text={
            "en": "How active are you during the day?",
            "hi": "दिन के दौरान आप कितने सक्रिय हैं?",
            "ta": "நாள் முழுவதும் நீங்கள் எவ்வளவு சுறுசுறுப்பாக இருக்கிறீர்கள்?",
            "te": "రోజంతా మీరు ఎంత చురుకుగా ఉంటారు?",
            "ml": "ദിവസം മുഴുവൻ നിങ്ങൾ എത്ര സജീവമാണ്?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="activity_very", text={"en": "Very active", "hi": "बहुत सक्रिय", "ta": "மிகவும் சுறுசுறுப்பான", "te": "చాలా చురుకుగా", "ml": "വളരെ സജീവം"}, value="high"),
            QuestionOption(option_id="activity_moderate", text={"en": "Moderately active", "hi": "मध्यम सक्रिय", "ta": "மிதமான சுறுசுறுப்பு", "te": "మధ్యస్థంగా చురుకుగా", "ml": "മിതമായ സജീവത"}, value="medium"),
            QuestionOption(option_id="activity_sedentary", text={"en": "Mostly sitting", "hi": "ज्यादातर बैठे", "ta": "பெரும்பாலும் உட்கார்ந்து", "te": "ఎక్కువగా కూర్చుని", "ml": "കൂടുതലും ഇരുന്ന്"}, value="low"),
        ],
        required=False,
        extraction_hints=["ahara_vihara"],
        clinical_concept_id="AYUSH:AHARA_VIHARA:ACTIVITY"
    ),
]


def get_ayush_questionnaire() -> List[Question]:
    """Get AYUSH questionnaire."""
    return AYUSH_QUESTIONS


def _build_option_lookup(questions: List[Question]) -> Dict[str, Dict[str, str]]:
    """
    Build a bidirectional lookup: question_id -> {option_value -> option_id, option_id -> option_value}.
    Also maps raw answer text patterns to normalized values.
    """
    lookup = {}
    for question in questions:
        value_to_id = {}
        id_to_value = {}
        # Free-text aliases that patients might type (lowercase)
        value_to_aliases: Dict[str, List[str]] = {}

        for opt in question.options or []:
            val = opt.value if isinstance(opt.value, str) else str(opt.value)
            value_to_id[val] = opt.option_id
            id_to_value[opt.option_id] = val

            # Collect all language variants as aliases for fuzzy matching
            for lang, text in opt.text.items():
                alias_key = text.lower().strip()
                if alias_key not in value_to_aliases:
                    value_to_aliases[alias_key] = []
                value_to_aliases[alias_key].append(val)

        lookup[question.question_id] = {
            "value_to_id": value_to_id,
            "id_to_value": id_to_value,
            "aliases": value_to_aliases,
        }
    return lookup


# Module-level lookup (built once)
_OPTION_LOOKUP = _build_option_lookup(AYUSH_QUESTIONS)


def _normalize_answer(question_id: str, raw_answer: str) -> str:
    """
    Normalize a patient answer to a known option value.

    Returns:
        The matched option value, or "unknown" if no match found.
    """
    if not raw_answer or not isinstance(raw_answer, str):
        return "unknown"

    question_lookup = _OPTION_LOOKUP.get(question_id, {})
    value_to_id = question_lookup.get("value_to_id", {})
    aliases = question_lookup.get("aliases", {})

    # 1. Exact match on known option values
    if raw_answer in value_to_id:
        return raw_answer

    # 2. Case-insensitive alias match (patient types option text verbatim)
    raw_lower = raw_answer.lower().strip()
    for alias, val in aliases.items():
        if alias == raw_lower or raw_lower in alias or alias in raw_lower:
            return val

    # 3. Partial keyword matching for common patterns
    patterns: Dict[str, str] = {
        # Body build
        "thin": "thin", "lean": "thin", "slim": "thin",
        "medium": "medium", "average": "medium",
        "heavy": "heavy", "large": "heavy", "big": "heavy", "overweight": "heavy",
        # Cold sensitivity
        "yes": "high", "very much": "high", "lot": "high",
        "sometimes": "medium", "occasionally": "medium", "moderate": "medium",
        "no": "low", "not": "low", "never": "low",
        # Appetite
        "strong": "strong", "good": "strong", "regular": "strong", "normal": "strong",
        "irregular": "irregular", "variable": "irregular", "changes": "irregular",
        "weak": "weak", "poor": "weak", "low": "weak",
        # Digestion
        "good": "good", "fine": "good", "okay": "good", "ok": "good",
        "slow": "slow", "heavy": "slow", "lethargic": "slow",
        "gas": "gas", "bloating": "gas", "bloated": "gas",
        # Bowel
        "regular": "normal", "normal": "normal",
        "constipated": "constipated", "hard": "constipated", "difficulty": "constipated",
        "loose": "loose", "frequent": "loose", "diarrhea": "loose", " watery": "loose",
        # Sleep
        "deep": "good", "restful": "good", "good": "good", "well": "good",
        "light": "light", "disturbed": "light", "interrupted": "light",
        "difficult": "difficult", "hard": "difficult", "insomnia": "difficult",
        # Stress
        "anxious": "anxious", "worried": "anxious", "nervous": "anxious",
        "angry": "angry", "irritable": "angry", "frustrated": "angry",
        "calm": "calm", "peaceful": "calm", "relaxed": "calm",
        # Activity
        "very active": "high", "active": "high", "energetic": "high", "high": "high",
        "moderate": "medium", "moderately": "medium", "somewhat": "medium",
        "sedentary": "low", "sitting": "low", "lazy": "low", "inactive": "low",
    }

    for pattern, value in patterns.items():
        if pattern in raw_lower:
            # Verify this value is actually valid for this question
            if value in value_to_id:
                return value

    return "unknown"


class AyushEngine:
    """AYUSH adaptive questionnaire and scoring engine."""

    def __init__(self):
        self.questions = get_ayush_questionnaire()
        self.option_lookup = _OPTION_LOOKUP

    def get_next_question(self, answered_questions: List[str]) -> Optional[Dict[str, Any]]:
        """Get next unanswered AYUSH question."""
        answered_set = set(answered_questions)

        for question in self.questions:
            if question.question_id not in answered_set:
                return {
                    "question_id": question.question_id,
                    "section": question.section,
                    "text": question.text,
                    "field_type": question.field_type,
                    "options": [opt.model_dump() for opt in question.options] if question.options else None,
                    "required": question.required
                }

        return None

    def _build_provenance(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        """Build provenance metadata from a stored answer."""
        return {
            "question_id": answer.get("question_id"),
            "answer": answer.get("answer"),
            "answer_text": answer.get("answer_text"),
            "normalized_value": answer.get("normalized_value"),
            "input_mode": answer.get("input_mode"),
            "language": answer.get("language"),
            "timestamp": answer.get("timestamp"),
        }

    def _score_prakriti(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score Vata/Pitta/Kapha based on relevant answers.

        Raw scores accumulate from individual answers.
        Normalized scores are proportions of the total raw score.
        """
        raw_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        indicators: List[Dict[str, Any]] = []

        # Weight table: {question_id: {option_value: {dosha: weight}}
        SCORING_RULES: Dict[str, Dict[str, Dict[str, float]]] = {
            "ayush_body_build": {
                "thin":    {"vata": 2.0, "pitta": 0.0, "kapha": 0.0},
                "medium":  {"vata": 0.5, "pitta": 1.5, "kapha": 0.5},
                "heavy":   {"vata": 0.0, "pitta": 0.0, "kapha": 2.0},
                "unknown": {"vata": 0.0, "pitta": 0.0, "kapha": 0.0},
            },
            "ayush_cold_sensitivity": {
                "high":    {"vata": 2.0, "pitta": 0.0, "kapha": 0.0},
                "medium":  {"vata": 1.0, "pitta": 0.5, "kapha": 0.5},
                "low":     {"vata": 0.0, "pitta": 1.0, "kapha": 1.0},
                "unknown": {"vata": 0.0, "pitta": 0.0, "kapha": 0.0},
            },
        }

        for answer in answers:
            qid = answer.get("question_id")
            # Use normalized value if available, else fall back to raw answer
            normalized = answer.get("normalized_value") or answer.get("answer") or answer.get("answer_text")
            provenance = self._build_provenance(answer)

            if qid in SCORING_RULES:
                rule = SCORING_RULES[qid]
                if normalized in rule:
                    weights = rule[normalized]
                    raw_scores["vata"] += weights["vata"]
                    raw_scores["pitta"] += weights["pitta"]
                    raw_scores["kapha"] += weights["kapha"]
                    indicators.append({
                        "question_id": qid,
                        "raw_answer": answer.get("answer_text"),
                        "normalized_value": normalized,
                        "vata_contribution": weights["vata"],
                        "pitta_contribution": weights["pitta"],
                        "kapha_contribution": weights["kapha"],
                        "provenance": provenance,
                    })
                else:
                    # Normalized value not in scoring rules - record unknown indicator
                    indicators.append({
                        "question_id": qid,
                        "raw_answer": answer.get("answer_text"),
                        "normalized_value": normalized,
                        "vata_contribution": 0.0,
                        "pitta_contribution": 0.0,
                        "kapha_contribution": 0.0,
                        "provenance": provenance,
                        "note": "normalized_value not in scoring rules",
                    })
            else:
                # Question not scored for prakriti
                pass

        # Normalize to proportions (0-1 scale per dosha)
        total_raw = sum(raw_scores.values())
        if total_raw > 0:
            normalized_scores = {
                "vata": raw_scores["vata"] / total_raw,
                "pitta": raw_scores["pitta"] / total_raw,
                "kapha": raw_scores["kapha"] / total_raw,
            }
            confidence = raw_scores["vata"] / total_raw if total_raw > 0 else 0.0  # relative to max possible
            # Confidence = how much the dominant score exceeds random (33%)
            max_score = max(raw_scores.values()) if raw_scores else 0
            confidence = min(1.0, (max_score / total_raw) if total_raw > 0 else 0.0)
        else:
            normalized_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
            confidence = 0.0

        # Dominant dosha (ties broken by vata > pitta > kapha as secondary)
        dominant = max(normalized_scores, key=lambda k: (normalized_scores[k], ["kapha", "pitta", "vata"].index(k)))

        return {
            "raw_scores": raw_scores,
            "vata_score": normalized_scores["vata"],
            "pitta_score": normalized_scores["pitta"],
            "kapha_score": normalized_scores["kapha"],
            "dominant_type": dominant if total_raw > 0 else None,
            "confidence": confidence,
            "indicators": indicators,
        }

    def _assess_agni(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess digestive fire (Agni) from appetite and digestion answers."""
        agni_indicators: List[Dict[str, Any]] = []
        assessment = "unknown"
        confidence = 0.0

        for answer in answers:
            qid = answer.get("question_id")
            if qid not in ("ayush_appetite", "ayush_digestion"):
                continue

            normalized = answer.get("normalized_value") or answer.get("answer") or answer.get("answer_text")
            provenance = self._build_provenance(answer)

            if normalized in ("strong", "good"):
                assessment = "strong"
                confidence = max(confidence, 1.0)
            elif normalized == "irregular":
                assessment = "irregular"
                confidence = max(confidence, 0.8)
            elif normalized == "weak":
                assessment = "weak"
                confidence = max(confidence, 0.9)
            elif normalized == "slow":
                # "slow digestion" suggests mandagni
                if assessment not in ("strong",):
                    assessment = "mandagni"  # weak digestive fire
                confidence = max(confidence, 0.8)
            elif normalized == "gas":
                if assessment not in ("strong",):
                    assessment = "irregular"
                confidence = max(confidence, 0.7)

            agni_indicators.append({
                "question_id": qid,
                "normalized_value": normalized,
                "provenance": provenance,
            })

        if assessment == "unknown":
            assessment = "not_assessed"

        return {
            "assessment": assessment,
            "confidence": confidence,
            "indicators": agni_indicators,
        }

    def _assess_koshtha(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess bowel pattern (Koshtha) from bowel movement answer."""
        koshtha_indicators: List[Dict[str, Any]] = []
        assessment = "unknown"
        confidence = 0.0

        for answer in answers:
            qid = answer.get("question_id")
            if qid != "ayush_bowel":
                continue

            normalized = answer.get("normalized_value") or answer.get("answer") or answer.get("answer_text")
            provenance = self._build_provenance(answer)

            if normalized == "normal":
                assessment = "normal"
                confidence = 1.0
            elif normalized == "constipated":
                assessment = "constipated"
                confidence = 1.0
            elif normalized == "loose":
                assessment = "loose"
                confidence = 1.0

            koshtha_indicators.append({
                "question_id": qid,
                "normalized_value": normalized,
                "provenance": provenance,
            })

        if assessment == "unknown":
            assessment = "not_assessed"

        return {
            "assessment": assessment,
            "confidence": confidence,
            "indicators": koshtha_indicators,
        }

    def _assess_satva(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess mental/emotional pattern (Satva) from sleep and stress answers."""
        satva_indicators: List[Dict[str, Any]] = []
        stress_response: Optional[str] = None
        sleep_quality: Optional[str] = None
        confidence = 0.0

        for answer in answers:
            qid = answer.get("question_id")
            if qid not in ("ayush_sleep", "ayush_stress"):
                continue

            normalized = answer.get("normalized_value") or answer.get("answer") or answer.get("answer_text")
            provenance = self._build_provenance(answer)

            if qid == "ayush_sleep":
                sleep_quality = normalized if normalized != "unknown" else None
                if normalized == "good":
                    confidence = max(confidence, 0.8)
                elif normalized == "light":
                    confidence = max(confidence, 0.7)
                elif normalized == "difficult":
                    confidence = max(confidence, 0.8)

            if qid == "ayush_stress":
                stress_response = normalized if normalized != "unknown" else None
                if normalized in ("calm", "anxious", "angry"):
                    confidence = max(confidence, 0.7)

            satva_indicators.append({
                "question_id": qid,
                "normalized_value": normalized,
                "provenance": provenance,
            })

        return {
            "stress_response": stress_response,
            "sleep_quality": sleep_quality,
            "confidence": confidence,
            "indicators": satva_indicators,
        }

    def _assess_ahara_vihara(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess diet and lifestyle (Ahara-Vihara) from activity answer."""
        indicators: List[Dict[str, Any]] = []
        activity_level: Optional[str] = None
        confidence = 0.0

        for answer in answers:
            qid = answer.get("question_id")
            if qid != "ayush_activity":
                continue

            normalized = answer.get("normalized_value") or answer.get("answer") or answer.get("answer_text")
            provenance = self._build_provenance(answer)

            if normalized in ("high", "medium", "low"):
                activity_level = normalized
                confidence = 1.0

            indicators.append({
                "question_id": qid,
                "normalized_value": normalized,
                "provenance": provenance,
            })

        return {
            "activity_level": activity_level,
            "confidence": confidence,
            "indicators": indicators,
        }

    def calculate_profile(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate AYUSH constitutional profile from patient answers.

        Separation of concerns:
        - Raw patient answer (as entered)
        - Normalized answer (mapped to known option values)
        - Calculated profile (derived from normalized answers)
        - Confidence/status (how certain the assessment is)

        Rules:
        - Unknown inputs do NOT default to negative scores
        - Missing questions do NOT count against the patient
        - Only questions with valid answers contribute to scoring
        """
        if not answers:
            return self._empty_profile()

        # Ensure every answer has a normalized_value
        normalized_answers = []
        for answer in answers:
            ans = dict(answer)
            if "normalized_value" not in ans or not ans["normalized_value"]:
                ans["normalized_value"] = _normalize_answer(
                    ans.get("question_id", ""),
                    ans.get("answer_text") or ans.get("answer") or ""
                )
            normalized_answers.append(ans)

        required_qids = {q.question_id for q in self.questions if q.required}
        answered_required = {a["question_id"] for a in normalized_answers if a["question_id"] in required_qids}
        completion_pct = int(len(answered_required) / len(required_qids) * 100) if required_qids else 100

        prakriti = self._score_prakriti(normalized_answers)
        agni = self._assess_agni(normalized_answers)
        koshtha = self._assess_koshtha(normalized_answers)
        satva = self._assess_satva(normalized_answers)
        ahara_vihara = self._assess_ahara_vihara(normalized_answers)

        return {
            "prakriti": {
                "vata_score": prakriti["vata_score"],
                "pitta_score": prakriti["pitta_score"],
                "kapha_score": prakriti["kapha_score"],
                "dominant_type": prakriti["dominant_type"],
                "confidence": prakriti["confidence"],
                "raw_scores": prakriti["raw_scores"],
                "indicators": prakriti["indicators"],
            },
            "agni": agni,
            "koshtha": koshtha,
            "satva": satva,
            "ahara_vihara": ahara_vihara,
            "answers": normalized_answers,
            "is_complete": completion_pct >= 100,
            "completion_percentage": completion_pct,
        }

    def _empty_profile(self) -> Dict[str, Any]:
        """Return an empty profile structure."""
        return {
            "prakriti": {
                "vata_score": 0.0,
                "pitta_score": 0.0,
                "kapha_score": 0.0,
                "dominant_type": None,
                "confidence": 0.0,
                "raw_scores": {"vata": 0.0, "pitta": 0.0, "kapha": 0.0},
                "indicators": [],
            },
            "agni": {"assessment": "not_assessed", "confidence": 0.0, "indicators": []},
            "koshtha": {"assessment": "not_assessed", "confidence": 0.0, "indicators": []},
            "satva": {"stress_response": None, "sleep_quality": None, "confidence": 0.0, "indicators": []},
            "ahara_vihara": {"activity_level": None, "confidence": 0.0, "indicators": []},
            "answers": [],
            "is_complete": False,
            "completion_percentage": 0,
        }
