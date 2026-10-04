"""
Unified stream questionnaire loader.

Single source of truth for all patient-facing clinical questionnaires.
Returns questions with language-independent option values.

Architecture:
  mode + stream → load appropriate question set → return unified Question list

All options use `value` (internal, language-independent) and `text` (localized labels).
The backend NEVER receives display text as clinical data.
"""
from typing import Dict, List, Any, Optional
from app.schemas.conversation import Question, QuestionOption


# ─────────────────────────────────────────────────────────────
# AYURVEDA  (~15 patient-friendly questions)
# ─────────────────────────────────────────────────────────────

def _make_ayurveda_questions() -> List[Question]:
    return [
        # Constitution / Prakriti
        Question(
            question_id="ayurveda_body_build",
            section="Constitution",
            text={
                "en": "How would you describe your general body build?",
                "hi": "आप अपने शरीर की बनावट का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் உடல் அமைப்பை எவ்வாறு விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_build_slim",  text={"en": "Slim and light", "hi": "पतला और हल्का", "ta": "மெலிந்து லேசாக"},   value="SLIM"),
                QuestionOption(option_id="ay_build_medium",text={"en": "Medium build",     "hi": "मध्यम बनावट",  "ta": "நடுத்தர அமைப்பு"}, value="MEDIUM"),
                QuestionOption(option_id="ay_build_heavy", text={"en": "Broad and well-built","hi":"भारी और मजबूत","ta": "கனமான உறுதியான"},  value="HEAVY"),
            ],
            required=True,
            extraction_hints=["prakriti", "body", "constitution"],
            clinical_concept_id="AYUSH:PRAKRITI:BUILD",
        ),
        Question(
            question_id="ayurveda_thermal",
            section="Constitution",
            text={
                "en": "Do you usually feel comfortable in cool weather or warm weather?",
                "hi": "आप आमतौर पर ठंड के मौसम में सहज महसूस करते हैं या गर्म मौसम में?",
                "ta": "குளிர்ச்சியான வானிலையில் அல்லது சூடான வானிலையில் வழக்கமாக நீங்கள் வசதியாக உணருகிறீர்களா?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_thermal_warm",  text={"en": "I prefer warmth",          "hi": "मुझे गर्मी पसंद है",       "ta": "வெம்மையை விரும்புகிறேன்"},    value="PREFERS_WARM"),
                QuestionOption(option_id="ay_thermal_cool",  text={"en": "I prefer cooler weather",   "hi": "मुझे ठंड पसंद है",         "ta": "குளிர்ச்சியை விரும்புகிறேன்"}, value="PREFERS_COOL"),
                QuestionOption(option_id="ay_thermal_both", text={"en": "Both are comfortable",      "hi": "दोनों में सहज हूँ",          "ta": "இரண்டும் வசதியானவை"},         value="NO_PREFERENCE"),
            ],
            required=True,
            extraction_hints=["prakriti", "temperature", "weather"],
            clinical_concept_id="AYUSH:PRAKRITI:THERMAL",
        ),
        Question(
            question_id="ayurveda_skin",
            section="Constitution",
            text={
                "en": "How would you describe your skin generally?",
                "hi": "आप अपनी त्वचा का सामान्य रूप से वर्णन कैसे करेंगे?",
                "ta": "உங்கள் தோலை பொதுவாக எவ்வாறு விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_skin_dry",    text={"en": "Dry or rough",              "hi": "सूखी या खुरदरी",         "ta": "உலர்ந்த அல்லது கருகலான"},   value="DRY"),
                QuestionOption(option_id="ay_skin_oily",    text={"en": "Oily or greasy",            "hi": "तैलीय या चिकनी",         "ta": "எண்ணெய் அல்லது கொழுப்பு"},  value="OILY"),
                QuestionOption(option_id="ay_skin_normal",  text={"en": "Normal and balanced",       "hi": "सामान्य और संतुलित",      "ta": "சாதாரணமான மற்றும் சமநிலை"}, value="NORMAL"),
                QuestionOption(option_id="ay_skin_combo",  text={"en": "Combination / varies",       "hi": "मिश्रित / बदलता रहता है", "ta": "கலவையான / மாறுபடும்"},       value="COMBINATION"),
            ],
            required=True,
            extraction_hints=["prakriti", "skin", "texture"],
            clinical_concept_id="AYUSH:PRAKRITI:SKIN",
        ),
        # Digestion / Agni
        Question(
            question_id="ayurveda_appetite",
            section="Digestion",
            text={
                "en": "How is your hunger during the day?",
                "hi": "दिन में आपकी भूख कैसी रहती है?",
                "ta": "பகலில் உங்கள் பசி எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_appt_strong",   text={"en": "Very strong and regular", "hi": "बहुत तीव्र और नियमित",  "ta": "மிகவும் வலுவான மற்றும் வழக்கமான"}, value="STRONG"),
                QuestionOption(option_id="ay_appt_regular",   text={"en": "Regular and manageable",   "hi": "नियमित और सामान्य",      "ta": "வழக்கமான மற்றும் நிர்வகிக்கக்கூடிய"}, value="REGULAR"),
                QuestionOption(option_id="ay_appt_irregular", text={"en": "Changes frequently",        "hi": "बार-बार बदलती है",      "ta": "அடிக்கடி மாறும்"},                 value="IRREGULAR"),
                QuestionOption(option_id="ay_appt_low",       text={"en": "Usually low",              "hi": "आमतौर पर कम",           "ta": "வழக்கமாக குறைவு"},              value="LOW"),
            ],
            required=True,
            extraction_hints=["agni", "appetite", "hunger"],
            clinical_concept_id="AYUSH:AGNI:APPETITE",
        ),
        Question(
            question_id="ayurveda_digestion",
            section="Digestion",
            text={
                "en": "How does food usually sit with you after eating?",
                "hi": "खाने के बाद आपके साथ आमतौर पर पाचन कैसा रहता है?",
                "ta": "சாப்பிட்டபிறகு வழக்கமாக உங்களுக்கு செரிமானம் எப்படி இருக்கும்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_dig_good", text={"en": "I digest it well, no issues",     "hi": "अच्छा पचता है, कोई दिक्कत नहीं", "ta": "நன்றாக செரிமானம் ஆகிறது, சிக்கல் இல்லை"}, value="GOOD"),
                QuestionOption(option_id="ay_dig_slow", text={"en": "Feels heavy or slow to digest",   "hi": "भारीपन महसूस होता है",          "ta": "கனமாக உணர்கிறது அல்லது மெதுவாக செரிமானம்"}, value="SLOW"),
                QuestionOption(option_id="ay_dig_gas",  text={"en": "I often have gas or bloating",    "hi": "मुझे अक्सर गैस या सूजन होती है","ta": "அடிக்கடி வாயு அல்லது வீக்கம் உணர்கிறேன்"}, value="GAS"),
                QuestionOption(option_id="ay_dig_loose", text={"en": "I tend toward loose motions",    "hi": "मुझे दस्त लगने की प्रवृत्ति होती है","ta": "தளர்வான குடல் இயக்கத்திற்கு சாத்தியம்"}, value="LOOSE"),
            ],
            required=True,
            extraction_hints=["agni", "digestion", "stomach"],
            clinical_concept_id="AYUSH:AGNI:DIGESTION",
        ),
        Question(
            question_id="ayurveda_bowel",
            section="Digestion",
            text={
                "en": "How are your bowel movements usually?",
                "hi": "आपका मल त्याग आमतौर पर कैसा रहता है?",
                "ta": "உங்கள் குடல் இயக்கம் வழக்கமாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_bowel_normal",      text={"en": "Usually normal",       "hi": "आमतौर पर सामान्य",     "ta": "வழக்கமாக சாதாரணமான"},  value="NORMAL"),
                QuestionOption(option_id="ay_bowel_constipated",  text={"en": "Hard or difficult",    "hi": "कठोर या कठिन",         "ta": "கடினமான அல்லது கடினம்"}, value="CONSTIPATED"),
                QuestionOption(option_id="ay_bowel_loose",        text={"en": "Loose or frequent",    "hi": "ढीला या बार-बार",      "ta": "தளர்வான அல்லது அடிக்கடி"},value="LOOSE"),
            ],
            required=True,
            extraction_hints=["koshtha", "bowel", "motion"],
            clinical_concept_id="AYUSH:KOSHTHA:BOWEL",
        ),
        # Sleep / Mind
        Question(
            question_id="ayurveda_sleep",
            section="General",
            text={
                "en": "How do you usually sleep?",
                "hi": "आप आमतौर पर कैसे सोते हैं?",
                "ta": "நீங்கள் வழக்கமாக எப்படி தூங்குகிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_sleep_deep",     text={"en": "Deep and restful",          "hi": "गहरी और आरामदायक",         "ta": "ஆழமான மற்றும் அமைதியான"},   value="DEEP_RESTFUL"),
                QuestionOption(option_id="ay_sleep_light",    text={"en": "Light or easily interrupted","hi": "हल्की या आसानी से टूटती है",  "ta": "இலேசான அல்லது எளிதில் இடையூறு"}, value="LIGHT"),
                QuestionOption(option_id="ay_sleep_difficult",text={"en": "I often have difficulty",     "hi": "मुझे अक्सर कठिनाई होती है", "ta": "அடிக்கடி சிரமம் ஏற்படுகிறது"}, value="DIFFICULT"),
            ],
            required=True,
            extraction_hints=["satva", "sleep", "rest"],
            clinical_concept_id="AYUSH:SATVA:SLEEP",
        ),
        Question(
            question_id="ayurveda_stress",
            section="General",
            text={
                "en": "When something stressful happens, how do you usually respond?",
                "hi": "जब कुछ तनावपूर्ण होता है, तो आप आमतौर पर कैसे प्रतिक्रिया करते हैं?",
                "ta": "மன அழுத்தம் ஏற்படும்போது, நீங்கள் வழக்கமாக எவ்வாறு பதிலளிக்கிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_stress_calm",    text={"en": "I stay calm",             "hi": "मैं शांत रहता हूँ",           "ta": "அமைதியாக இருக்கிறேன்"},           value="CALM"),
                QuestionOption(option_id="ay_stress_worry",   text={"en": "I worry but recover",     "hi": "चिंता होती है लेकिन ठीक हो जाता हूँ","ta": "கவலை ஏற்படும் ஆனால் மீள்கிறேன்"}, value="WORRIED_RECOVER"),
                QuestionOption(option_id="ay_stress_overwhelm",text={"en": "I feel overwhelmed easily","hi": "मुझे आसानी से बोझ लगता है","ta": "எளிதில் அழுத்தமாக உணர்கிறேன்"}, value="OVERWHELMED"),
            ],
            required=False,
            extraction_hints=["satva", "stress", "mental"],
            clinical_concept_id="AYUSH:SATVA:STRESS",
        ),
        # Activity / Lifestyle
        Question(
            question_id="ayurveda_activity",
            section="Lifestyle",
            text={
                "en": "How active are you during the day?",
                "hi": "दिन के दौरान आप कितने सक्रिय रहते हैं?",
                "ta": "பகல் நேரத்தில் நீங்கள் எவ்வளவு சுறுசுறுப்பாக இருக்கிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_act_high",   text={"en": "Very active and energetic",  "hi": "बहुत सक्रिय और ऊर्जावान",    "ta": "மிகவும் சுறுசுறுப்பான மற்றும் ஆற்றல்"}, value="HIGH"),
                QuestionOption(option_id="ay_act_medium", text={"en": "Moderately active",           "hi": "मध्यम सक्रिय",                 "ta": "மிதமான சுறுசுறுப்பு"},            value="MEDIUM"),
                QuestionOption(option_id="ay_act_low",    text={"en": "Mostly sitting or resting",   "hi": "ज्यादातर बैठे या आराम",        "ta": "பெரும்பாலும் உட்கார்ந்து அல்லது ஓய்வு"}, value="LOW"),
            ],
            required=False,
            extraction_hints=["ahara_vihara", "activity", "exercise"],
            clinical_concept_id="AYUSH:AHARA_VIHARA:ACTIVITY",
        ),
        # Food habits
        Question(
            question_id="ayurveda_food_preference",
            section="Diet",
            text={
                "en": "Which type of food do you naturally prefer?",
                "hi": "आप स्वाभाविक रूप से किस प्रकार के भोजन को पसंद करते हैं?",
                "ta": "நீங்கள் இயல்பாக எந்த வகையான உணவை விரும்புகிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_food_hot",     text={"en": "Spicy and hot food",          "hi": "मसालेदार और गर्म भोजन",     "ta": "காரமான மற்றும் சூடான உணவு"},    value="SPICY_HOT"),
                QuestionOption(option_id="ay_food_cold",    text={"en": "Cooling or refreshing food",   "hi": "ठंडा या ताजा भोजन",          "ta": "குளிர்ச்சியான அல்லது நீரேற்ற உணவு"}, value="COOL_REFRESHING"),
                QuestionOption(option_id="ay_food_heavy",   text={"en": "Heavy or rich food",          "hi": "भारी या गाढ़ा भोजन",          "ta": "கனமான அல்லது பருகத் தக்க உணவு"}, value="HEAVY_RICH"),
                QuestionOption(option_id="ay_food_light",   text={"en": "Light and simple food",       "hi": "हल्का और सादा भोजन",          "ta": "இலேசான மற்றும் எளிய உணவு"},      value="LIGHT_SIMPLE"),
            ],
            required=False,
            extraction_hints=["ahara_vihara", "diet", "food"],
            clinical_concept_id="AYUSH:AHARA_VIHARA:DIET",
        ),
        # Routine
        Question(
            question_id="ayurveda_routine",
            section="Lifestyle",
            text={
                "en": "How regular is your daily routine (sleep, meals, activity)?",
                "hi": "आपकी दिनचर्या कितनी नियमित है (नींद, भोजन, गतिविधि)?",
                "ta": "உங்கள் தினசரி வழக்கம் (தூக்கம், உணவு, செயல்பாடு) எவ்வளவு வழக்கமானது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="ay_rout_regular",   text={"en": "Very regular and consistent", "hi": "बहुत नियमित और सुसंगत",     "ta": "மிகவும் வழக்கமான மற்றும் நிலையான"}, value="REGULAR"),
                QuestionOption(option_id="ay_rout_somewhat", text={"en": "Somewhat regular",            "hi": "कुछ हद तक नियमित",          "ta": "கொஞ்சம் வழக்கமான"},                value="SOMEWHAT"),
                QuestionOption(option_id="ay_rout_irregular", text={"en": "Irregular or unpredictable",  "hi": "अनियमित या अप्रत्याशित",     "ta": "வழக்கமற்ற அல்லது முன்கணிக்க முடியாத"},value="IRREGULAR"),
            ],
            required=False,
            extraction_hints=["ahara_vihara", "routine", "lifestyle"],
            clinical_concept_id="AYUSH:AHARA_VIHARA:ROUTINE",
        ),
        # Chief complaint
        Question(
            question_id="ayurveda_chief_complaint",
            section="Chief Complaint",
            text={
                "en": "What is the main health problem or symptom that brings you here today?",
                "hi": "आज आपको यहाँ लाने वाली मुख्य स्वास्थ्य समस्या या लक्षण क्या है?",
                "ta": "இன்று உங்களை இங்கு க apporté முக்கிய உடல் பிரச்சனை அல்லது அறிகுறி என்ன?",
            },
            field_type="text",
            required=True,
            extraction_hints=["chief_complaint", "symptom", "problem"],
            clinical_concept_id="SNOMED:404684003",
        ),
        Question(
            question_id="ayurveda_complaint_duration",
            section="Chief Complaint",
            text={
                "en": "How long have you had this problem?",
                "hi": "आपको यह समस्या कब से है?",
                "ta": "இந்த பிரச்சனை எவ்வாறு காலமாக உள்ளது?",
            },
            field_type="text",
            required=True,
            extraction_hints=["duration", "days", "weeks", "months", "years"],
            clinical_concept_id="SNOMED:103335007",
        ),
        Question(
            question_id="ayurveda_complaint_severity",
            section="Chief Complaint",
            text={
                "en": "On a scale of 0 to 10, how severe is this problem? (0 = no problem, 10 = most severe)",
                "hi": "0 से 10 के पैमाने पर, यह समस्या कितनी गंभीर है? (0 = कोई समस्या नहीं, 10 = सबसे गंभीर)",
                "ta": "0 முதல் 10 வரையிலான அளவில், இந்த பிரச்சனை எவ்வளவு கடுமையானது? (0 = பிரச்சனை இல்லை, 10 = மிக கடுமையானது)",
            },
            field_type="number",
            required=True,
            extraction_hints=["severity", "pain scale", "rating"],
            clinical_concept_id="SNOMED:246112005",
        ),
        Question(
            question_id="ayurveda_associated_symptoms",
            section="Chief Complaint",
            text={
                "en": "Do you have any other symptoms along with this problem?",
                "hi": "क्या इस समस्या के साथ आपको कोई अन्य लक्षण भी हैं?",
                "ta": "இந்த பிரச்சனையுடன் வேறு அறிகுறிகள் உள்ளதா?",
            },
            field_type="text",
            required=False,
            extraction_hints=["associated_symptoms", "other symptoms"],
            clinical_concept_id="SNOMED:418799008",
        ),
    ]


# ─────────────────────────────────────────────────────────────
# SIDDHA  (~12 patient-friendly questions)
# ─────────────────────────────────────────────────────────────

def _make_siddha_questions() -> List[Question]:
    return [
        Question(
            question_id="siddha_body_build",
            section="Constitution",
            text={
                "en": "How would you describe your body frame generally?",
                "hi": "आप अपने शरीर का ढांचा सामान्य रूप से कैसे बताएंगे?",
                "ta": "உங்கள் உடல் அமைப்பை பொதுவாக எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_build_thin",   text={"en": "Thin and wiry",      "hi": "पतला और मजबूत",      "ta": "மெலிந்த மற்றும் உறுதியான"}, value="THIN_WIRY"),
                QuestionOption(option_id="sid_build_medium", text={"en": "Medium and balanced", "hi": "मध्यम और संतुलित",    "ta": "நடுத்தர மற்றும் சமநிலை"}, value="MEDIUM"),
                QuestionOption(option_id="sid_build_heavy",  text={"en": "Heavy and sturdy",    "hi": "भारी और मजबूत",      "ta": "கனமான மற்றும் உறுதியான"}, value="HEAVY_STURDY"),
            ],
            required=True,
            extraction_hints=["mukkuttram", "constitution", "body"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:BUILD",
        ),
        Question(
            question_id="siddha_appetite",
            section="Digestion",
            text={
                "en": "How would you describe your hunger pattern?",
                "hi": "आप अपनी भूख की पैटर्न का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் பசி முறையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_appt_strong",   text={"en": "Strong and consistent",  "hi": "मजबूत और निरंतर",     "ta": "வலுவான மற்றும் நிலையான"}, value="STRONG"),
                QuestionOption(option_id="sid_appt_regular",  text={"en": "Regular and manageable",  "hi": "नियमित और सामान्य",     "ta": "வழக்கமான மற்றும் நிர்வகிக்கக்கூடிய"}, value="REGULAR"),
                QuestionOption(option_id="sid_appt_variable", text={"en": "Variable or unpredictable","hi": "बदलती या अप्रत्याशित", "ta": "மாறுபடும் அல்லது முன்கணிக்க முடியாத"}, value="VARIABLE"),
                QuestionOption(option_id="sid_appt_weak",     text={"en": "Usually weak",           "hi": "आमतौर पर कमजोर",    "ta": "வழக்கமாக பலவீனமான"}, value="WEAK"),
            ],
            required=True,
            extraction_hints=["agni", "appetite", "hunger", "mukkuttram"],
            clinical_concept_id="SIDDHA:AGNI:APPETITE",
        ),
        Question(
            question_id="siddha_digestion",
            section="Digestion",
            text={
                "en": "How does your digestion feel on most days?",
                "hi": "अधिकतर दिनों में आपका पाचन कैसा लगता है?",
                "ta": "பெரும்பாலான நாட்களில் உங்கள் செரிமானம் எப்படி உணர்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_dig_good", text={"en": "Good, I feel comfortable",    "hi": "अच्छा, सहज लगता है",       "ta": "நன்றாக, வசதியாக உணர்கிறேன்"},       value="GOOD"),
                QuestionOption(option_id="sid_dig_bloated",text={"en": "I feel bloated or heavy",     "hi": "मुझे सूजन या भारीपन लगता है","ta": "வீக்கம் அல்லது கனம் உணர்கிறேன்"},   value="BLOATED"),
                QuestionOption(option_id="sid_dig_gas",   text={"en": "I have gas or acidity",       "hi": "मुझे गैस या एसिडिटी है",    "ta": "வாயு அல்லது அமிலத்தன்மை உண்டு"}, value="GAS"),
                QuestionOption(option_id="sid_dig_irregular",text={"en": "Irregular or unpredictable","hi": "अनियमित या अप्रत्याशित",    "ta": "வழக்கமற்ற அல்லது முன்கணிக்க முடியாத"}, value="IRREGULAR"),
            ],
            required=True,
            extraction_hints=["agni", "digestion", "mukkuttram"],
            clinical_concept_id="SIDDHA:AGNI:DIGESTION",
        ),
        Question(
            question_id="siddha_bowel",
            section="Digestion",
            text={
                "en": "How are your bowel habits most of the time?",
                "hi": "अधिकतर समय आपकी आंतों की आदतें कैसी रहती हैं?",
                "ta": "பெரும்பாலும் உங்கள் குடல் பழக்கம் எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_bowel_normal",    text={"en": "Normal and regular",    "hi": "सामान्य और नियमित",    "ta": "சாதாரணமான மற்றும் வழக்கமான"},  value="NORMAL"),
                QuestionOption(option_id="sid_bowel_constipated",text={"en": "Tendency to constipation","hi": "कब्ज की प्रवृत्ति",     "ta": "மலச்சிக்கல் சாத்தியம்"},         value="CONSTIPATED"),
                QuestionOption(option_id="sid_bowel_loose",    text={"en": "Loose or frequent",      "hi": "ढीला या बार-बार",     "ta": "தளர்வான அல்லது அடிக்கடி"},     value="LOOSE"),
            ],
            required=True,
            extraction_hints=["bowel", "mukkuttram", " Elimination"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:ELIMINATION",
        ),
        Question(
            question_id="siddha_sleep",
            section="General",
            text={
                "en": "How is your sleep generally?",
                "hi": "आपकी नींद आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் தூக்கம் பொதுவாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_sleep_good",  text={"en": "Sound and restful",        "hi": "गहरी और आरामदायक",      "ta": "ஆழமான மற்றும் அமைதியான"},   value="SOUND"),
                QuestionOption(option_id="sid_sleep_light", text={"en": "Light or easily disturbed",  "hi": "हल्की या आसानी से टूटती है","ta": "இலேசான அல்லது எளிதில் தடை"}, value="LIGHT"),
                QuestionOption(option_id="sid_sleep_less",  text={"en": "I sleep less than 6 hours", "hi": "मैं 6 घंटे से कम सोता हूँ",  "ta": "6 மணி நேரத்திற்கும் குறைவாக தூங்குகிறேன்"}, value="REDUCED"),
            ],
            required=True,
            extraction_hints=["sleep", "rest", "mukkuttram"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:SLEEP",
        ),
        Question(
            question_id="siddha_thermal",
            section="Constitution",
            text={
                "en": "Do you prefer cooler or warmer environments?",
                "hi": "आप ठंडे या गर्म वातावरण को क्यों पसंद करते हैं?",
                "ta": "குளிர்ச்சியான அல்லது வெம்மையான சூழலை நீங்கள் விரும்புகிறீர்களா?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_thermal_warm", text={"en": "I prefer warm environments",  "hi": "मुझे गर्म वातावरण पसंद है",  "ta": "வெம்மையான சூழலை விரும்புகிறேன்"},  value="WARM"),
                QuestionOption(option_id="sid_thermal_cool", text={"en": "I prefer cooler environments","hi": "मुझे ठंडा वातावरण पसंद है",  "ta": "குளிர்ச்சியான சூழலை விரும்புகிறேன்"},value="COOL"),
                QuestionOption(option_id="sid_thermal_both", text={"en": "No particular preference",     "hi": "कोई विशेष प्राथमिकता नहीं",   "ta": "குறிப்பிட்ட விருப்பம் இல்லை"},       value="NONE"),
            ],
            required=True,
            extraction_hints=["prakriti", "temperature", "mukkuttram"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:THERMAL",
        ),
        Question(
            question_id="siddha_skin_tendency",
            section="General",
            text={
                "en": "How does your skin generally behave?",
                "hi": "आपकी त्वचा आमतौर पर कैसे व्यवहार करती है?",
                "ta": "உங்கள் தோல் பொதுவாக எவ்வாறு செயல்படுகிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_skin_dry",   text={"en": "Tends to be dry",          "hi": "सूखने की प्रवृत्ति",         "ta": "உலர்வதற்கு சாத்தியம்"},        value="DRY"),
                QuestionOption(option_id="sid_skin_oily",  text={"en": "Tends to be oily",          "hi": "तैलीय होने की प्रवृत्ति",    "ta": "எண்ணெய் சாத்தியம்"},          value="OILY"),
                QuestionOption(option_id="sid_skin_normal", text={"en": "Generally normal",           "hi": "आमतौर पर सामान्य",          "ta": "பொதுவாக சாதாரணமான"},         value="NORMAL"),
            ],
            required=False,
            extraction_hints=["skin", "mukkuttram"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:SKIN",
        ),
        Question(
            question_id="siddha_mental",
            section="General",
            text={
                "en": "How would you describe your general mental temperament?",
                "hi": "आप अपने सामान्य मानसिक स्वभाव का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் பொதுவான மன தன்மையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="sid_ment_active",   text={"en": "Active and alert",         "hi": "सक्रिय और सतर्क",      "ta": "சுறுசுறுப்பான மற்றும் எச்சரிக்கை"}, value="ACTIVE"),
                QuestionOption(option_id="sid_ment_patient",   text={"en": "Patient and steady",        "hi": "धैर्यवान और स्थिर",     "ta": "பொறுமையான மற்றும் நிலையான"},   value="PATIENT"),
                QuestionOption(option_id="sid_ment_restless",   text={"en": "Restless or anxious",       "hi": "बेचैन या चिंतित",       "ta": "அமைதியற்ற அல்லது கவலையான"},   value="RESTLESS"),
            ],
            required=False,
            extraction_hints=["mind", "temperament", "mental"],
            clinical_concept_id="SIDDHA:MUKKUTTRAM:MENTAL",
        ),
        # Chief complaint
        Question(
            question_id="siddha_chief_complaint",
            section="Chief Complaint",
            text={
                "en": "What is the main health problem or symptom that brings you here today?",
                "hi": "आज आपको यहाँ लाने वाली मुख्य स्वास्थ्य समस्या या लक्षण क्या है?",
                "ta": "இன்று உங்களை இங்கு க带到 முக்கிய உடல் பிரச்சனை அல்லது அறிகுறி என்ன?",
            },
            field_type="text",
            required=True,
            extraction_hints=["chief_complaint", "symptom", "problem"],
            clinical_concept_id="SNOMED:404684003",
        ),
        Question(
            question_id="siddha_duration",
            section="Chief Complaint",
            text={
                "en": "How long have you had this problem?",
                "hi": "आपको यह समस्या कब से है?",
                "ta": "இந்த பிரச்சனை எவ்வாறு காலமாக உள்ளது?",
            },
            field_type="text",
            required=True,
            extraction_hints=["duration", "days", "weeks", "months", "years"],
            clinical_concept_id="SNOMED:103335007",
        ),
        Question(
            question_id="siddha_severity",
            section="Chief Complaint",
            text={
                "en": "On a scale of 0 to 10, how severe is this? (0 = no problem, 10 = most severe)",
                "hi": "0 से 10 के पैमाने पर, यह कितना गंभीर है? (0 = कोई समस्या नहीं, 10 = सबसे गंभीर)",
                "ta": "0 முதல் 10 வரையிலான அளவில், இது எவ்வளவு கடுமையானது? (0 = பிரச்சனை இல்லை, 10 = மிக கடுமையானது)",
            },
            field_type="number",
            required=True,
            extraction_hints=["severity", "pain scale"],
            clinical_concept_id="SNOMED:246112005",
        ),
    ]


# ─────────────────────────────────────────────────────────────
# UNANI  (~12 patient-friendly questions)
# ─────────────────────────────────────────────────────────────

def _make_unani_questions() -> List[Question]:
    return [
        Question(
            question_id="unani_thermal_nature",
            section="Constitution",
            text={
                "en": "Do you generally feel more comfortable in hot weather or cold weather?",
                "hi": "आपको आमतौर पर गर्म मौसम में सहज लगता है या ठंडे में?",
                "ta": "நீங்கள் பொதுவாக வெப்பமான காலநிலையில் அல்லது குளிர்ச்சியான காலநிலையில் அதிக வசதியாக உணர்கிறீர்களா?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_therm_hot",    text={"en": "I feel better in hot weather",    "hi": "गर्म मौसम में बेहतर लगता है",    "ta": "வெம்மையான காலநிலையில் சிறப்பாக உணர்கிறேன்"}, value="HOT_PREF"),
                QuestionOption(option_id="un_therm_cold",   text={"en": "I feel better in cold weather",   "hi": "ठंडे मौसम में बेहतर लगता है",   "ta": "குளிர்ச்சியான காலநிலையில் சிறப்பாக உணர்கிறேன்"}, value="COLD_PREF"),
                QuestionOption(option_id="un_therm_neutral",text={"en": "Weather doesn't affect me much",   "hi": "मौसम मुझे ज्यादा प्रभावित नहीं करता","ta": "காலநிலை என்னை அதிகம் பாதிக்காது"}, value="NEUTRAL"),
            ],
            required=True,
            extraction_hints=["mizaj", "temperature", "constitution"],
            clinical_concept_id="UNANI:MIZAJ:TEMPERAMENT",
        ),
        Question(
            question_id="unani_body_frame",
            section="Constitution",
            text={
                "en": "How would you describe your overall body frame?",
                "hi": "आप अपने समग्र शरीर की संरचना का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் ஒட்டுமொத்த உடல் அமைப்பை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_frame_slim",    text={"en": "Slim and light",                "hi": "पतला और हल्का",         "ta": "மெலிந்து லேசாக"},   value="SLIM"),
                QuestionOption(option_id="un_frame_medium",  text={"en": "Medium and well-proportioned",   "hi": "मध्यम और अच्छे अनुपात में", "ta": "நடுத்தர மற்றும் நன்கு விகிதாசார"}, value="MEDIUM"),
                QuestionOption(option_id="un_frame_heavyset",text={"en": "Broad and solidly built",         "hi": "चौड़ा और मजबूती से बना", "ta": "அகலமான மற்றும் உறுதியான கட்டமைப்பு"}, value="BROAD"),
            ],
            required=True,
            extraction_hints=["mizaj", "body", "constitution"],
            clinical_concept_id="UNANI:MIZAJ:BUILD",
        ),
        Question(
            question_id="unani_skin_type",
            section="Constitution",
            text={
                "en": "How would you describe your skin generally?",
                "hi": "आप अपनी त्वचा का सामान्य वर्णन कैसे करेंगे?",
                "ta": "உங்கள் தோலைப் பொதுவாக எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_skin_dry",    text={"en": "Dry and flaky",          "hi": "सूखी और छिलने वाली",  "ta": "உலர்ந்த மற்றும் செதிள்"},  value="DRY"),
                QuestionOption(option_id="un_skin_oily",   text={"en": "Oily or greasy",          "hi": "तैलीय या चिकनी",      "ta": "எண்ணெய் அல்லது கொழுப்பு"},value="OILY"),
                QuestionOption(option_id="un_skin_normal", text={"en": "Normal and balanced",      "hi": "सामान्य और संतुलित",   "ta": "சாதாரணமான மற்றும் சமநிலை"},value="NORMAL"),
            ],
            required=False,
            extraction_hints=["skin", "mizaj"],
            clinical_concept_id="UNANI:MIZAJ:SKIN",
        ),
        Question(
            question_id="unani_appetite",
            section="Digestion",
            text={
                "en": "How is your appetite usually?",
                "hi": "आपकी भूख आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் பசி வழக்கமாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_appt_strong",   text={"en": "Strong and regular",    "hi": "मजबूत और नियमित",   "ta": "வலுவான மற்றும் வழக்கமான"},  value="STRONG"),
                QuestionOption(option_id="un_appt_moderate", text={"en": "Moderate",               "hi": "मध्यम",              "ta": "மிதமான"},                  value="MODERATE"),
                QuestionOption(option_id="un_appt_weak",     text={"en": "Weak or poor",           "hi": "कमजोर या खराब",     "ta": "பலவீனமான அல்லது மோசமான"}, value="WEAK"),
            ],
            required=True,
            extraction_hints=["quwwat", "appetite", "digestion"],
            clinical_concept_id="UNANI:QUWWAT:DIGESTION",
        ),
        Question(
            question_id="unani_digestion",
            section="Digestion",
            text={
                "en": "How does your digestion feel on most days?",
                "hi": "अधिकतर दिनों में आपका पाचन कैसा लगता है?",
                "ta": "பெரும்பாலான நாட்களில் உங்கள் செரிமானம் எப்படி உணர்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_dig_good",    text={"en": "Good, no problems",       "hi": "अच्छा, कोई दिक्कत नहीं",   "ta": "நன்றாக, சிக்கல் இல்லை"},         value="GOOD"),
                QuestionOption(option_id="un_dig_heaviness",text={"en": "I feel heaviness after eating","hi":"खाने के बाद भारीपन लगता है","ta": "சாப்பிட்டபிறகு கனம் உணர்கிறேன்"}, value="HEAVINESS"),
                QuestionOption(option_id="un_dig_gas",     text={"en": "I have gas or bloating",   "hi": "मुझे गैस या सूजन होती है","ta": "வாயு அல்லது வீக்கம் உண்டு"},   value="GAS"),
                QuestionOption(option_id="un_dig_irregular",text={"en": "Irregular or unpredictable","hi": "अनियमित या अप्रत्याशित",   "ta": "வழக்கமற்ற அல்லது முன்கணிக்க முடியாத"}, value="IRREGULAR"),
            ],
            required=True,
            extraction_hints=["quwwat", "digestion", "stomach"],
            clinical_concept_id="UNANI:QUWWAT:DIGESTION",
        ),
        Question(
            question_id="unani_bowel",
            section="Digestion",
            text={
                "en": "How are your bowel movements usually?",
                "hi": "आपका मल त्याग आमतौर पर कैसा रहता है?",
                "ta": "உங்கள் குடல் இயக்கம் வழக்கமாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_bowel_normal",    text={"en": "Normal and regular",    "hi": "सामान्य और नियमित",     "ta": "சாதாரணமான மற்றும் வழக்கமான"}, value="NORMAL"),
                QuestionOption(option_id="un_bowel_constipated",text={"en": "Hard or difficult",      "hi": "कठोर या कठिन",         "ta": "கடினமான அல்லது கடினம்"},       value="CONSTIPATED"),
                QuestionOption(option_id="un_bowel_loose",      text={"en": "Loose or frequent",      "hi": "ढीला या बार-बार",      "ta": "தளர்வான அல்லது அடிக்கடி"},     value="LOOSE"),
            ],
            required=True,
            extraction_hints=["bowel", "istifragh", "elimination"],
            clinical_concept_id="UNANI:ISTIFRAGH:ELIMINATION",
        ),
        Question(
            question_id="unani_sleep",
            section="General",
            text={
                "en": "How is your sleep generally?",
                "hi": "आपकी नींद आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் தூக்கம் பொதுவாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_sleep_good",     text={"en": "Good and refreshing",    "hi": "अच्छी और ताज़ा करने वाली","ta": "நன்றாக மற்றும் புத்துணர்ச்சி அளிக்கும்"}, value="REFRESHING"),
                QuestionOption(option_id="un_sleep_disturbed",text={"en": "Disturbed or restless",     "hi": "बाधित या बेचैन",        "ta": "இடையூறான அல்லது அமைதியற்ற"}, value="DISTURBED"),
                QuestionOption(option_id="un_sleep_insomnia",text={"en": "I often cannot sleep",       "hi": "मुझे अक्सर नींद नहीं आती","ta": "அடிக்கடி தூங்க முடிவதில்லை"},    value="INSOMNIA"),
            ],
            required=True,
            extraction_hints=["nuum", "sleep", "rest"],
            clinical_concept_id="UNANI:NUUM:SLEEP",
        ),
        Question(
            question_id="unani_activity",
            section="Lifestyle",
            text={
                "en": "How would you describe your daily activity level?",
                "hi": "आप अपने दैनिक गतिविधि स्तर का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் தினசரி செயல்பாட்டு நிலையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_act_high",    text={"en": "Very active",          "hi": "बहुत सक्रिय",        "ta": "மிகவும் சுறுசுறுப்பான"}, value="HIGH"),
                QuestionOption(option_id="un_act_moderate", text={"en": "Moderately active",     "hi": "मध्यम सक्रिय",       "ta": "மிதமான சுறுசுறுப்பு"},   value="MODERATE"),
                QuestionOption(option_id="un_act_sedentary",text={"en": "Mostly resting",         "hi": "ज्यादातर आराम",       "ta": "பெரும்பாலும் ஓய்வு"},     value="LOW"),
            ],
            required=False,
            extraction_hints=["harakat", "activity", "exercise"],
            clinical_concept_id="UNANI:HARAKAT:ACTIVITY",
        ),
        Question(
            question_id="unani_mental",
            section="General",
            text={
                "en": "How would you describe your general temperament or mood?",
                "hi": "आप अपने सामान्य स्वभाव या मनोदशा का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் பொதுவான செயல்திறன் அல்லது மனநிலையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="un_ment_quick",  text={"en": "Quick and changeable",   "hi": "तेज़ और बदलने वाला",    "ta": "விரைவான மற்றும் மாறுபடும்"}, value="QUICK"),
                QuestionOption(option_id="un_ment_steady",  text={"en": "Steady and consistent",   "hi": "स्थिर और निरंतर",      "ta": "நிலையான மற்றும் சமநிலை"}, value="STEADY"),
                QuestionOption(option_id="un_ment_slow",    text={"en": "Slow and relaxed",        "hi": "धीमा और आरामदायक",     "ta": "மெதுவான மற்றும் அமைதியான"}, value="SLOW"),
            ],
            required=False,
            extraction_hints=["quwa", "mental", "temperament"],
            clinical_concept_id="UNANI:QUWA:MENTAL",
        ),
        # Chief complaint
        Question(
            question_id="unani_chief_complaint",
            section="Chief Complaint",
            text={
                "en": "What is the main health problem or symptom that brings you here today?",
                "hi": "आज आपको यहाँ लाने वाली मुख्य स्वास्थ्य समस्या या लक्षण क्या है?",
                "ta": "இன்று உங்களை இங்கு க brings முக்கிய உடல் பிரச்சனை அல்லது அறிகுறி என்ன?",
            },
            field_type="text",
            required=True,
            extraction_hints=["chief_complaint", "symptom", "problem"],
            clinical_concept_id="SNOMED:404684003",
        ),
        Question(
            question_id="unani_duration",
            section="Chief Complaint",
            text={
                "en": "How long have you had this problem?",
                "hi": "आपको यह समस्या कब से है?",
                "ta": "இந்த பிரச்சனை எவ்வாறு காலமாக உள்ளது?",
            },
            field_type="text",
            required=True,
            extraction_hints=["duration", "days", "weeks", "months", "years"],
            clinical_concept_id="SNOMED:103335007",
        ),
        Question(
            question_id="unani_severity",
            section="Chief Complaint",
            text={
                "en": "On a scale of 0 to 10, how severe is this? (0 = no problem, 10 = most severe)",
                "hi": "0 से 10 के पैमाने पर, यह कितना गंभीर है? (0 = कोई समस्या नहीं, 10 = सबसे गंभीर)",
                "ta": "0 முதல் 10 வரையிலான அளவில், இது எவ்வளவு கடுமையானது? (0 = பிரச்சனை இல்லை, 10 = மிக கடுமையானது)",
            },
            field_type="number",
            required=True,
            extraction_hints=["severity", "pain scale"],
            clinical_concept_id="SNOMED:246112005",
        ),
    ]


# ─────────────────────────────────────────────────────────────
# HOMOEOPATHY  (~12 patient-friendly questions)
# ─────────────────────────────────────────────────────────────

def _make_homoeopathy_questions() -> List[Question]:
    return [
        Question(
            question_id="hom_chief_complaint",
            section="Chief Complaint",
            text={
                "en": "What is the main health problem or symptom that brings you here today?",
                "hi": "आज आपको यहाँ लाने वाली मुख्य स्वास्थ्य समस्या या लक्षण क्या है?",
                "ta": "இன்று உங்களை இங்கு க brings முக்கிய உடல் பிரச்சனை அல்லது அறிகுறி என்ன?",
            },
            field_type="text",
            required=True,
            extraction_hints=["chief_complaint", "symptom", "problem"],
            clinical_concept_id="SNOMED:404684003",
        ),
        Question(
            question_id="hom_onset",
            section="History",
            text={
                "en": "When did this problem start?",
                "hi": "यह समस्या कब शुरू हुई?",
                "ta": "இந்த பிரச்சனை எப்போது தொடங்கியது?",
            },
            field_type="text",
            required=True,
            extraction_hints=["onset", "started", "began", "since"],
            clinical_concept_id="SNOMED:85585009",
        ),
        Question(
            question_id="hom_cause",
            section="History",
            text={
                "en": "What do you think may have caused or triggered this problem?",
                "hi": "आपको क्या लगता है कि इस समस्या का कारण या उत्तेजना क्या हो सकता है?",
                "ta": "இந்த பிரச்சனைக்கு காரணம் அல்லது தூண்டுதலாக இருக்கக்கூடியது என்ன?",
            },
            field_type="text",
            required=False,
            extraction_hints=["cause", "trigger", "reason", "etiology"],
            clinical_concept_id="SNOMED:248152002",
        ),
        Question(
            question_id="hom_severity",
            section="History",
            text={
                "en": "On a scale of 0 to 10, how severe is this? (0 = no problem, 10 = most severe)",
                "hi": "0 से 10 के पैमाने पर, यह कितना गंभीर है? (0 = कोई समस्या नहीं, 10 = सबसे गंभीर)",
                "ta": "0 முதல் 10 வரையிலான அளவில், இது எவ்வளவு கடுமையானது? (0 = பிரச்சனை இல்லை, 10 = மிக கடுமையானது)",
            },
            field_type="number",
            required=True,
            extraction_hints=["severity", "pain scale"],
            clinical_concept_id="SNOMED:246112005",
        ),
        Question(
            question_id="hom_modality_better",
            section="Modalities",
            text={
                "en": "What makes this problem feel better?",
                "hi": "इस समस्या को क्या बेहतर लगाता है?",
                "ta": "இந்த பிரச்சனையை என்ன சிறப்பாக உணர வைக்கிறது?",
            },
            field_type="text",
            required=False,
            extraction_hints=["better", "improves", "relieves", "modality"],
            clinical_concept_id="SNOMED:370847009",
        ),
        Question(
            question_id="hom_modality_worse",
            section="Modalities",
            text={
                "en": "What makes this problem feel worse?",
                "hi": "इस समस्या को क्या बदतर लगाता है?",
                "ta": "இந்த பிரச்சனையை என்ன மோசமாக உணர வைக்கிறது?",
            },
            field_type="text",
            required=False,
            extraction_hints=["worse", "aggravates", "modality"],
            clinical_concept_id="SNOMED:370847009",
        ),
        Question(
            question_id="hom_thermal",
            section="General",
            text={
                "en": "Do you generally prefer warmth or coolness?",
                "hi": "आपको आमतौर पर गर्मी पसंद है या ठंड?",
                "ta": "நீங்கள் பொதுவாக வெம்மையையா அல்லது குளிர்ச்சியையா விரும்புகிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="hom_therm_warm",  text={"en": "I prefer warmth",           "hi": "मुझे गर्मी पसंद है",     "ta": "வெம்மையை விரும்புகிறேன்"},   value="WARM"),
                QuestionOption(option_id="hom_therm_cool",  text={"en": "I prefer coolness",          "hi": "मुझे ठंड पसंद है",      "ta": "குளிர்ச்சியை விரும்புகிறேன்"}, value="COOL"),
                QuestionOption(option_id="hom_therm_indiff",text={"en": "Neither makes a difference",  "hi": "कोई फर्क नहीं पड़ता",     "ta": "எந்த வித்தியாசமும் இல்லை"},   value="INDIFFERENT"),
            ],
            required=False,
            extraction_hints=["temperature", "thermal", "general"],
            clinical_concept_id="SNOMED:364853009",
        ),
        Question(
            question_id="hom_thirst",
            section="General",
            text={
                "en": "How is your thirst usually?",
                "hi": "आपकी प्यास आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் தாகம் வழக்கமாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="hom_thirst_large",  text={"en": "I drink large quantities", "hi": "मैं बड़ी मात्रा में पीता हूँ","ta": "அதிக அளவில் குடிக்கிறேன்"},    value="LARGE"),
                QuestionOption(option_id="hom_thirst_small",  text={"en": "I drink small sips",       "hi": "मैं छोटे घूंट पीता हूँ",    "ta": "சிறிய குடிப்பழக்கம்"},         value="SMALL"),
                QuestionOption(option_id="hom_thirst_none",   text={"en": "I don't feel thirsty",      "hi": "मुझे प्यास नहीं लगती",    "ta": "தாகம் உணர்வதில்லை"},          value="NONE"),
            ],
            required=False,
            extraction_hints=["thirst", "general"],
            clinical_concept_id="SNOMED:267036007",
        ),
        Question(
            question_id="hom_appetite",
            section="General",
            text={
                "en": "How is your appetite generally?",
                "hi": "आपकी भूख आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் பசி வழக்கமாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="hom_appt_increased", text={"en": "Increased or unusual",   "hi": "बढ़ा हुआ या असामान्य", "ta": "அதிகரித்த அல்லது அசாதாரண"},  value="INCREASED"),
                QuestionOption(option_id="hom_appt_normal",    text={"en": "Normal",                "hi": "सामान्य",             "ta": "சாதாரணமான"},               value="NORMAL"),
                QuestionOption(option_id="hom_appt_decreased",text={"en": "Decreased or poor",     "hi": "कम या खराब",         "ta": "குறைந்த அல்லது மோசமான"},    value="DECREASED"),
            ],
            required=False,
            extraction_hints=["appetite", "hunger"],
            clinical_concept_id="SNOMED:366979004",
        ),
        Question(
            question_id="hom_sleep",
            section="General",
            text={
                "en": "How is your sleep generally?",
                "hi": "आपकी नींद आमतौर पर कैसी रहती है?",
                "ta": "உங்கள் தூக்கம் பொதுவாக எப்படி இருக்கிறது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="hom_sleep_good",   text={"en": "Good and restful",       "hi": "अच्छी और आरामदायक",       "ta": "நன்றாக மற்றும் அமைதியான"},      value="RESTFUL"),
                QuestionOption(option_id="hom_sleep_disturb", text={"en": "Disturbed or restless",   "hi": "बाधित या बेचैन",           "ta": "இடையூறான அல்லது அமைதியற்ற"},   value="DISTURBED"),
                QuestionOption(option_id="hom_sleep_position",text={"en": "I need a particular position","hi": "मुझे एक विशेष स्थिति चाहिए","ta": "ஒரு குறிப்பிட்ட நிலை தேவை"},   value="POSITION"),
            ],
            required=False,
            extraction_hints=["sleep", "rest", "position"],
            clinical_concept_id="SNOMED:162397009",
        ),
        Question(
            question_id="hom_emotional",
            section="General",
            text={
                "en": "How would you describe your general emotional state lately?",
                "hi": "आप हाल के दिनों में अपनी सामान्य भावनात्मक स्थिति का वर्णन कैसे करेंगे?",
                "ta": "இல்லிய நேரங்களில் உங்கள் பொதுவான உணர்ச்சி நிலையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="hom_emo_calm",    text={"en": "Calm and composed",        "hi": "शांत और संयत",      "ta": "அமைதியான மற்றும் கட்டுப்பாட்டில்"}, value="CALM"),
                QuestionOption(option_id="hom_emo_anxious", text={"en": "Anxious or worried",        "hi": "चिंतित या परेशान",  "ta": "கவலையான அல்லது கவலை"},         value="ANXIOUS"),
                QuestionOption(option_id="hom_emo_irrit",   text={"en": "Irritable or easily angered","hi":"चिड़चिड़ा या गुस्सा",  "ta": "எரிச்சலான அல்லது எளிதில் கோபம்"}, value="IRRITABLE"),
                QuestionOption(option_id="hom_emo_sad",    text={"en": "Sad or low",                "hi": "उदास या नीचा",     "ta": "வருத்தமான அல்லது குறைந்த"},    value="SAD"),
            ],
            required=False,
            extraction_hints=["emotional", "mental", "general"],
            clinical_concept_id="SNOMED:38362003",
        ),
    ]


# ─────────────────────────────────────────────────────────────
# YOGA & NATUROPATHY  (~12 patient-friendly questions)
# ─────────────────────────────────────────────────────────────

def _make_yoga_questions() -> List[Question]:
    return [
        Question(
            question_id="yoga_chief_complaint",
            section="Chief Complaint",
            text={
                "en": "What is the main health concern or symptom that brings you here today?",
                "hi": "आज आपको यहाँ लाने वाली मुख्य स्वास्थ्य चिंता या लक्षण क्या है?",
                "ta": "இன்று உங்களை இங்கு க brings முக்கிய உடல் கவலை அல்லது அறிகுறி என்ன?",
            },
            field_type="text",
            required=True,
            extraction_hints=["chief_complaint", "symptom", "problem"],
            clinical_concept_id="SNOMED:404684003",
        ),
        Question(
            question_id="yoga_duration",
            section="History",
            text={
                "en": "How long have you had this concern?",
                "hi": "आपको यह चिंता कब से है?",
                "ta": "இந்த கவலை எவ்வாறு காலமாக உள்ளது?",
            },
            field_type="text",
            required=True,
            extraction_hints=["duration", "days", "weeks", "months", "years"],
            clinical_concept_id="SNOMED:103335007",
        ),
        Question(
            question_id="yoga_physical_activity",
            section="Lifestyle",
            text={
                "en": "How would you describe your current level of physical activity?",
                "hi": "आप अपने वर्तमान शारीरिक गतिविधि के स्तर का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் தற்போதைய உடல் செயல்பாட்டு நிலையை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_act_regular", text={"en": "I exercise regularly (3+ times/week)", "hi": "मैं नियमित व्यायाम करता हूँ (सप्ताह में 3+ बार)","ta": "வழக்கமாக உடற்பயிற்சி செய்கிறேன் (வாரத்திற்கு 3+ முறை)"}, value="REGULAR"),
                QuestionOption(option_id="yoga_act_occasional",text={"en": "I am occasionally active",            "hi": "मैं कभी-कभी सक्रिय रहता हूँ",           "ta": "சில நேரங்களில் சுறுசுறுப்பாக இருக்கிறேன்"}, value="OCCASIONAL"),
                QuestionOption(option_id="yoga_act_sedentary",text={"en": "Mostly sitting, minimal activity",     "hi": "ज्यादातर बैठा, न्यूनतम गतिविधि",        "ta": "பெரும்பாலும் உட்கார்ந்து, குறைந்த செயல்பாடு"}, value="LOW"),
            ],
            required=True,
            extraction_hints=["exercise", "activity", "physical"],
            clinical_concept_id="SNOMED:68130003",
        ),
        Question(
            question_id="yoga_sleep",
            section="Lifestyle",
            text={
                "en": "How many hours do you sleep on average per night?",
                "hi": "आप औसतन प्रति रात कितने घंटे सोते हैं?",
                "ta": "சராசரியாக ஒவ்வொரு இரவும் எவ்வளவு மணி நேரம் தூங்குகிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_sleep_lt6",  text={"en": "Less than 6 hours",  "hi": "6 घंटे से कम",   "ta": "6 மணி நேரத்திற்கும் குறைவாக"}, value="LT6"),
                QuestionOption(option_id="yoga_sleep_6to8", text={"en": "6 to 8 hours",        "hi": "6 से 8 घंटे",    "ta": "6 முதல் 8 மணி"},                value="6TO8"),
                QuestionOption(option_id="yoga_sleep_gt8",   text={"en": "More than 8 hours",   "hi": "8 घंटे से अधिक", "ta": "8 மணி நேரத்திற்கும் மேல்"},      value="GT8"),
            ],
            required=True,
            extraction_hints=["sleep", "rest", "hours"],
            clinical_concept_id="SNOMED:162397009",
        ),
        Question(
            question_id="yoga_diet",
            section="Diet",
            text={
                "en": "How would you describe your current diet?",
                "hi": "आप अपने वर्तमान आहार का वर्णन कैसे करेंगे?",
                "ta": "உங்கள் தற்போதைய உணவை எப்படி விவரிப்பீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_diet_veg",      text={"en": "Mostly vegetarian",   "hi": "ज्यादातर शाकाहारी",   "ta": "பெரும்பாலும் சைவ"},      value="VEGETARIAN"),
                QuestionOption(option_id="yoga_diet_mixed",    text={"en": "Mixed vegetarian/non-veg","hi":"मिश्रित",               "ta": "கலப்பு"},                value="MIXED"),
                QuestionOption(option_id="yoga_diet_processed", text={"en": "High in processed food","hi": "प्रोसेस्ड फूड में उच्च","ta": "செயலாக்கப்பட்ட உணவு அதிகம்"}, value="PROCESSED"),
            ],
            required=True,
            extraction_hints=["diet", "food", "nutrition"],
            clinical_concept_id="SNOMED:151082008",
        ),
        Question(
            question_id="yoga_hydration",
            section="Lifestyle",
            text={
                "en": "How much water do you drink per day approximately?",
                "hi": "आप प्रतिदिन लगभग कितना पानी पीते हैं?",
                "ta": "ஒவ்வொரு நாளும் எவ்வளவு தண்ணீர் குடிக்கிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_hyd_low",  text={"en": "Less than 4 glasses",   "hi": "4 गिलास से कम",   "ta": "4 ஒட்டைக்கும் குறைவாக"}, value="LOW"),
                QuestionOption(option_id="yoga_hyd_mid",  text={"en": "4 to 8 glasses",         "hi": "4 से 8 गिलास",    "ta": "4 முதல் 8 ஒட்டை"},       value="MID"),
                QuestionOption(option_id="yoga_hyd_high", text={"en": "More than 8 glasses",     "hi": "8 गिलास से अधिक", "ta": "8 ஒட்டைக்கும் மேல்"},     value="HIGH"),
            ],
            required=False,
            extraction_hints=["water", "hydration", "fluids"],
            clinical_concept_id="SNOMED:226854008",
        ),
        Question(
            question_id="yoga_stress",
            section="Lifestyle",
            text={
                "en": "How would you rate your current stress level?",
                "hi": "आप अपने वर्तमान तनाव स्तर को कैसे रेट करेंगे?",
                "ta": "உங்கள் தற்போதைய மன அழுத்த நிலையை எப்படி மதிப்பிடுவீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_stress_low",    text={"en": "Low / manageable",      "hi": "कम / प्रबंधनीय",       "ta": "குறைவான / நிர்வகிக்கக்கூடிய"}, value="LOW"),
                QuestionOption(option_id="yoga_stress_moderate",text={"en": "Moderate",              "hi": "मध्यम",                   "ta": "மிதமான"},                     value="MODERATE"),
                QuestionOption(option_id="yoga_stress_high",   text={"en": "High / overwhelming",   "hi": "उच्च / अभिभूत करने वाला","ta": "உயர் / அழுத்தமான"},             value="HIGH"),
            ],
            required=True,
            extraction_hints=["stress", "mental", "psychological"],
            clinical_concept_id="SNOMED:36592006",
        ),
        Question(
            question_id="yoga_breathing",
            section="Lifestyle",
            text={
                "en": "Do you practice any breathing exercises (pranayama) or yoga?",
                "hi": "क्या आप कोई श्वास व्यायाम (प्राणायाम) या योग करते हैं?",
                "ta": "நீங்கள் ஏதேனும் சுவாசம் பயிற்சி (பிராணாயாமம்) அல்லது யோகா செய்கிறீர்களா?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_breath_yes", text={"en": "Yes, regularly",   "hi": "हाँ, नियमित रूप से", "ta": "ஆம், வழக்கமாக"},   value="REGULAR"),
                QuestionOption(option_id="yoga_breath_occ", text={"en": "Yes, occasionally","hi": "कभी-कभी",         "ta": "சில நேரங்களில்"},   value="OCCASIONAL"),
                QuestionOption(option_id="yoga_breath_no",  text={"en": "No",              "hi": "नहीं",            "ta": "இல்லை"},          value="NO"),
            ],
            required=False,
            extraction_hints=["pranayama", "breathing", "yoga"],
            clinical_concept_id="SNOMED:284558009",
        ),
        Question(
            question_id="yoga_routine",
            section="Lifestyle",
            text={
                "en": "How regular is your daily routine (sleep, meals, wake times)?",
                "hi": "आपकी दिनचर्या कितनी नियमित है (नींद, भोजन, जागने का समय)?",
                "ta": "உங்கள் தினசரி வழக்கம் (தூக்கம், உணவு, விழிப்பு நேரம்) எவ்வளவு வழக்கமானது?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_rout_regular",  text={"en": "Very regular",     "hi": "बहुत नियमित",   "ta": "மிகவும் வழக்கமான"},  value="REGULAR"),
                QuestionOption(option_id="yoga_rout_somewhat",  text={"en": "Somewhat regular", "hi": "कुछ हद तक नियमित","ta": "கொஞ்சம் வழக்கமான"},value="SOMEWHAT"),
                QuestionOption(option_id="yoga_rout_irregular", text={"en": "Irregular",        "hi": "अनियमित",       "ta": "வழக்கமற்ற"},        value="IRREGULAR"),
            ],
            required=False,
            extraction_hints=["routine", "lifestyle", "dinacharya"],
            clinical_concept_id="SNOMED:409073007",
        ),
        Question(
            question_id="yoga_sedentary",
            section="Lifestyle",
            text={
                "en": "How many hours per day do you spend sitting?",
                "hi": "आप दिन में कितने घंटे बैठते हैं?",
                "ta": "ஒவ்வொரு நாளும் நீங்கள் எவ்வளவு மணி நேரம் உட்காருகிறீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_sed_lt4",  text={"en": "Less than 4 hours",  "hi": "4 घंटे से कम",   "ta": "4 மணி நேரத்திற்கும் குறைவாக"}, value="LT4"),
                QuestionOption(option_id="yoga_sed_4to8", text={"en": "4 to 8 hours",        "hi": "4 से 8 घंटे",    "ta": "4 முதல் 8 மணி"},               value="4TO8"),
                QuestionOption(option_id="yoga_sed_gt8",  text={"en": "More than 8 hours",   "hi": "8 घंटे से अधिक", "ta": "8 மணி நேரத்திற்கும் மேல்"},      value="GT8"),
            ],
            required=False,
            extraction_hints=["sedentary", "sitting", "screen"],
            clinical_concept_id="SNOMED:68130003",
        ),
        Question(
            question_id="yoga_wellbeing",
            section="General",
            text={
                "en": "Overall, how would you rate your general sense of well-being?",
                "hi": "कुल मिलाकर, आप अपनी सामान्य भलाई की भावना को कैसे रेट करेंगे?",
                "ta": "மொத்தத்தில், உங்கள் பொதுவான நல்வாழ்வு உணர்வை எப்படி மதிப்பிடுவீர்கள்?",
            },
            field_type="single_choice",
            options=[
                QuestionOption(option_id="yoga_wb_good",    text={"en": "Good, I feel well",          "hi": "अच्छा, मैं अच्छा महसूस करता हूँ","ta": "நன்றாக, நான் நன்றாக உணர்கிறேன்"}, value="GOOD"),
                QuestionOption(option_id="yoga_wb_fair",   text={"en": "Fair, could be better",       "hi": "ठीक, बेहतर हो सकता है",          "ta": "சராசரி, மேம்படுத்தலாம்"},         value="FAIR"),
                QuestionOption(option_id="yoga_wb_poor",   text={"en": "Poor, I have been unwell",     "hi": "खराब, मैं बीमार रहा हूँ",        "ta": "மோசமான, உடல்நலக் குறைபாடு"},   value="POOR"),
            ],
            required=False,
            extraction_hints=["wellbeing", "general", "overall"],
            clinical_concept_id="SNOMED:365848003",
        ),
    ]


# ─────────────────────────────────────────────────────────────
# ALLOPATHY — delegate to existing questionnaire_schema
# ─────────────────────────────────────────────────────────────

def get_allopathy_questionnaire() -> List[Question]:
    from app.services.conversation.questionnaire_schema import get_allopathy_questionnaire as _get
    return _get()


# ─────────────────────────────────────────────────────────────
# UNIFIED LOADER
# ─────────────────────────────────────────────────────────────

def get_questionnaire(mode: str, stream: Optional[str] = None) -> List[Question]:
    """
    Return the appropriate questionnaire for a given mode and stream.

    Args:
        mode: "allopathy" | "ayush"
        stream: Required when mode is "ayush".
                One of: "ayurveda" | "siddha" | "unani" | "homoeopathy" | "yoga_naturopathy"

    Returns:
        List of Question objects for the given mode/stream.

    Raises:
        ValueError: If mode/stream combination is invalid.
    """
    mode = mode.lower() if mode else "allopathy"

    if mode == "allopathy":
        return get_allopathy_questionnaire()

    if mode == "ayush":
        if not stream:
            stream = "ayurveda"  # safe default

        stream_map = {
            "ayurveda":          _make_ayurveda_questions,
            "siddha":            _make_siddha_questions,
            "unani":             _make_unani_questions,
            "homoeopathy":       _make_homoeopathy_questions,
            "yoga_naturopathy":  _make_yoga_questions,
        }

        loader = stream_map.get(stream.lower())
        if not loader:
            raise ValueError(f"Unknown AYUSH stream: {stream!r}. Valid: {list(stream_map.keys())}")
        return loader()

    raise ValueError(f"Unknown mode: {mode!r}. Expected 'allopathy' or 'ayush'.")


def get_questionnaire_summary(mode: str, stream: Optional[str] = None) -> Dict[str, Any]:
    """Return a lightweight summary of the questionnaire (sections, question count)."""
    questions = get_questionnaire(mode, stream)
    sections = list(dict.fromkeys(q.section for q in questions))
    required = sum(1 for q in questions if q.required)
    return {
        "mode": mode,
        "stream": stream,
        "total_questions": len(questions),
        "required_questions": required,
        "sections": sections,
    }
