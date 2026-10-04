"""
Language registry schemas.
"""
from typing import List, Optional
from pydantic import BaseModel


class LanguageCapabilities(BaseModel):
    """Language support capabilities."""
    asr_supported: bool = False
    tts_supported: bool = False
    ui_supported: bool = True
    questionnaire_supported: bool = True
    conversation_supported: bool = False


class Language(BaseModel):
    """Language information."""
    code: str
    native_name: str
    english_name: str
    bcp47_locale: str
    capabilities: LanguageCapabilities


class LanguageListResponse(BaseModel):
    """Response containing list of supported languages."""
    languages: List[Language]
    total: int


# The 23 language registry - source of truth
LANGUAGE_REGISTRY: List[Language] = [
    Language(
        code="as",
        native_name="অসমীয়া",
        english_name="Assamese",
        bcp47_locale="as-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="bn",
        native_name="বাংলা",
        english_name="Bengali",
        bcp47_locale="bn-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="brx",
        native_name="बर'/बड़ो",
        english_name="Bodo",
        bcp47_locale="brx-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="doi",
        native_name="डोगरी",
        english_name="Dogri",
        bcp47_locale="doi-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="gu",
        native_name="ગુજરાતી",
        english_name="Gujarati",
        bcp47_locale="gu-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="hi",
        native_name="हिन्दी",
        english_name="Hindi",
        bcp47_locale="hi-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="kn",
        native_name="ಕನ್ನಡ",
        english_name="Kannada",
        bcp47_locale="kn-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="ks",
        native_name="कॉशुर / کٲشُر",
        english_name="Kashmiri",
        bcp47_locale="ks-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="kok",
        native_name="कोंकणी",
        english_name="Konkani",
        bcp47_locale="kok-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="mai",
        native_name="मैथिली",
        english_name="Maithili",
        bcp47_locale="mai-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="ml",
        native_name="മലയാളം",
        english_name="Malayalam",
        bcp47_locale="ml-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="mni",
        native_name="মৈতৈলোন্",
        english_name="Manipuri",
        bcp47_locale="mni-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="mr",
        native_name="मराठी",
        english_name="Marathi",
        bcp47_locale="mr-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="ne",
        native_name="नेपाली",
        english_name="Nepali",
        bcp47_locale="ne-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="or",
        native_name="ଓଡ଼ିଆ",
        english_name="Odia",
        bcp47_locale="or-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="pa",
        native_name="ਪੰਜਾਬੀ",
        english_name="Punjabi",
        bcp47_locale="pa-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="sa",
        native_name="संस्कृतम्",
        english_name="Sanskrit",
        bcp47_locale="sa-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="sat",
        native_name="ᱥᱟᱱᱛᱟᱲᱤ",
        english_name="Santali",
        bcp47_locale="sat-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="sd",
        native_name="سنڌي",
        english_name="Sindhi",
        bcp47_locale="sd-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="ta",
        native_name="தமிழ்",
        english_name="Tamil",
        bcp47_locale="ta-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="te",
        native_name="తెలుగు",
        english_name="Telugu",
        bcp47_locale="te-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
    Language(
        code="ur",
        native_name="اردو",
        english_name="Urdu",
        bcp47_locale="ur-IN",
        capabilities=LanguageCapabilities(ui_supported=True, questionnaire_supported=True)
    ),
    Language(
        code="en",
        native_name="English",
        english_name="English",
        bcp47_locale="en-IN",
        capabilities=LanguageCapabilities(asr_supported=True, tts_supported=True, ui_supported=True, questionnaire_supported=True, conversation_supported=True)
    ),
]


def get_language_by_code(code: str) -> Optional[Language]:
    """Get language information by code."""
    for lang in LANGUAGE_REGISTRY:
        if lang.code == code:
            return lang
    return None


def get_supported_languages() -> LanguageListResponse:
    """Get all supported languages."""
    return LanguageListResponse(
        languages=LANGUAGE_REGISTRY,
        total=len(LANGUAGE_REGISTRY)
    )
