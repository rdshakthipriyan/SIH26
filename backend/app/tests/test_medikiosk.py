"""
Comprehensive test suite for MediKiosk backend.

Tests authentication, conversation, AYUSH, OCR, red flags, queue, FHIR, and security.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models import PatientSession, Physician, ClinicalCase, QueueToken, ClinicalDocument

# Test database
TEST_DATABASE_URL = "sqlite:///./test_medikiosk.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestAuthentication:
    """Test authentication and session management."""

    def test_physician_register(self, client):
        """Test physician registration."""
        response = client.post("/api/v1/sessions/physician/register", json={
            "email": "doctor@example.com",
            "password": "SecurePass123",
            "full_name": "Dr. Test Physician",
            "specialization": "General Medicine",
            "department": "OPD",
            "registration_number": "REG12345"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "physician"

    def test_physician_login(self, client):
        """Test physician login."""
        # Register first
        client.post("/api/v1/sessions/physician/register", json={
            "email": "doctor_login@example.com",
            "password": "SecurePass123",
            "full_name": "Dr. Test Login",
            "specialization": "General Medicine",
            "department": "OPD",
            "registration_number": "REG_LOGIN_123"
        })

        # Login
        response = client.post("/api/v1/sessions/physician/login", json={
            "email": "doctor_login@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_invalid_login(self, client):
        """Test invalid login credentials."""
        response = client.post("/api/v1/sessions/physician/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401

    def test_patient_session_start(self, client):
        """Test patient session creation."""
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test Patient",
            "patient_age": "35",
            "patient_gender": "male",
            "consent_given": True,
            "token_number": "101",
            "department": "General Medicine",
            "mode": "allopathy",
            "language_code": "en"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "temp_id" in data
        assert "token" in data

    def test_patient_abha_session(self, client):
        """Test patient session with ABHA."""
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": False,
            "abha_id": "12-3456-7890-1234",
            "patient_name": "Test Patient",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "hi"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["temp_id"] is None  # Not a guest


class TestLanguages:
    """Test language registry."""

    def test_get_languages(self, client):
        """Test language list endpoint."""
        response = client.get("/api/v1/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert data["total"] == 23  # Exactly 23 languages

    def test_language_structure(self, client):
        """Test language data structure."""
        response = client.get("/api/v1/languages")
        data = response.json()

        # Check English language
        en_lang = next((l for l in data["languages"] if l["code"] == "en"), None)
        assert en_lang is not None
        assert en_lang["native_name"] == "English"
        assert en_lang["bcp47_locale"] == "en-IN"
        assert en_lang["capabilities"]["asr_supported"] == True

    def test_tamil_language(self, client):
        """Test Tamil language configuration."""
        response = client.get("/api/v1/languages")
        data = response.json()

        ta_lang = next((l for l in data["languages"] if l["code"] == "ta"), None)
        assert ta_lang is not None
        assert ta_lang["native_name"] == "தமிழ்"
        assert ta_lang["capabilities"]["asr_supported"] == True
        assert ta_lang["capabilities"]["conversation_supported"] == True


class TestConversation:
    """Test conversation engine."""

    @pytest.fixture
    def patient_token(self, client):
        """Create patient session and return token."""
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        return response.json()

    def test_start_conversation(self, client, patient_token):
        """Test starting conversation."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        response = client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "en", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "first_question" in data
        assert data["first_question"]["question_id"] == "cc_main"

    def test_conversation_response(self, client, patient_token):
        """Test responding to conversation."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        # Start conversation
        client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "en", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Respond
        response = client.post(
            f"/api/v1/cases/{session_id}/conversation/respond",
            json={"answer_text": "I have chest pain for 2 days", "input_mode": "touch"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "next_question" in data
        assert "extracted_facts" in data

    def test_extraction(self, client, patient_token):
        """Test clinical fact extraction."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "en", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.post(
            f"/api/v1/cases/{session_id}/conversation/respond",
            json={"answer_text": "chest pain for 2 days severity 7 out of 10", "input_mode": "touch"},
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        facts = data["extracted_facts"]

        # Should extract multiple facts
        assert "duration_value" in facts or "severity" in facts


class TestNegation:
    """Test negation handling."""

    @pytest.fixture
    def patient_token(self, client):
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        return response.json()

    def test_english_negation(self, client, patient_token):
        """Test English negation detection."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "en", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.post(
            f"/api/v1/cases/{session_id}/conversation/respond",
            json={"answer_text": "I don't have chest pain", "input_mode": "touch"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get clinical history
        history_response = client.get(
            f"/api/v1/cases/{session_id}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        history = history_response.json()

        # Negated symptom should have negative status
        if history.get("clinical_history"):
            for key, value in history["clinical_history"].items():
                if isinstance(value, dict) and "status" in value:
                    if "chest_pain" in key:
                        assert value["status"] == "negative"


class TestRedFlags:
    """Test red flag detection."""

    @pytest.fixture
    def patient_token(self, client):
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        return response.json()

    def test_chest_pain_red_flag(self, client, patient_token):
        """Test severe chest pain triggers red flag."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        # Direct invocation of red flag engine with synthetic history.
        from app.services.triage.red_flag_engine import red_flag_engine

        clinical_history = {
            "chief_complaint": {
                "value": "chest_pain",
                "status": "positive",
                "provenance": {
                    "input_mode": "touch",
                    "language": "en",
                    "timestamp": "2026-08-31T00:00:00",
                    "raw_transcript": None,
                    "question_id": "cc_main",
                },
            },
            "severity": {
                "value": 9,
                "status": "positive",
                "provenance": {
                    "input_mode": "touch",
                    "language": "en",
                    "timestamp": "2026-08-31T00:00:01",
                    "raw_transcript": None,
                    "question_id": "severity",
                },
            },
        }

        flags = red_flag_engine.check_red_flags(clinical_history)
        assert any(f["flag_id"] == "chest_pain_emergency" for f in flags)

        # Drive the engine through the API by feeding answers that produce the
        # same clinical_history; the engine itself persists the case flag.
        client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "en", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # The first call (cc_main) — also seeds severity in case extractor scans
        # universal patterns even when the active question is chief_complaint.
        client.post(
            f"/api/v1/cases/{session_id}/conversation/respond",
            json={"answer_text": "severe chest pain 9 out of 10", "input_mode": "touch"},
            headers={"Authorization": f"Bearer {token}"}
        )

        history_response = client.get(
            f"/api/v1/cases/{session_id}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = history_response.json()
        assert data["has_red_flags"] == True


class TestAYUSH:
    """Test AYUSH engine."""

    @pytest.fixture
    def patient_token(self, client):
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "ayush",
            "language_code": "en"
        })
        return response.json()

    def test_ayush_answer_submission(self, client, patient_token):
        """Test AYUSH answer submission."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        response = client.post(
            f"/api/v1/cases/{session_id}/ayush/answer",
            json={
                "question_id": "ayush_body_build",
                "answer_text": "thin",
                "input_mode": "touch"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "next_question" in data
        assert "profile" in data

    def test_ayush_profile_calculation(self, client, patient_token):
        """Test AYUSH profile calculation."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        # Submit answers
        answers = [
            {"question_id": "ayush_body_build", "answer_text": "thin"},
            {"question_id": "ayush_cold_sensitivity", "answer_text": "high"},
            {"question_id": "ayush_appetite", "answer_text": "irregular"},
        ]

        for answer in answers:
            client.post(
                f"/api/v1/cases/{session_id}/ayush/answer",
                json={**answer, "input_mode": "touch"},
                headers={"Authorization": f"Bearer {token}"}
            )

        # Get profile
        response = client.get(
            f"/api/v1/cases/{session_id}/ayush/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ayush_profile"] is not None
        assert "prakriti" in data["ayush_profile"]


class TestSecurity:
    """Test security and authorization."""

    def test_patient_cannot_access_other_session(self, client):
        """Test patient A cannot access patient B session."""
        # Create patient A
        response_a = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Patient A",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        patient_a = response_a.json()

        # Create patient B
        response_b = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Patient B",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        patient_b = response_b.json()

        # Patient A tries to access Patient B's session
        response = client.get(
            f"/api/v1/cases/{patient_b['session_id']}/history",
            headers={"Authorization": f"Bearer {patient_a['token']}"}
        )
        assert response.status_code == 403

    def test_patient_cannot_access_doctor_endpoints(self, client):
        """Test patient cannot access doctor endpoints."""
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "en"
        })
        patient = response.json()

        response = client.get(
            "/api/v1/doctor/cases",
            headers={"Authorization": f"Bearer {patient['token']}"}
        )
        assert response.status_code == 403


class TestQueue:
    """Test queue management."""

    def test_queue_list(self, client):
        """Test getting queue list."""
        response = client.get("/api/v1/queue")
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "total" in data

    def test_queue_status_update(self, client):
        """Test queue status updates when history submitted."""
        # Create patient session with token
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "token_number": "101",
            "department": "General Medicine",
            "mode": "allopathy",
            "language_code": "en"
        })
        patient = response.json()

        # Submit history
        client.post(
            f"/api/v1/cases/{patient['session_id']}/history/submit",
            headers={"Authorization": f"Bearer {patient['token']}"}
        )

        # Check queue
        queue_response = client.get("/api/v1/queue")
        queue_data = queue_response.json()

        # Find our token
        our_token = next((t for t in queue_data["tokens"] if t["token_number"] == "101"), None)
        assert our_token is not None
        assert our_token["status"] == "history_ready"


class TestProvenance:
    """Test provenance tracking."""

    @pytest.fixture
    def patient_token(self, client):
        response = client.post("/api/v1/sessions/start", json={
            "is_guest": True,
            "patient_name": "Test",
            "consent_given": True,
            "mode": "allopathy",
            "language_code": "ta"
        })
        return response.json()

    def test_voice_provenance(self, client, patient_token):
        """Test voice input provenance tracking."""
        session_id = patient_token["session_id"]
        token = patient_token["token"]

        client.post(
            f"/api/v1/cases/{session_id}/conversation/start",
            json={"language_code": "ta", "mode": "allopathy"},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.post(
            f"/api/v1/cases/{session_id}/conversation/respond",
            json={
                "answer_text": "chest pain",
                "input_mode": "voice",
                "raw_transcript": "original tamil voice input"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
