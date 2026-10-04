"""
Automated Browser Test Suite for MediKiosk Questionnaire Flow
Tests the three critical scenarios identified in the investigation.
"""
import requests
import json
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000/api/v1"

class TestResults:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def add_result(self, test_name: str, passed: bool, message: str):
        self.results.append({
            "test": test_name,
            "status": "✓ PASS" if passed else "✗ FAIL",
            "message": message
        })
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            print(f"    {result['message']}")
        print("=" * 70)
        print(f"Total: {self.tests_passed} passed, {self.tests_failed} failed")
        print("=" * 70)


def create_session(mode: str, language_code: str) -> Dict[str, Any]:
    """Create a test session."""
    response = requests.post(
        f"{BASE_URL}/sessions/start",
        json={
            "patient_name": f"Test Patient {mode}",
            "patient_age": "30",
            "patient_gender": "male",
            "is_guest": True,
            "consent_given": True,
            "mode": mode,
            "language_code": language_code
        }
    )
    response.raise_for_status()
    return response.json()


def start_conversation(session_id: str, token: str, mode: str, stream: str = None, language_code: str = "en") -> Dict[str, Any]:
    """Start a conversation."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "mode": mode,
        "language_code": language_code
    }
    if stream:
        payload["stream"] = stream

    response = requests.post(
        f"{BASE_URL}/cases/{session_id}/conversation/start",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def respond_to_question(session_id: str, token: str, question_id: str, answer_text: str, answer_value: str = None) -> Dict[str, Any]:
    """Respond to a question."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "answer_text": answer_text,
        "input_mode": "touch",
        "question_id": question_id
    }
    if answer_value:
        payload["answer_value"] = answer_value

    response = requests.post(
        f"{BASE_URL}/cases/{session_id}/conversation/respond",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def test_ayush_english():
    """Test A: AYUSH Ayurveda (English) - Verify 5+ sequential questions."""
    print("\n" + "=" * 70)
    print("TEST A: AYUSH AYURVEDA (ENGLISH)")
    print("=" * 70)

    results = TestResults()

    try:
        # Create session
        print("\n1. Creating session...")
        session_data = create_session("ayush", "en")
        session_id = session_data["session_id"]
        token = session_data["token"]
        print(f"   ✓ Session created: {session_id}")

        # Start conversation
        print("\n2. Starting Ayurveda conversation...")
        conv_data = start_conversation(session_id, token, "ayush", "ayurveda", "en")
        first_question = conv_data.get("first_question")

        if not first_question:
            results.add_result("Start Conversation", False, "No first_question returned")
            return results

        print(f"   ✓ First question: {first_question['question_id']}")
        print(f"     Text: {first_question['text']['en'][:60]}...")

        results.add_result("Start Conversation", True, f"First question: {first_question['question_id']}")

        # Track questions seen
        questions_seen = [first_question["question_id"]]
        current_question = first_question

        # Answer questions and verify progression
        test_answers = [
            ("ayurveda_body_build", "Slim and light", "SLIM"),
            ("ayurveda_thermal", "I prefer warmth", "PREFERS_WARM"),
            ("ayurveda_skin", "Dry or rough", "DRY"),
            ("ayurveda_appetite", "Very strong and regular", "STRONG"),
            ("ayurveda_digestion", "I digest it well, no issues", "GOOD"),
        ]

        for i, (expected_qid, answer_text, answer_value) in enumerate(test_answers, 1):
            print(f"\n{i + 2}. Answering question {i}: {current_question['question_id']}")

            # Verify we got the expected question
            if current_question["question_id"] != expected_qid:
                results.add_result(
                    f"Question {i} ID",
                    False,
                    f"Expected {expected_qid}, got {current_question['question_id']}"
                )
                break

            results.add_result(
                f"Question {i} ID",
                True,
                f"Correct question: {expected_qid}"
            )

            # Answer the question
            response = respond_to_question(
                session_id, token, current_question["question_id"], answer_text, answer_value
            )

            # Check if complete prematurely
            if response.get("is_complete") and i < len(test_answers):
                results.add_result(
                    f"Question {i} Progression",
                    False,
                    f"Marked complete after only {i} questions (expected 15 total)"
                )
                break

            # Get next question
            next_question = response.get("next_question")
            if not next_question and not response.get("is_complete"):
                results.add_result(
                    f"Question {i} Progression",
                    False,
                    "No next_question and not marked complete"
                )
                break

            if next_question:
                questions_seen.append(next_question["question_id"])
                print(f"   ✓ Next question: {next_question['question_id']}")
                print(f"     Text: {next_question['text']['en'][:60]}...")

                # Verify it's different from current
                if next_question["question_id"] == current_question["question_id"]:
                    results.add_result(
                        f"Question {i} Progression",
                        False,
                        f"Same question repeated: {current_question['question_id']}"
                    )
                    break

                results.add_result(
                    f"Question {i} Progression",
                    True,
                    f"Advanced to {next_question['question_id']}"
                )

                current_question = next_question
            else:
                print(f"   ✓ Conversation complete after {i} questions")
                break

        # Verify we got at least 5 unique questions
        if len(questions_seen) >= 5:
            results.add_result(
                "Question Count",
                True,
                f"Received {len(questions_seen)} unique questions (expected ≥5)"
            )
        else:
            results.add_result(
                "Question Count",
                False,
                f"Only {len(questions_seen)} questions (expected ≥5)"
            )

        print(f"\n   Questions seen: {', '.join(questions_seen)}")

    except Exception as e:
        results.add_result("Test Execution", False, str(e))
        import traceback
        traceback.print_exc()

    return results


def test_ayush_tamil():
    """Test B: AYUSH Ayurveda (Tamil) - Verify Tamil rendering and progression."""
    print("\n" + "=" * 70)
    print("TEST B: AYUSH AYURVEDA (TAMIL)")
    print("=" * 70)

    results = TestResults()

    try:
        # Create session
        print("\n1. Creating session...")
        session_data = create_session("ayush", "ta")
        session_id = session_data["session_id"]
        token = session_data["token"]
        print(f"   ✓ Session created: {session_id}")

        # Start conversation
        print("\n2. Starting Ayurveda conversation (Tamil)...")
        conv_data = start_conversation(session_id, token, "ayush", "ayurveda", "ta")
        first_question = conv_data.get("first_question")

        if not first_question:
            results.add_result("Start Conversation", False, "No first_question returned")
            return results

        # Check Tamil text exists
        tamil_text = first_question.get("text", {}).get("ta")
        if not tamil_text:
            results.add_result("Tamil Text", False, "No Tamil text in first question")
            return results

        # Verify Tamil Unicode (U+0B80-U+0BFF range)
        if ord(tamil_text[0]) in range(0x0B80, 0x0C00):
            results.add_result("Tamil Text Encoding", True, "Tamil text properly encoded")
            print(f"   ✓ Tamil text: {tamil_text[:40]}...")
        else:
            results.add_result("Tamil Text Encoding", False, f"Invalid Tamil encoding: U+{ord(tamil_text[0]):04X}")

        # Check options have Tamil text
        options = first_question.get("options", [])
        if options:
            tamil_option = options[0].get("text", {}).get("ta")
            if tamil_option and ord(tamil_option[0]) in range(0x0B80, 0x0C00):
                results.add_result("Tamil Options", True, "Options have valid Tamil text")
                print(f"   ✓ Tamil option: {tamil_option}")
            else:
                results.add_result("Tamil Options", False, "Options missing Tamil text or corrupted")

        # Answer first 3 questions to verify progression
        current_question = first_question
        questions_seen = [first_question["question_id"]]

        tamil_answers = [
            ("மெலிந்து லேசாக", "SLIM"),
            ("வெம்மையை விரும்புகிறேன்", "PREFERS_WARM"),
            ("உலர்ந்த அல்லது கருகலான", "DRY"),
        ]

        for i, (tamil_answer, answer_value) in enumerate(tamil_answers, 1):
            print(f"\n{i + 2}. Answering question {i}: {current_question['question_id']}")

            response = respond_to_question(
                session_id, token, current_question["question_id"], tamil_answer, answer_value
            )

            next_question = response.get("next_question")
            if next_question:
                questions_seen.append(next_question["question_id"])
                tamil_next = next_question.get("text", {}).get("ta")

                if tamil_next and ord(tamil_next[0]) in range(0x0B80, 0x0C00):
                    print(f"   ✓ Next question in Tamil: {tamil_next[:40]}...")
                    results.add_result(f"Question {i} Progression", True, f"Advanced to {next_question['question_id']}")
                else:
                    results.add_result(f"Question {i} Tamil Text", False, "Next question missing Tamil")

                current_question = next_question
            else:
                break

        if len(questions_seen) >= 3:
            results.add_result("Tamil Flow", True, f"Completed {len(questions_seen)} questions in Tamil")
        else:
            results.add_result("Tamil Flow", False, f"Only {len(questions_seen)} questions")

    except Exception as e:
        results.add_result("Test Execution", False, str(e))
        import traceback
        traceback.print_exc()

    return results


def test_allopathy():
    """Test C: Allopathy (English) - Verify no question repetition."""
    print("\n" + "=" * 70)
    print("TEST C: ALLOPATHY (ENGLISH)")
    print("=" * 70)

    results = TestResults()

    try:
        # Create session
        print("\n1. Creating session...")
        session_data = create_session("allopathy", "en")
        session_id = session_data["session_id"]
        token = session_data["token"]
        print(f"   ✓ Session created: {session_id}")

        # Start conversation
        print("\n2. Starting Allopathy conversation...")
        conv_data = start_conversation(session_id, token, "allopathy", None, "en")
        first_question = conv_data.get("first_question")

        if not first_question:
            results.add_result("Start Conversation", False, "No first_question returned")
            return results

        print(f"   ✓ First question: {first_question['question_id']}")
        print(f"     Text: {first_question['text']['en'][:60]}...")

        # Track questions seen
        questions_seen = [first_question["question_id"]]
        question_texts = [first_question["text"]["en"]]
        current_question = first_question

        # Answer 5 questions
        for i in range(1, 6):
            print(f"\n{i + 2}. Answering question {i}: {current_question['question_id']}")

            # Provide generic answer
            answer_text = f"Test answer {i} for allopathy question"

            response = respond_to_question(
                session_id, token, current_question["question_id"], answer_text
            )

            next_question = response.get("next_question")
            if not next_question:
                print(f"   ✓ Conversation complete after {i} questions")
                break

            # Check for repetition
            next_qid = next_question["question_id"]
            next_text = next_question["text"]["en"]

            if next_qid in questions_seen:
                results.add_result(
                    f"Question {i} Repetition Check",
                    False,
                    f"Question ID repeated: {next_qid}"
                )
                break

            if next_text in question_texts:
                results.add_result(
                    f"Question {i} Repetition Check",
                    False,
                    f"Question text repeated: {next_text[:40]}..."
                )
                break

            results.add_result(
                f"Question {i} Unique",
                True,
                f"Question {i+1} is unique: {next_qid}"
            )

            questions_seen.append(next_qid)
            question_texts.append(next_text)

            print(f"   ✓ Next question: {next_qid}")
            print(f"     Text: {next_text[:60]}...")

            current_question = next_question

        # Verify we got at least 5 unique questions
        if len(questions_seen) >= 5:
            results.add_result(
                "No Repetition",
                True,
                f"All {len(questions_seen)} questions were unique"
            )
        else:
            results.add_result(
                "Question Count",
                False,
                f"Only {len(questions_seen)} questions (expected 5)"
            )

        print(f"\n   Questions seen: {', '.join(questions_seen)}")

    except Exception as e:
        results.add_result("Test Execution", False, str(e))
        import traceback
        traceback.print_exc()

    return results


def main():
    print("=" * 70)
    print("MEDIKIOSK QUESTIONNAIRE FLOW - AUTOMATED TEST SUITE")
    print("=" * 70)
    print("\nTesting the three critical scenarios:")
    print("  A. AYUSH Ayurveda (English) - Sequential progression")
    print("  B. AYUSH Ayurveda (Tamil) - Unicode rendering")
    print("  C. Allopathy (English) - No repetition")
    print("\nStarting tests...\n")

    # Run all tests
    results_a = test_ayush_english()
    results_b = test_ayush_tamil()
    results_c = test_allopathy()

    # Combined summary
    print("\n" + "=" * 70)
    print("COMBINED TEST RESULTS")
    print("=" * 70)

    print("\n--- TEST A: AYUSH AYURVEDA (ENGLISH) ---")
    results_a.print_summary()

    print("\n--- TEST B: AYUSH AYURVEDA (TAMIL) ---")
    results_b.print_summary()

    print("\n--- TEST C: ALLOPATHY (ENGLISH) ---")
    results_c.print_summary()

    # Overall summary
    total_passed = results_a.tests_passed + results_b.tests_passed + results_c.tests_passed
    total_failed = results_a.tests_failed + results_b.tests_failed + results_c.tests_failed

    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
    print("=" * 70)

    if total_failed == 0:
        print("\n✓ ALL TESTS PASSED - System is working correctly!")
        return 0
    else:
        print(f"\n✗ {total_failed} TEST(S) FAILED - Review failures above")
        return 1


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    exit(main())
