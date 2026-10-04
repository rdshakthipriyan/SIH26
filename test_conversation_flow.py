"""
Test script to verify AYUSH and Allopathy conversation progression.

Run this after starting the backend server.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_ayush_progression():
    """Test AYUSH/Ayurveda progression through all 15 questions."""
    print("\n" + "="*80)
    print("TEST 1: AYUSH AYURVEDA PROGRESSION (15 questions)")
    print("="*80 + "\n")

    # Create a session first
    session_response = requests.post(
        f"{BASE_URL}/sessions/start",
        json={
            "patient_name": "Test Patient",
            "patient_age": 35,
            "patient_gender": "M",
            "is_guest": True,
            "consent_given": True,
            "mode": "ayush",
            "language_code": "en"
        }
    )
    session_data = session_response.json()
    session_id = session_data.get("session_id")
    print(f"✓ Created session: {session_id}\n")

    # Start conversation
    start_response = requests.post(
        f"{BASE_URL}/cases/{session_id}/conversation/start",
        json={
            "mode": "ayush",
            "stream": "ayurveda",
            "language_code": "en"
        },
        headers={"Authorization": f"Bearer {session_data.get('token')}"}
    )
    start_data = start_response.json()
    first_question = start_data.get("first_question", {})
    print(f"✓ Start conversation")
    print(f"  First question: {first_question.get('question_id')}")
    print(f"  Is complete: {start_data.get('is_complete')}\n")

    answered_count = 0
    current_question = first_question
    responses_log = []

    # Answer all questions
    while current_question and answered_count < 20:  # Safety limit
        question_id = current_question.get("question_id")
        answered_count += 1

        print(f"[{answered_count}] Answering: {question_id}")

        # Provide answer based on question type
        field_type = current_question.get("field_type")
        if field_type == "single_choice" and current_question.get("options"):
            answer_value = current_question["options"][0].get("value", "DEFAULT")
            answer_text = current_question["options"][0].get("text", {}).get("en", "Option 1")
        elif field_type == "number":
            answer_value = "5"
            answer_text = "5"
        else:
            answer_value = f"Answer to {question_id}"
            answer_text = answer_value

        # Submit answer
        respond_response = requests.post(
            f"{BASE_URL}/cases/{session_id}/conversation/respond",
            json={
                "answer_text": answer_text,
                "answer_value": answer_value,
                "input_mode": "touch",
                "question_id": question_id
            },
            headers={"Authorization": f"Bearer {session_data.get('token')}"}
        )

        if respond_response.status_code != 200:
            print(f"  ✗ ERROR: {respond_response.status_code}")
            print(f"    {respond_response.text}\n")
            break

        respond_data = respond_response.json()
        next_question = respond_data.get("next_question")
        is_complete = respond_data.get("is_complete", False)
        completion = respond_data.get("completion_percentage", 0)

        responses_log.append({
            "question": question_id,
            "next": next_question.get("question_id") if next_question else None,
            "is_complete": is_complete,
            "completion": completion
        })

        print(f"  ✓ Answered: {answer_text[:40]}")
        if next_question:
            print(f"    Next question: {next_question.get('question_id')}")
        else:
            print(f"    Next question: NONE (complete)")
        print(f"    Is complete: {is_complete}")
        print(f"    Progress: {completion}%\n")

        if is_complete:
            print(f"✓ CONVERSATION COMPLETE after {answered_count} questions\n")
            break

        current_question = next_question

    # Verify progression
    print("\nPROGRESSION SUMMARY:")
    print("-" * 80)
    expected_ayurveda_questions = [
        "ayurveda_body_build",
        "ayurveda_thermal",
        "ayurveda_skin",
        "ayurveda_appetite",
        "ayurveda_digestion",
        "ayurveda_bowel",
        "ayurveda_sleep",
        "ayurveda_stress",
        "ayurveda_activity",
        "ayurveda_food_preference",
        "ayurveda_routine",
        "ayurveda_chief_complaint",
        "ayurveda_complaint_duration",
        "ayurveda_complaint_severity",
        "ayurveda_associated_symptoms",
    ]

    for i, log in enumerate(responses_log, 1):
        expected = expected_ayurveda_questions[i-1] if i-1 < len(expected_ayurveda_questions) else "???"
        actual = log["question"]
        match = "✓" if actual == expected else "✗"
        print(f"{match} Q{i:2d}: {actual}")
        print(f"       → {log['next']}")

    if answered_count >= 15:
        print(f"\n✓ PASS: All 15 questions answered")
    else:
        print(f"\n✗ FAIL: Only {answered_count} questions answered (expected 15)")

    return answered_count == 15


def test_allopathy_progression():
    """Test Allopathy progression through at least 5 questions."""
    print("\n" + "="*80)
    print("TEST 2: ALLOPATHY PROGRESSION (5+ questions)")
    print("="*80 + "\n")

    # Create a session first
    session_response = requests.post(
        f"{BASE_URL}/sessions/start",
        json={
            "patient_name": "Test Patient 2",
            "patient_age": 40,
            "patient_gender": "F",
            "is_guest": True,
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        }
    )
    session_data = session_response.json()
    session_id = session_data.get("session_id")
    print(f"✓ Created session: {session_id}\n")

    # Start conversation
    start_response = requests.post(
        f"{BASE_URL}/cases/{session_id}/conversation/start",
        json={
            "mode": "allopathy",
            "language_code": "en"
        },
        headers={"Authorization": f"Bearer {session_data.get('token')}"}
    )
    start_data = start_response.json()
    first_question = start_data.get("first_question", {})
    print(f"✓ Start conversation")
    print(f"  First question: {first_question.get('question_id')}")
    print(f"  Is complete: {start_data.get('is_complete')}\n")

    answered_count = 0
    current_question = first_question
    responses_log = []
    prev_question_id = None

    # Answer 5 questions
    while current_question and answered_count < 5:
        question_id = current_question.get("question_id")
        answered_count += 1

        print(f"[{answered_count}] Answering: {question_id}")

        # Check for repetition
        if question_id == prev_question_id:
            print(f"  ✗ REPETITION: Same question as previous!")
            responses_log.append({
                "question": question_id,
                "repeated": True
            })
            break

        # Provide answer
        answer_text = f"Test answer for {question_id}"
        answer_value = answer_text

        # Submit answer
        respond_response = requests.post(
            f"{BASE_URL}/cases/{session_id}/conversation/respond",
            json={
                "answer_text": answer_text,
                "answer_value": answer_value,
                "input_mode": "touch"
            },
            headers={"Authorization": f"Bearer {session_data.get('token')}"}
        )

        if respond_response.status_code != 200:
            print(f"  ✗ ERROR: {respond_response.status_code}")
            print(f"    {respond_response.text}\n")
            break

        respond_data = respond_response.json()
        next_question = respond_data.get("next_question")

        responses_log.append({
            "from": question_id,
            "to": next_question.get("question_id") if next_question else None,
            "repeated": False
        })

        print(f"  ✓ Answered")
        if next_question:
            print(f"    Next question: {next_question.get('question_id')}")
        else:
            print(f"    Next question: NONE\n")

        prev_question_id = question_id
        current_question = next_question

    # Verify progression
    print("\nPROGRESSION SUMMARY:")
    print("-" * 80)

    has_repetition = False
    for i, log in enumerate(responses_log, 1):
        if log.get("repeated"):
            print(f"✗ Q{i}: REPEATED QUESTION")
            has_repetition = True
        else:
            print(f"✓ Q{i}: {log['from']} → {log['to']}")

    if answered_count >= 5 and not has_repetition:
        print(f"\n✓ PASS: Progressed through {answered_count} unique questions")
        return True
    else:
        print(f"\n✗ FAIL: Repetition or insufficient progression")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONVERSATION FLOW TEST SUITE")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80)

    try:
        ayush_pass = test_ayush_progression()
    except Exception as e:
        print(f"✗ AYUSH test failed with exception: {e}")
        ayush_pass = False

    try:
        allopathy_pass = test_allopathy_progression()
    except Exception as e:
        print(f"✗ Allopathy test failed with exception: {e}")
        allopathy_pass = False

    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"AYUSH Progression:     {'✓ PASS' if ayush_pass else '✗ FAIL'}")
    print(f"Allopathy Progression: {'✓ PASS' if allopathy_pass else '✗ FAIL'}")
    print("="*80 + "\n")
