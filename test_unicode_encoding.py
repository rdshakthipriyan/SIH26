"""
Test script to verify Unicode encoding in API responses.

Run this to check if Tamil/Hindi text is correctly encoded in HTTP responses.
"""
import requests
import json
import sys

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_SESSION_ID = None  # Will be created

def test_unicode_encoding():
    """Test Unicode encoding throughout the API stack."""

    print("=" * 60)
    print("UNICODE ENCODING TEST")
    print("=" * 60)

    # Step 1: Create session
    print("\n1. Creating test session...")
    try:
        response = requests.post(
            f"{BASE_URL}/sessions/start",
            json={
                "patient_name": "Unicode Test Patient",
                "patient_age": "30",
                "patient_gender": "male",
                "is_guest": True,
                "consent_given": True,
                "mode": "ayush",
                "language_code": "ta"
            }
        )
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data.get("session_id")
        token = session_data.get("token")

        print(f"✓ Session created: {session_id}")
    except Exception as e:
        print(f"✗ Failed to create session: {e}")
        return

    # Step 2: Start conversation with Tamil
    print("\n2. Starting Ayurveda conversation (Tamil)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/cases/{session_id}/conversation/start",
            headers=headers,
            json={
                "mode": "ayush",
                "stream": "ayurveda",
                "language_code": "ta"
            }
        )
        response.raise_for_status()

        # Check raw response bytes
        raw_bytes = response.content
        print(f"\nRaw response length: {len(raw_bytes)} bytes")

        # Parse JSON
        data = response.json()
        first_question = data.get("first_question")

        if not first_question:
            print("✗ No first_question in response")
            return

        # Extract Tamil text
        tamil_text = first_question.get("text", {}).get("ta")
        english_text = first_question.get("text", {}).get("en")
        hindi_text = first_question.get("text", {}).get("hi")

        print("\n" + "=" * 60)
        print("QUESTION TEXT ENCODING ANALYSIS")
        print("=" * 60)

        # English
        print("\nEnglish:")
        print(f"  Text: {english_text}")
        print(f"  Length: {len(english_text) if english_text else 0} chars")

        # Hindi
        print("\nHindi:")
        if hindi_text:
            print(f"  Text: {hindi_text}")
            print(f"  Length: {len(hindi_text)} chars")
            print(f"  UTF-8 bytes: {hindi_text.encode('utf-8')[:50]}...")
            print(f"  First char: U+{ord(hindi_text[0]):04X}")
            # Check for mojibake pattern
            if any(ord(c) < 128 for c in hindi_text[:10]):
                print("  ⚠️  WARNING: Contains ASCII chars, possible mojibake")
            else:
                print("  ✓ Contains proper Unicode chars")
        else:
            print("  ✗ Missing")

        # Tamil
        print("\nTamil:")
        if tamil_text:
            print(f"  Text: {tamil_text}")
            print(f"  Length: {len(tamil_text)} chars")
            print(f"  UTF-8 bytes: {tamil_text.encode('utf-8')[:50]}...")
            print(f"  First char: U+{ord(tamil_text[0]):04X}")
            # Tamil Unicode range: U+0B80–U+0BFF
            if ord(tamil_text[0]) in range(0x0B80, 0x0C00):
                print("  ✓ First char is in Tamil Unicode block")
            else:
                print(f"  ✗ First char NOT in Tamil block (U+{ord(tamil_text[0]):04X})")
        else:
            print("  ✗ Missing")

        # Check options
        print("\n" + "=" * 60)
        print("OPTIONS ENCODING")
        print("=" * 60)

        options = first_question.get("options", [])
        if options:
            for i, opt in enumerate(options[:2], 1):  # Check first 2 options
                opt_text = opt.get("text", {})
                print(f"\nOption {i}:")
                print(f"  Value: {opt.get('value')}")
                print(f"  English: {opt_text.get('en')}")
                ta_opt = opt_text.get('ta')
                if ta_opt:
                    print(f"  Tamil: {ta_opt}")
                    if ord(ta_opt[0]) in range(0x0B80, 0x0C00):
                        print("  ✓ Tamil encoding correct")
                    else:
                        print("  ✗ Tamil encoding CORRUPTED")

        print("\n" + "=" * 60)
        print("HTTP HEADERS")
        print("=" * 60)
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')}")

        print("\n" + "=" * 60)
        print("VERDICT")
        print("=" * 60)

        if tamil_text and ord(tamil_text[0]) in range(0x0B80, 0x0C00):
            print("✓ Unicode encoding is CORRECT in HTTP response")
            print("  Tamil text properly encoded as UTF-8")
            print("  Any console display issues are local terminal encoding problems")
        else:
            print("✗ Unicode encoding CORRUPTED in HTTP response")
            print("  Data corruption exists at HTTP/JSON serialization layer")

    except Exception as e:
        print(f"✗ Failed to start conversation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set console encoding for Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    test_unicode_encoding()
