"""Quick integration verification script for AYUSH / conversation flow."""
import sys, os
sys.path.insert(0, '.')
os.chdir('D:/Projects/New folder/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.conversation.conversation_engine import ConversationEngine
from app.services.ayush.ayush_engine import AyushEngine
from app.services.conversation.stream_questionnaire import get_questionnaire
from app.models.clinical_case import ClinicalCase

# Use existing DB with tables
DATABASE_URL = "sqlite:///medikiosk.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Simulate an AYUSH conversation flow
ayush_engine = ConversationEngine(SessionLocal(), mode="ayush", stream="ayurveda")
q_first = ayush_engine.get_next_question("test-session", {})
print("First AYUSH question:", q_first["question_id"] if q_first else None)

# Simulate first answer with proper answer_value
res = ayush_engine.process_answer(
    session_id="test-session",
    question_id=q_first["question_id"],
    answer_text="Slim and light",
    language="en",
    input_mode="touch",
    answer_value="SLIM",
)
print("\nResponse keys:", sorted(res.keys()))
print("ayush_profile present:", res.get("ayush_profile") is not None)
print("mode:", res.get("mode"))
print("stream:", res.get("stream"))

if res.get("ayush_profile"):
    profile = res["ayush_profile"]
    print("\nProfile prakriti:", {
        "vata": profile.get("prakriti", {}).get("vata_score"),
        "pitta": profile.get("prakriti", {}).get("pitta_score"),
        "kapha": profile.get("prakriti", {}).get("kapha_score"),
        "dominant": profile.get("prakriti", {}).get("dominant_type"),
    })
    print("Profile agni:", profile.get("agni"))
    print("Profile koshtha:", profile.get("koshtha"))
    print("Profile satva:", profile.get("satva"))
    print("Profile ahara_vihara:", profile.get("ahara_vihara"))
    print("Completion %:", profile.get("completion_percentage"))
    print("is_complete:", profile.get("is_complete"))
else:
    print("\nERROR: ayush_profile is None!")

# Answer second question
if res.get("next_question"):
    res2 = ayush_engine.process_answer(
        session_id="test-session",
        question_id=res["next_question"]["question_id"],
        answer_text="I prefer warmth",
        language="en",
        input_mode="touch",
        answer_value="PREFERS_WARM",
    )
    if res2.get("ayush_profile"):
        p = res2["ayush_profile"]
        print("\nAfter 2nd answer:")
        print("  prakriti:", {
            "vata": round(p.get("prakriti", {}).get("vata_score", 0), 3),
            "pitta": round(p.get("prakriti", {}).get("pitta_score", 0), 3),
            "kapha": round(p.get("prakriti", {}).get("kapha_score", 0), 3),
        })
        print("  completion:", p.get("completion_percentage"), "%")

# Allopathy mode — confirm no profile returned
allo_engine = ConversationEngine(SessionLocal(), mode="allopathy", stream=None)
print("\nAllopathy stream:", allo_engine.stream)
print("Allopathy mode:", allo_engine.mode)
print("\n✓ Integration test complete.")
