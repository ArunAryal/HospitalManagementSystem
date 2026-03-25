from tests.conftest import make_patient, make_doctor, make_appointment


class TestCreateAppointment:
    def test_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        r = client.post("/appointments/", json={
            "patient_id": p["patient_id"],
            "doctor_id": d["doctor_id"],
            "appointment_date": "2025-12-01",
            "appointment_time": "09:00:00",
            "reason": "Chest pain",
        })
        assert r.status_code == 201
        assert r.json()["status"] == "Scheduled"

    def test_invalid_patient_rejected(self, client):
        d = make_doctor(client)
        r = client.post("/appointments/", json={
            "patient_id": 99999,
            "doctor_id": d["doctor_id"],
            "appointment_date": "2025-12-01",
            "appointment_time": "09:00:00",
        })
        assert r.status_code == 404

    def test_unavailable_doctor_rejected(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        client.put(f"/doctors/{d['doctor_id']}", json={"is_available": False})
        r = client.post("/appointments/", json={
            "patient_id": p["patient_id"],
            "doctor_id": d["doctor_id"],
            "appointment_date": "2025-12-01",
            "appointment_time": "09:00:00",
        })
        assert r.status_code == 400

    def test_conflict_rejected(self, client):
        p = make_patient(client, phone="111")
        p2 = make_patient(client, phone="222")
        d = make_doctor(client)
        make_appointment(client, p["patient_id"], d["doctor_id"],
                         appointment_date="2025-12-01", appointment_time="10:00:00")
        r = client.post("/appointments/", json={
            "patient_id": p2["patient_id"],
            "doctor_id": d["doctor_id"],
            "appointment_date": "2025-12-01",
            "appointment_time": "10:00:00",
        })
        assert r.status_code == 409

    def test_same_doctor_different_time_allowed(self, client):
        p = make_patient(client, phone="333")
        p2 = make_patient(client, phone="444")
        d = make_doctor(client)
        make_appointment(client, p["patient_id"], d["doctor_id"],
                         appointment_date="2025-12-01", appointment_time="10:00:00")
        r = client.post("/appointments/", json={
            "patient_id": p2["patient_id"],
            "doctor_id": d["doctor_id"],
            "appointment_date": "2025-12-01",
            "appointment_time": "11:00:00",
        })
        assert r.status_code == 201


class TestGetAppointment:
    def test_get_existing(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        r = client.get(f"/appointments/{a['appointment_id']}")
        assert r.status_code == 200

    def test_get_nonexistent(self, client):
        assert client.get("/appointments/99999").status_code == 404


class TestListAppointments:
    def test_filter_by_patient(self, client):
        p1 = make_patient(client, phone="001")
        p2 = make_patient(client, phone="002")
        d = make_doctor(client)
        make_appointment(client, p1["patient_id"], d["doctor_id"], appointment_time="08:00:00")
        make_appointment(client, p2["patient_id"], d["doctor_id"], appointment_time="09:00:00")
        r = client.get(f"/appointments/?patient_id={p1['patient_id']}")
        assert all(a["patient_id"] == p1["patient_id"] for a in r.json())

    def test_filter_by_date(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        make_appointment(client, p["patient_id"], d["doctor_id"],
                         appointment_date="2025-11-01", appointment_time="08:00:00")
        make_appointment(client, p["patient_id"], d["doctor_id"],
                         appointment_date="2025-12-01", appointment_time="09:00:00")
        r = client.get("/appointments/?appointment_date=2025-11-01")
        assert all(a["appointment_date"] == "2025-11-01" for a in r.json())

    def test_filter_by_status(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        client.put(f"/appointments/{a['appointment_id']}", json={"status": "Completed"})
        r = client.get("/appointments/?status=Completed")
        assert all(a["status"] == "Completed" for a in r.json())


class TestUpdateAppointment:
    def test_update_status_to_completed(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        r = client.put(f"/appointments/{a['appointment_id']}", json={"status": "Completed"})
        assert r.status_code == 200
        assert r.json()["status"] == "Completed"

    def test_update_status_to_no_show(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        r = client.put(f"/appointments/{a['appointment_id']}", json={"status": "No-Show"})
        assert r.status_code == 200
        assert r.json()["status"] == "No-Show"

    def test_invalid_status_rejected(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        r = client.put(f"/appointments/{a['appointment_id']}", json={"status": "Gone"})
        assert r.status_code == 422


class TestDeleteAppointment:
    def test_delete_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        assert client.delete(f"/appointments/{a['appointment_id']}").status_code == 204
        assert client.get(f"/appointments/{a['appointment_id']}").status_code == 404
