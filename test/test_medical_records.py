from tests.conftest import (
    make_patient, make_doctor, make_appointment,
    make_medicine, make_medical_record,
)


class TestCreateMedicalRecord:
    def test_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        r = client.post("/medical-records/", json={
            "patient_id": p["patient_id"],
            "doctor_id": d["doctor_id"],
            "diagnosis": "Type 2 Diabetes",
            "symptoms": "Frequent urination, fatigue",
        })
        assert r.status_code == 201
        assert r.json()["diagnosis"] == "Type 2 Diabetes"

    def test_with_appointment(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        a = make_appointment(client, p["patient_id"], d["doctor_id"])
        r = client.post("/medical-records/", json={
            "patient_id": p["patient_id"],
            "doctor_id": d["doctor_id"],
            "appointment_id": a["appointment_id"],
            "diagnosis": "Flu",
        })
        assert r.status_code == 201
        assert r.json()["appointment_id"] == a["appointment_id"]

    def test_invalid_patient_rejected(self, client):
        d = make_doctor(client)
        r = client.post("/medical-records/", json={
            "patient_id": 99999,
            "doctor_id": d["doctor_id"],
            "diagnosis": "Test",
        })
        assert r.status_code == 404

    def test_invalid_doctor_rejected(self, client):
        p = make_patient(client)
        r = client.post("/medical-records/", json={
            "patient_id": p["patient_id"],
            "doctor_id": 99999,
            "diagnosis": "Test",
        })
        assert r.status_code == 404


class TestGetMedicalRecord:
    def test_get_existing(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        r = client.get(f"/medical-records/{rec['record_id']}")
        assert r.status_code == 200

    def test_get_nonexistent(self, client):
        assert client.get("/medical-records/99999").status_code == 404


class TestListMedicalRecords:
    def test_filter_by_patient(self, client):
        p1 = make_patient(client, phone="111")
        p2 = make_patient(client, phone="222")
        d = make_doctor(client)
        make_medical_record(client, p1["patient_id"], d["doctor_id"])
        make_medical_record(client, p2["patient_id"], d["doctor_id"])
        r = client.get(f"/medical-records/?patient_id={p1['patient_id']}")
        assert all(rec["patient_id"] == p1["patient_id"] for rec in r.json())


class TestUpdateMedicalRecord:
    def test_update_diagnosis(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        r = client.put(f"/medical-records/{rec['record_id']}", json={"diagnosis": "Updated Diagnosis"})
        assert r.status_code == 200
        assert r.json()["diagnosis"] == "Updated Diagnosis"


class TestDeleteMedicalRecord:
    def test_delete_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        assert client.delete(f"/medical-records/{rec['record_id']}").status_code == 204
        assert client.get(f"/medical-records/{rec['record_id']}").status_code == 404


# ── Prescriptions ───────────────────────────────────────────────────────────────

class TestPrescriptions:
    def test_add_prescription_success(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med = make_medicine(client, stock_quantity=50)

        r = client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
            "medical_record_id": rec["record_id"],
            "medicine_id": med["medicine_id"],
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "7 days",
            "quantity": 14,
        })
        assert r.status_code == 201
        assert r.json()["quantity"] == 14

    def test_adding_prescription_deducts_stock(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med = make_medicine(client, stock_quantity=50)

        client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
            "medical_record_id": rec["record_id"],
            "medicine_id": med["medicine_id"],
            "dosage": "250mg",
            "frequency": "Once daily",
            "duration": "5 days",
            "quantity": 10,
        })

        updated = client.get(f"/medicines/{med['medicine_id']}").json()
        assert updated["stock_quantity"] == 40

    def test_insufficient_stock_rejected(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med = make_medicine(client, stock_quantity=5)

        r = client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
            "medical_record_id": rec["record_id"],
            "medicine_id": med["medicine_id"],
            "dosage": "100mg",
            "frequency": "Daily",
            "duration": "30 days",
            "quantity": 100,
        })
        assert r.status_code == 400
        assert "stock" in r.json()["detail"].lower()

    def test_delete_prescription_restores_stock(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med = make_medicine(client, stock_quantity=50)

        presc = client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
            "medical_record_id": rec["record_id"],
            "medicine_id": med["medicine_id"],
            "dosage": "100mg",
            "frequency": "Daily",
            "duration": "10 days",
            "quantity": 10,
        }).json()

        client.delete(f"/medical-records/prescriptions/{presc['prescription_id']}")
        restored = client.get(f"/medicines/{med['medicine_id']}").json()
        assert restored["stock_quantity"] == 50

    def test_list_prescriptions_for_record(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med1 = make_medicine(client, medicine_name="MedX", stock_quantity=100)
        med2 = make_medicine(client, medicine_name="MedY", stock_quantity=100)

        for med in [med1, med2]:
            client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
                "medical_record_id": rec["record_id"],
                "medicine_id": med["medicine_id"],
                "dosage": "100mg",
                "frequency": "Daily",
                "duration": "5 days",
                "quantity": 5,
            })

        r = client.get(f"/medical-records/{rec['record_id']}/prescriptions")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_mismatched_record_id_rejected(self, client):
        p = make_patient(client)
        d = make_doctor(client)
        rec = make_medical_record(client, p["patient_id"], d["doctor_id"])
        med = make_medicine(client)

        r = client.post(f"/medical-records/{rec['record_id']}/prescriptions", json={
            "medical_record_id": 99999,  # does not match URL
            "medicine_id": med["medicine_id"],
            "dosage": "100mg",
            "frequency": "Daily",
            "duration": "5 days",
            "quantity": 1,
        })
        assert r.status_code == 400
