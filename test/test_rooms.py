from tests.conftest import make_patient, make_doctor, make_room


def make_admission(client, patient_id, room_id, doctor_id, **overrides):
    payload = {
        "patient_id": patient_id,
        "room_id": room_id,
        "doctor_id": doctor_id,
        "admission_date": "2025-12-01T08:00:00",
        "reason": "Surgery",
        **overrides,
    }
    r = client.post("/admissions", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


# ── Rooms ───────────────────────────────────────────────────────────────────────

class TestCreateRoom:
    def test_success(self, client):
        r = client.post("/rooms", json={
            "room_number": "201",
            "room_type": "ICU",
            "capacity": 1,
            "charge_per_day": "5000.00",
        })
        assert r.status_code == 201
        assert r.json()["room_type"] == "ICU"
        assert r.json()["is_available"] is True

    def test_duplicate_room_number_rejected(self, client):
        make_room(client, room_number="A1")
        r = client.post("/rooms", json={
            "room_number": "A1",
            "room_type": "General",
            "capacity": 3,
            "charge_per_day": "800.00",
        })
        assert r.status_code == 400

    def test_invalid_room_type_rejected(self, client):
        r = client.post("/rooms", json={
            "room_number": "B1",
            "room_type": "Suite",
            "capacity": 1,
            "charge_per_day": "1000.00",
        })
        assert r.status_code == 422


class TestGetRoom:
    def test_get_existing(self, client):
        room = make_room(client)
        r = client.get(f"/rooms/{room['room_id']}")
        assert r.status_code == 200

    def test_get_nonexistent(self, client):
        assert client.get("/rooms/99999").status_code == 404


class TestListRooms:
    def test_returns_all(self, client):
        make_room(client, room_number="R1")
        make_room(client, room_number="R2", room_type="ICU")
        r = client.get("/rooms")
        assert len(r.json()) == 2

    def test_filter_by_type(self, client):
        make_room(client, room_number="G1", room_type="General")
        make_room(client, room_number="I1", room_type="ICU")
        r = client.get("/rooms?room_type=ICU")
        assert all(room["room_type"] == "ICU" for room in r.json())

    def test_filter_available_only(self, client):
        make_room(client, room_number="AV1", capacity=1)
        p = make_patient(client)
        d = make_doctor(client)
        full_room = make_room(client, room_number="FU1", capacity=1)
        make_admission(client, p["patient_id"], full_room["room_id"], d["doctor_id"])
        r = client.get("/rooms?available_only=true")
        room_ids = [room["room_id"] for room in r.json()]
        assert full_room["room_id"] not in room_ids


class TestUpdateRoom:
    def test_update_charge(self, client):
        room = make_room(client)
        r = client.put(f"/rooms/{room['room_id']}", json={"charge_per_day": "2000.00"})
        assert r.status_code == 200
        assert float(r.json()["charge_per_day"]) == 2000.0


class TestDeleteRoom:
    def test_delete_empty_room(self, client):
        room = make_room(client, room_number="DEL1")
        assert client.delete(f"/rooms/{room['room_id']}").status_code == 204

    def test_delete_occupied_room_rejected(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, room_number="OCC1", capacity=2)
        make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])
        r = client.delete(f"/rooms/{room['room_id']}")
        assert r.status_code == 400


# ── Admissions ──────────────────────────────────────────────────────────────────

class TestAdmitPatient:
    def test_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client)
        r = client.post("/admissions", json={
            "patient_id": p["patient_id"],
            "room_id": room["room_id"],
            "doctor_id": d["doctor_id"],
            "admission_date": "2025-12-01T08:00:00",
            "reason": "Post-op care",
        })
        assert r.status_code == 201
        assert r.json()["status"] == "Active"

    def test_increments_room_occupancy(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, capacity=3)
        make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])
        updated = client.get(f"/rooms/{room['room_id']}").json()
        assert updated["current_occupancy"] == 1

    def test_full_room_marks_unavailable(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, room_number="FULL1", capacity=1)
        make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])
        updated = client.get(f"/rooms/{room['room_id']}").json()
        assert updated["is_available"] is False

    def test_full_room_rejects_new_admission(self, client):
        p1 = make_patient(client, phone="501")
        p2 = make_patient(client, phone="502")
        d = make_doctor(client)
        room = make_room(client, room_number="FULL2", capacity=1)
        make_admission(client, p1["patient_id"], room["room_id"], d["doctor_id"])
        r = client.post("/admissions", json={
            "patient_id": p2["patient_id"],
            "room_id": room["room_id"],
            "doctor_id": d["doctor_id"],
            "admission_date": "2025-12-02T08:00:00",
            "reason": "Second admission",
        })
        assert r.status_code == 400

    def test_invalid_patient_rejected(self, client):
        d = make_doctor(client)
        room = make_room(client, room_number="INV1")
        r = client.post("/admissions", json={
            "patient_id": 99999,
            "room_id": room["room_id"],
            "doctor_id": d["doctor_id"],
            "admission_date": "2025-12-01T08:00:00",
            "reason": "Test",
        })
        assert r.status_code == 404


class TestDischargePatient:
    def test_discharge_frees_room(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, room_number="DSCH1", capacity=1)
        adm = make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])

        r = client.put(f"/admissions/{adm['admission_id']}", json={"status": "Discharged"})
        assert r.status_code == 200
        assert r.json()["status"] == "Discharged"
        assert r.json()["discharge_date"] is not None

        updated_room = client.get(f"/rooms/{room['room_id']}").json()
        assert updated_room["current_occupancy"] == 0
        assert updated_room["is_available"] is True

    def test_manual_discharge_date(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, room_number="DSCH2", capacity=2)
        adm = make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])

        r = client.put(f"/admissions/{adm['admission_id']}", json={
            "status": "Discharged",
            "discharge_date": "2025-12-10T12:00:00",
        })
        assert r.json()["discharge_date"] == "2025-12-10T12:00:00"


class TestListAdmissions:
    def test_filter_by_status(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        room = make_room(client, room_number="LS1", capacity=5)
        adm = make_admission(client, p["patient_id"], room["room_id"], d["doctor_id"])
        client.put(f"/admissions/{adm['admission_id']}", json={"status": "Discharged"})

        r = client.get("/admissions?status=Discharged")
        assert all(a["status"] == "Discharged" for a in r.json())

    def test_filter_by_patient(self, client):
        p1 = make_patient(client, phone="601")
        p2 = make_patient(client, phone="602")
        d = make_doctor(client)
        room = make_room(client, room_number="FP1", capacity=5)
        make_admission(client, p1["patient_id"], room["room_id"], d["doctor_id"])
        make_admission(client, p2["patient_id"], room["room_id"], d["doctor_id"])
        r = client.get(f"/admissions?patient_id={p1['patient_id']}")
        assert all(a["patient_id"] == p1["patient_id"] for a in r.json())
