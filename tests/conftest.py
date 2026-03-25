import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

# In-memory SQLite — no MySQL server needed for tests
SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=engine)

    # Create SQLite triggers for room occupancy management
    db = TestingSessionLocal()
    try:
        # Trigger to update room occupancy on admission insert
        db.execute(
            text("""
            CREATE TRIGGER IF NOT EXISTS after_admission_insert
            AFTER INSERT ON admissions
            FOR EACH ROW
            WHEN NEW.status = 'Active'
            BEGIN
                UPDATE rooms 
                SET current_occupancy = current_occupancy + 1,
                    is_available = CASE 
                        WHEN (current_occupancy + 1) >= capacity THEN 0 
                        ELSE 1 
                    END
                WHERE room_id = NEW.room_id;
            END;
        """)
        )

        # Trigger to update room occupancy on admission discharge
        db.execute(
            text("""
            CREATE TRIGGER IF NOT EXISTS after_admission_update
            AFTER UPDATE ON admissions
            FOR EACH ROW
            WHEN OLD.status = 'Active' AND NEW.status = 'Discharged'
            BEGIN
                UPDATE rooms 
                SET current_occupancy = MAX(0, current_occupancy - 1),
                    is_available = 1
                WHERE room_id = NEW.room_id;
            END;
        """)
        )

        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Wipe all rows between tests so each test starts fresh."""
    yield
    db = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Shared factory helpers ──────────────────────────────────────────────────────


def make_patient(client, **overrides):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-05-15",
        "gender": "Male",
        "phone": "9800000001",
        "blood_group": "O+",
        "email": "john@example.com",
        **overrides,
    }
    r = client.post("/patients/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_doctor(client, **overrides):
    payload = {
        "first_name": "Dr. Alice",
        "last_name": "Smith",
        "specialization": "Cardiology",
        "phone": "9800000002",
        "email": "alice@hospital.com",
        "consultation_fee": "500.00",
        "joined_date": "2020-01-01",
        **overrides,
    }
    r = client.post("/doctors/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_appointment(client, patient_id, doctor_id, **overrides):
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01",
        "appointment_time": "10:00:00",
        "reason": "Routine checkup",
        **overrides,
    }
    r = client.post("/appointments/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_medicine(client, **overrides):
    payload = {
        "medicine_name": "Paracetamol",
        "unit_price": "10.00",
        "stock_quantity": 100,
        "reorder_level": 10,
        **overrides,
    }
    r = client.post("/medicines/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_room(client, **overrides):
    payload = {
        "room_number": "101",
        "room_type": "General",
        "capacity": 2,
        "charge_per_day": "1000.00",
        **overrides,
    }
    r = client.post("/rooms", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_medical_record(
    client, patient_id, doctor_id, appointment_id=None, **overrides
):
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": appointment_id,
        "diagnosis": "Hypertension",
        "symptoms": "Headache, dizziness",
        "treatment": "Medication",
        **overrides,
    }
    r = client.post("/medical-records/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()
