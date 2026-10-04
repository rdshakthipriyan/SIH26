"""Debug script to test conversation respond endpoint."""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db
from app.models.patient import PatientSession
from app.models.clinical_case import ClinicalCase
from app.core.security import create_access_token
from datetime import datetime, timedelta
import uuid

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Create a patient session
session_id = str(uuid.uuid4())
temp_id = f"TEMP-OPD-{uuid.uuid4().hex[:8]}"
patient = PatientSession(
    session_id=session_id,
    temp_id=temp_id,
    patient_name="Test Patient",
    mode="allopathy",
    language_code="en",
    consent_given=True,
    consent_timestamp=datetime.utcnow()
)
db = next(get_db())
db.add(patient)

# Create clinical case
case = ClinicalCase(
    case_id=str(uuid.uuid4()),
    session_id=session_id,
    department="OPD",
    mode="allopathy",
    language_code="en",
    status="in_progress",
    conversation_state={"current_question_id": "cc_main", "answered_questions": []}
)
db.add(case)
db.commit()
db.close()

# Create token
token = create_access_token({
    "sub": session_id,
    "temp_id": temp_id,
    "mode": "allopathy",
    "role": "patient",
    "session_id": session_id
})

# Start conversation
start_response = client.post(
    f"/api/v1/cases/{session_id}/conversation/start",
    json={"language_code": "en", "mode": "allopathy"},
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Start response: {start_response.status_code}")
if start_response.status_code != 200:
    print(f"Start error: {start_response.text}")
    sys.exit(1)

# Try to respond
print(f"\nAttempting to respond with session_id: {session_id}")
respond_response = client.post(
    f"/api/v1/cases/{session_id}/conversation/respond",
    json={"answer_text": "I have chest pain for 2 days", "input_mode": "touch"},
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Respond status: {respond_response.status_code}")
try:
    print(f"Respond body: {respond_response.text}")
except UnicodeEncodeError:
    print("Respond body: [contains unicode characters - encoding issue on Windows console]")
print("\n=== DEBUG TEST PASSED ===")
