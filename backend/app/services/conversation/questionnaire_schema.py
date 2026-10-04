"""
Allopathy questionnaire schema.

Data-driven clinical history questionnaire based on SOCRATES/HPI.
"""
from typing import Dict, List, Any
from app.schemas.conversation import Question, QuestionOption


# Section definitions
SECTIONS = [
    "chief_complaint",
    "hpi",
    "past_history",
    "medications",
    "allergies",
    "family_history",
    "personal_history",
    "review_of_systems"
]


def get_allopathy_questionnaire() -> List[Question]:
    """
    Get the complete allopathy questionnaire.

    Returns a data-driven list of questions with multilingual support.
    """
    questions = []

    # Chief Complaint
    questions.append(Question(
        question_id="cc_main",
        section="chief_complaint",
        text={
            "en": "What is the main problem or complaint that brings you here today?",
            "hi": "आज आपको यहां लाने वाली मुख्य समस्या या शिकायत क्या है?",
            "ta": "இன்று உங்களுக்கு என்ன பிரச்சனை அல்லது முறைப்பாடு உள்ளது?",
            "te": "ఈ రోజు మిమ్మల్ని ఇక్కడికి తీసుకొచ్చిన ప్రధాన సమస్య లేదా ఫిర్యాదు ఏమిటి?",
            "ml": "ഇന്ന് നിങ്ങളെ ഇവിടെ കൊണ്ടുവന്ന പ്രധാന പ്രശ്നം അല്ലെങ്കിൽ പരാതി എന്താണ്?",
        },
        field_type="text",
        required=True,
        extraction_hints=["symptom", "complaint", "problem"],
        clinical_concept_id="SNOMED:404684003"
    ))

    questions.append(Question(
        question_id="cc_details",
        section="chief_complaint",
        text={
            "en": "Can you describe this problem in more detail?",
            "hi": "क्या आप इस समस्या का अधिक विस्तार से वर्णन कर सकते हैं?",
            "ta": "இந்த பிரச்சனையை இன்னும் விரிவாக விவரிக்க முடியுமா?",
            "te": "మీరు ఈ సమస్యను మరింత వివరంగా వివరించగలరా?",
            "ml": "ഈ പ്രശ്നം കൂടുതൽ വിശദമായി വിവരിക്കാമോ?",
        },
        field_type="text",
        required=False,
        extraction_hints=["details", "description"],
        clinical_concept_id="SNOMED:404684003"
    ))

    # Onset
    questions.append(Question(
        question_id="onset",
        section="hpi",
        text={
            "en": "When did this problem start?",
            "hi": "यह समस्या कब शुरू हुई?",
            "ta": "இந்த பிரச்சனை எப்போது தொடங்கியது?",
            "te": "ఈ సమస్య ఎప్పుడు ప్రారంభమైంది?",
            "ml": "ഈ പ്രശ്നം എപ്പോൾ ആരംഭിച്ചു?",
        },
        field_type="text",
        required=True,
        extraction_hints=["onset", "started", "began", "since"],
        clinical_concept_id="SNOMED:85585009"
    ))

    # Duration
    questions.append(Question(
        question_id="duration",
        section="hpi",
        text={
            "en": "How long have you had this problem?",
            "hi": "आपको यह समस्या कब से है?",
            "ta": "இந்த பிரச்சனை எவ்வளவு காலமாக உள்ளது?",
            "te": "మీకు ఈ సమస్య ఎంతకాలంగా ఉంది?",
            "ml": "ഈ പ്രശ്നം എത്രനാളായി ഉണ്ട്?",
        },
        field_type="text",
        required=True,
        extraction_hints=["duration", "days", "weeks", "months", "years", "hours"],
        clinical_concept_id="SNOMED:103335007"
    ))

    # Severity
    questions.append(Question(
        question_id="severity",
        section="hpi",
        text={
            "en": "On a scale of 0 to 10, how severe is this problem? (0 = no problem, 10 = worst imaginable)",
            "hi": "0 से 10 के पैमाने पर, यह समस्या कितनी गंभीर है? (0 = कोई समस्या नहीं, 10 = सबसे बुरी कल्पनीय)",
            "ta": "0 முதல் 10 வரையிலான அளவில், இந்த பிரச்சனை எவ்வளவு கடுமையானது? (0 = பிரச்சனை இல்லை, 10 = மிக மோசமானது)",
            "te": "0 నుండి 10 స్కేల్‌లో, ఈ సమస్య ఎంత తీవ్రంగా ఉంది? (0 = సమస్య లేదు, 10 = చాలా చెత్తది)",
            "ml": "0 മുതൽ 10 വരെയുള്ള സ്കെയിലിൽ, ഈ പ്രശ്നം എത്ര ഗുരുതരമാണ്? (0 = പ്രശ്നമില്ല, 10 = ഏറ്റവും മോശം)",
        },
        field_type="number",
        required=True,
        extraction_hints=["severity", "pain scale", "rating", "out of 10"],
        clinical_concept_id="SNOMED:246112005"
    ))

    # Location
    questions.append(Question(
        question_id="location",
        section="hpi",
        text={
            "en": "Where exactly is the problem located?",
            "hi": "समस्या ठीक कहाँ स्थित है?",
            "ta": "பிரச்சனை சரியாக எங்கே உள்ளது?",
            "te": "సమస్య ఖచ్చితంగా ఎక్కడ ఉంది?",
            "ml": "പ്രശ്നം കൃത്യമായി എവിടെയാണ്?",
        },
        field_type="text",
        required=False,
        extraction_hints=["location", "where", "site", "body part"],
        clinical_concept_id="SNOMED:246267002"
    ))

    # Character
    questions.append(Question(
        question_id="character",
        section="hpi",
        text={
            "en": "How would you describe the character or quality of this problem? (e.g., sharp, dull, throbbing, burning)",
            "hi": "आप इस समस्या के चरित्र या गुणवत्ता का वर्णन कैसे करेंगे? (जैसे, तीव्र, सुस्त, धड़कता हुआ, जलन)",
            "ta": "இந்த பிரச்சனையின் தன்மை அல்லது தரத்தை எவ்வாறு விவரிப்பீர்கள்? (எ.கா., கூர்மையான, மந்தமான, துடிக்கும், எரியும்)",
            "te": "ఈ సమస్య యొక్క స్వభావం లేదా నాణ్యతను మీరు ఎలా వివరిస్తారు? (ఉదా., పదునైన, నిస్తేజమైన, కొట్టుకునే, కాలిపోయే)",
            "ml": "ഈ പ്രശ്നത്തിന്റെ സ്വഭാവമോ ഗുണമോ നിങ്ങൾ എങ്ങനെ വിവരിക്കും? (ഉദാ., മൂർച്ചയുള്ള, മന്ദമായ, പിടിമുറുക്കുന്ന, പൊള്ളുന്ന)",
        },
        field_type="text",
        required=False,
        extraction_hints=["character", "quality", "type", "sharp", "dull", "burning"],
        clinical_concept_id="SNOMED:246464006"
    ))

    # Radiation
    questions.append(Question(
        question_id="radiation",
        section="hpi",
        text={
            "en": "Does the problem spread or radiate to any other area?",
            "hi": "क्या समस्या किसी अन्य क्षेत्र में फैलती है या विकीर्ण होती है?",
            "ta": "பிரச்சனை வேறு எந்த பகுதிக்கும் பரவுகிறதா அல்லது கதிர்வீச்சு செய்கிறதா?",
            "te": "సమస్య ఏదైనా ఇతర ప్రాంతానికి వ్యాపిస్తుందా లేదా రేడియేట్ అవుతుందా?",
            "ml": "പ്രശ്നം മറ്റേതെങ്കിലും പ്രദേശത്തേക്ക് വ്യാപിക്കുന്നുണ്ടോ അല്ലെങ്കിൽ റേഡിയേറ്റ് ചെയ്യുന്നുണ്ടോ?",
        },
        field_type="text",
        required=False,
        extraction_hints=["radiation", "spread", "radiate", "travels"],
        clinical_concept_id="SNOMED:228828009"
    ))

    # Progression
    questions.append(Question(
        question_id="progression",
        section="hpi",
        text={
            "en": "Is the problem getting better, worse, or staying the same?",
            "hi": "क्या समस्या बेहतर हो रही है, बदतर हो रही है, या वैसी ही बनी हुई है?",
            "ta": "பிரச்சனை மேம்படுகிறதா, மோசமாகிறதா அல்லது அப்படியே உள்ளதா?",
            "te": "సమస్య మెరుగుపడుతుందా, దిగజారుతుందా లేదా అలాగే ఉందా?",
            "ml": "പ്രശ്നം മെച്ചപ്പെടുകയാണോ, വഷളാവുകയാണോ അതോ അതേപടി തുടരുകയാണോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(
                option_id="prog_better",
                text={"en": "Getting better", "hi": "बेहतर हो रहा है", "ta": "மேம்படுகிறது", "te": "మెరుగుపడుతోంది", "ml": "മെച്ചപ്പെടുന്നു"},
                value="improving"
            ),
            QuestionOption(
                option_id="prog_worse",
                text={"en": "Getting worse", "hi": "बदतर हो रहा है", "ta": "மோசமாகிறது", "te": "దిగజారుతోంది", "ml": "വഷളാവുന്നു"},
                value="worsening"
            ),
            QuestionOption(
                option_id="prog_same",
                text={"en": "Staying the same", "hi": "वैसा ही है", "ta": "அப்படியே உள்ளது", "te": "అలాగే ఉంది", "ml": "അതേപടി"},
                value="stable"
            ),
        ],
        required=False,
        extraction_hints=["progression", "better", "worse", "same", "improving"],
        clinical_concept_id="SNOMED:246455001"
    ))

    # Associated symptoms
    questions.append(Question(
        question_id="associated_symptoms",
        section="hpi",
        text={
            "en": "Do you have any other symptoms along with this problem?",
            "hi": "क्या इस समस्या के साथ आपको कोई अन्य लक्षण हैं?",
            "ta": "இந்த பிரச்சனையுடன் வேறு ஏதேனும் அறிகுறிகள் உள்ளதா?",
            "te": "ఈ సమస్యతో పాటు మీకు ఏదైనా ఇతర లక్షణాలు ఉన్నాయా?",
            "ml": "ഈ പ്രശ്നത്തോടൊപ്പം മറ്റേതെങ്കിലും ലക്ഷണങ്ങൾ ഉണ്ടോ?",
        },
        field_type="text",
        required=False,
        extraction_hints=["associated symptoms", "other symptoms", "along with"],
        clinical_concept_id="SNOMED:418799008"
    ))

    # Past Medical History
    questions.append(Question(
        question_id="pmh_any",
        section="past_history",
        text={
            "en": "Do you have any past medical conditions or chronic diseases?",
            "hi": "क्या आपको कोई पिछली चिकित्सीय स्थितियां या पुरानी बीमारियां हैं?",
            "ta": "உங்களுக்கு ஏதேனும் கடந்தகால மருத்துவ நிலைகள் அல்லது நாள்பட்ட நோய்கள் உள்ளதா?",
            "te": "మీకు గత వైద్య పరిస్థితులు లేదా దీర్ఘకాలిక వ్యాధులు ఏవైనా ఉన్నాయా?",
            "ml": "നിങ്ങൾക്ക് മുൻകാല രോഗാവസ്ഥകളോ വിട്ടുമാറാത്ത രോഗങ്ങളോ ഉണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="pmh_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="pmh_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
            QuestionOption(option_id="pmh_unknown", text={"en": "I don't know", "hi": "मुझे नहीं पता", "ta": "எனக்குத் தெரியாது", "te": "నాకు తెలియదు", "ml": "എനിക്കറിയില്ല"}, value="unknown"),
        ],
        required=True,
        extraction_hints=["past medical history", "chronic disease", "medical condition"],
        clinical_concept_id="SNOMED:161496009"
    ))

    questions.append(Question(
        question_id="pmh_details",
        section="past_history",
        text={
            "en": "Please list your past medical conditions (like diabetes, high blood pressure, asthma, etc.)",
            "hi": "कृपया अपनी पिछली चिकित्सीय स्थितियों की सूची बनाएं (जैसे मधुमेह, उच्च रक्तचाप, अस्थमा, आदि)",
            "ta": "உங்கள் கடந்தகால மருத்துவ நிலைகளை பட்டியலிடுங்கள் (நீரிழிவு, உயர் இரத்த அழுத்தம், ஆஸ்துமா போன்றவை)",
            "te": "దయచేసి మీ గత వైద్య పరిస్థితులను జాబితా చేయండి (డయాబెటీస్, హై బ్లడ్ ప్రెజర్, ఆస్తమా వంటివి)",
            "ml": "നിങ്ങളുടെ മുൻകാല രോഗാവസ്ഥകൾ പട്ടികപ്പെടുത്തുക (പ്രമേഹം, ഉയർന്ന രക്തസമ്മർദ്ദം, ആസ്തമ മുതലായവ)",
        },
        field_type="text",
        required=False,
        conditional_rules={"depends_on": "pmh_any", "show_if_value": "yes"},
        extraction_hints=["medical condition", "disease", "diabetes", "hypertension", "asthma"],
        clinical_concept_id="SNOMED:161496009"
    ))

    # Past Surgical History
    questions.append(Question(
        question_id="psh_any",
        section="past_history",
        text={
            "en": "Have you had any surgeries or operations in the past?",
            "hi": "क्या आपकी अतीत में कोई सर्जरी या ऑपरेशन हुआ है?",
            "ta": "கடந்த காலத்தில் ஏதேனும் அறுவை சிகிச்சைகள் அல்லது அறுவை சிகிச்சைகள் செய்துள்ளீர்களா?",
            "te": "గతంలో మీకు ఏవైనా శస్త్రచికిత్సలు లేదా ఆపరేషన్లు జరిగాయా?",
            "ml": "മുൻകാലങ്ങളിൽ നിങ്ങൾക്ക് ഏതെങ്കിലും ശസ്ത്രക്രിയകളോ ഓപ്പറേഷനുകളോ ഉണ്ടായിട്ടുണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="psh_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="psh_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
            QuestionOption(option_id="psh_unknown", text={"en": "I don't know", "hi": "मुझे नहीं पता", "ta": "எனக்குத் தெரியாது", "te": "నాకు తెలియదు", "ml": "എനിക്കറിയില്ല"}, value="unknown"),
        ],
        required=True,
        extraction_hints=["surgery", "operation", "surgical history"],
        clinical_concept_id="SNOMED:161615003"
    ))

    questions.append(Question(
        question_id="psh_details",
        section="past_history",
        text={
            "en": "Please describe your past surgeries (what surgery, when it was done)",
            "hi": "कृपया अपनी पिछली सर्जरी का वर्णन करें (कौन सी सर्जरी, कब की गई)",
            "ta": "உங்கள் கடந்தகால அறுவை சிகிச்சைகளை விவரிக்கவும் (என்ன அறுவை சிகிச்சை, எப்போது செய்யப்பட்டது)",
            "te": "దయచేసి మీ గత శస్త్రచికిత్సలను వివరించండి (ఏ శస్త్రచికిత్స, ఎప్పుడు చేయబడింది)",
            "ml": "നിങ്ങളുടെ മുൻകാല ശസ്ത്രക്രിയകൾ വിവരിക്കുക (ഏത് ശസ്ത്രക്രിയ, എപ്പോൾ നടത്തി)",
        },
        field_type="text",
        required=False,
        conditional_rules={"depends_on": "psh_any", "show_if_value": "yes"},
        extraction_hints=["surgery", "procedure", "year", "operation"],
        clinical_concept_id="SNOMED:161615003"
    ))

    # Medications
    questions.append(Question(
        question_id="med_any",
        section="medications",
        text={
            "en": "Are you currently taking any medications?",
            "hi": "क्या आप वर्तमान में कोई दवाएं ले रहे हैं?",
            "ta": "நீங்கள் தற்போது ஏதேனும் மருந்துகளை எடுத்துக்கொள்கிறீர்களா?",
            "te": "మీరు ప్రస్తుతం ఏవైనా మందులు తీసుకుంటున్నారా?",
            "ml": "നിങ്ങൾ നിലവിൽ എന്തെങ്കിലും മരുന്നുകൾ കഴിക്കുന്നുണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="med_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="med_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
        ],
        required=True,
        extraction_hints=["medications", "medicines", "drugs", "tablets"],
        clinical_concept_id="SNOMED:182832007"
    ))

    questions.append(Question(
        question_id="med_details",
        section="medications",
        text={
            "en": "Please list your current medications (name, dosage, frequency)",
            "hi": "कृपया अपनी वर्तमान दवाओं की सूची बनाएं (नाम, खुराक, आवृत्ति)",
            "ta": "உங்கள் தற்போதைய மருந்துகளை பட்டியலிடுங்கள் (பெயர், அளவு, அதிர்வெண்)",
            "te": "దయచేసి మీ ప్రస్తుత మందులను జాబితా చేయండి (పేరు, మోతాదు, ఫ్రీక్వెన్సీ)",
            "ml": "നിങ്ങളുടെ നിലവിലെ മരുന്നുകൾ പട്ടികപ്പെടുത്തുക (പേര്, ഡോസേജ്, ആവൃത്തി)",
        },
        field_type="text",
        required=False,
        conditional_rules={"depends_on": "med_any", "show_if_value": "yes"},
        extraction_hints=["medication", "dosage", "frequency", "tablet", "medicine"],
        clinical_concept_id="SNOMED:182832007"
    ))

    # Allergies
    questions.append(Question(
        question_id="allergy_any",
        section="allergies",
        text={
            "en": "Do you have any allergies to medications, foods, or other substances?",
            "hi": "क्या आपको दवाओं, खाद्य पदार्थों या अन्य पदार्थों से कोई एलर्जी है?",
            "ta": "மருந்துகள், உணவுகள் அல்லது பிற பொருட்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?",
            "te": "మీకు మందులు, ఆహారాలు లేదా ఇతర పదార్థాలకు ఏవైనా అలర్జీలు ఉన్నాయా?",
            "ml": "മരുന്നുകൾ, ഭക്ഷണങ്ങൾ അല്ലെങ്കിൽ മറ്റ് പദാർത്ഥങ്ങൾക്ക് എന്തെങ്കിലും അലർജി ഉണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="allergy_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="allergy_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
            QuestionOption(option_id="allergy_unknown", text={"en": "I don't know", "hi": "मुझे नहीं पता", "ta": "எனக்குத் தெரியாது", "te": "నాకు తెలియదు", "ml": "എനിക്കറിയില്ല"}, value="unknown"),
        ],
        required=True,
        extraction_hints=["allergy", "allergic", "reaction"],
        clinical_concept_id="SNOMED:473010000"
    ))

    questions.append(Question(
        question_id="allergy_details",
        section="allergies",
        text={
            "en": "Please describe your allergies (what you're allergic to and what reaction you have)",
            "hi": "कृपया अपनी एलर्जी का वर्णन करें (आपको किससे एलर्जी है और क्या प्रतिक्रिया होती है)",
            "ta": "உங்கள் ஒவ்வாமைகளை விவரிக்கவும் (நீங்கள் எதற்கு ஒவ்வாமை கொண்டுள்ளீர்கள், என்ன எதிர்வினை உள்ளது)",
            "te": "దయచేసి మీ అలర్జీలను వివరించండి (మీకు దేనికి అలర్జీ ఉంది మరియు ఏ రియాక్షన్ ఉంది)",
            "ml": "നിങ്ങളുടെ അലർജികൾ വിവരിക്കുക (എന്താണ് അലർജി, എന്ത് പ്രതികരണം)",
        },
        field_type="text",
        required=False,
        conditional_rules={"depends_on": "allergy_any", "show_if_value": "yes"},
        extraction_hints=["allergen", "reaction", "allergy"],
        clinical_concept_id="SNOMED:473010000"
    ))

    # Family History
    questions.append(Question(
        question_id="family_history",
        section="family_history",
        text={
            "en": "Do any diseases run in your family? (like diabetes, heart disease, cancer)",
            "hi": "क्या आपके परिवार में कोई बीमारियाँ चलती हैं? (जैसे मधुमेह, हृदय रोग, कैंसर)",
            "ta": "உங்கள் குடும்பத்தில் ஏதேனும் நோய்கள் இயங்குகின்றனவா? (நீரிழிவு, இதய நோய், புற்றுநோய் போன்றவை)",
            "te": "మీ కుటుంబంలో ఏవైనా వ్యాధులు నడుస్తున్నాయా? (డయాబెటీస్, గుండె జబ్బు, క్యాన్సర్ వంటివి)",
            "ml": "നിങ്ങളുടെ കുടുംബത്തിൽ എന്തെങ്കിലും രോഗങ്ങൾ പ്രവർത്തിക്കുന്നുണ്ടോ? (പ്രമേഹം, ഹൃദ്രോഗം, കാൻസർ എന്നിവ പോലെ)",
        },
        field_type="text",
        required=False,
        extraction_hints=["family history", "hereditary", "genetic", "runs in family"],
        clinical_concept_id="SNOMED:57177007"
    ))

    # Personal History - Smoking
    questions.append(Question(
        question_id="smoking",
        section="personal_history",
        text={
            "en": "Do you smoke or use tobacco?",
            "hi": "क्या आप धूम्रपान करते हैं या तंबाकू का उपयोग करते हैं?",
            "ta": "நீங்கள் புகைபிடிக்கிறீர்களா அல்லது புகையிலை பயன்படுத்துகிறீர்களா?",
            "te": "మీరు ధూమపానం చేస్తారా లేదా పొగాకు వాడుతారా?",
            "ml": "നിങ്ങൾ പുകവലിക്കുന്നുണ്ടോ അല്ലെങ്കിൽ പുകയില ഉപയോഗിക്കുന്നുണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="smoke_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="smoke_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
            QuestionOption(option_id="smoke_former", text={"en": "Former smoker", "hi": "पूर्व धूम्रपान करने वाला", "ta": "முன்னாள் புகைப்பிடிப்பவர்", "te": "మాజీ ధూమపానం", "ml": "മുൻ പുകവലിക്കാരൻ"}, value="former"),
        ],
        required=False,
        extraction_hints=["smoking", "tobacco", "cigarettes"],
        clinical_concept_id="SNOMED:365980008"
    ))

    # Personal History - Alcohol
    questions.append(Question(
        question_id="alcohol",
        section="personal_history",
        text={
            "en": "Do you drink alcohol?",
            "hi": "क्या आप शराब पीते हैं?",
            "ta": "நீங்கள் மது அருந்துகிறீர்களா?",
            "te": "మీరు మద్యపానం చేస్తారా?",
            "ml": "നിങ്ങൾ മദ്യം കുടിക്കുന്നുണ്ടോ?",
        },
        field_type="single_choice",
        options=[
            QuestionOption(option_id="alcohol_yes", text={"en": "Yes", "hi": "हाँ", "ta": "ஆம்", "te": "అవును", "ml": "അതെ"}, value="yes"),
            QuestionOption(option_id="alcohol_no", text={"en": "No", "hi": "नहीं", "ta": "இல்லை", "te": "కాదు", "ml": "ഇല്ല"}, value="no"),
            QuestionOption(option_id="alcohol_occasional", text={"en": "Occasionally", "hi": "कभी-कभी", "ta": "எப்போதாவது", "te": "అప్పుడప్పుడు", "ml": "ഇടയ്ക്കിടെ"}, value="occasional"),
        ],
        required=False,
        extraction_hints=["alcohol", "drinking", "drinks"],
        clinical_concept_id="SNOMED:160573003"
    ))

    return questions


def get_questionnaire_schema() -> Dict[str, Any]:
    """Get complete allopathy questionnaire schema."""
    questions = get_allopathy_questionnaire()

    return {
        "questionnaire_id": "allopathy_v1",
        "version": "1.0",
        "mode": "allopathy",
        "sections": SECTIONS,
        "questions": [q.model_dump() for q in questions]
    }
