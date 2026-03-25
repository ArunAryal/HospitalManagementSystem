from tests.conftest import make_patient, make_doctor, make_appointment


def make_bill(client, patient_id, appointment_id=None, **overrides):
    payload = {
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "consultation_fee": "500.00",
        "medicine_charges": "200.00",
        "room_charges": "0.00",
        "other_charges": "50.00",
        "total_amount": "750.00",
        **overrides,
    }
    r = client.post("/bills/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_room(client, **overrides):
    """Helper to create a room."""
    payload = {
        "room_number": f"R{len(str(id(client)))}",
        "room_type": "General",
        "capacity": 2,
        "charge_per_day": "500.00",
        **overrides,
    }
    r = client.post("/rooms/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_medicine(client, **overrides):
    """Helper to create a medicine."""
    payload = {
        "medicine_name": f"Medicine_{id(overrides)}",
        "unit_price": "100.00",
        "stock_quantity": 100,
        "reorder_level": 10,
        **overrides,
    }
    r = client.post("/medicines/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_admission(client, patient_id, room_id, doctor_id, **overrides):
    """Helper to create an admission."""
    payload = {
        "patient_id": patient_id,
        "room_id": room_id,
        "doctor_id": doctor_id,
        "reason": "General checkup",
        **overrides,
    }
    r = client.post("/admissions/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def make_medical_record(client, patient_id, doctor_id, **overrides):
    """Helper to create a medical record."""
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "diagnosis": "Test diagnosis",
        **overrides,
    }
    r = client.post("/medical-records/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


class TestCreateBill:
    def test_success(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        assert b["payment_status"] == "Pending"
        assert b["paid_amount"] == "0"

    def test_invalid_patient_rejected(self, client):
        r = client.post("/bills/", json={
            "patient_id": 99999,
            "total_amount": "500.00",
        })
        assert r.status_code == 404

    def test_invalid_appointment_rejected(self, client):
        p = make_patient(client)
        r = client.post("/bills/", json={
            "patient_id": p["patient_id"],
            "appointment_id": 99999,
            "total_amount": "500.00",
        })
        assert r.status_code == 404

    def test_negative_total_rejected(self, client):
        p = make_patient(client)
        r = client.post("/bills/", json={
            "patient_id": p["patient_id"],
            "total_amount": "-100.00",
        })
        assert r.status_code == 422


class TestGetBill:
    def test_get_existing(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        r = client.get(f"/bills/{b['bill_id']}")
        assert r.status_code == 200
        assert r.json()["bill_id"] == b["bill_id"]

    def test_get_nonexistent(self, client):
        assert client.get("/bills/99999").status_code == 404


class TestListBills:
    def test_filter_by_patient(self, client):
        p1 = make_patient(client, phone="001")
        p2 = make_patient(client, phone="002")
        make_bill(client, p1["patient_id"])
        make_bill(client, p2["patient_id"])
        r = client.get(f"/bills/?patient_id={p1['patient_id']}")
        assert all(b["patient_id"] == p1["patient_id"] for b in r.json())

    def test_filter_by_payment_status(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        client.put(f"/bills/{b['bill_id']}", json={
            "payment_method": "Cash",
            "paid_amount": "750.00",
        })
        r = client.get("/bills/?payment_status=Paid")
        assert all(bill["payment_status"] == "Paid" for bill in r.json())


class TestUpdateBill:
    def test_full_payment_sets_paid(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"], total_amount="1000.00")
        r = client.put(f"/bills/{b['bill_id']}", json={
            "payment_method": "Card",
            "paid_amount": "1000.00",
        })
        assert r.status_code == 200
        assert r.json()["payment_status"] == "Paid"
        assert r.json()["payment_method"] == "Card"

    def test_partial_payment_sets_partially_paid(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"], total_amount="1000.00")
        r = client.put(f"/bills/{b['bill_id']}", json={
            "payment_method": "Cash",
            "paid_amount": "400.00",
        })
        assert r.json()["payment_status"] == "Partially Paid"

    def test_invalid_payment_method_rejected(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        r = client.put(f"/bills/{b['bill_id']}", json={"payment_method": "Barter"})
        assert r.status_code == 422

    def test_invalid_status_rejected(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        r = client.put(f"/bills/{b['bill_id']}", json={"payment_status": "Free"})
        assert r.status_code == 422


class TestDeleteBill:
    def test_delete_success(self, client):
        p = make_patient(client)
        b = make_bill(client, p["patient_id"])
        assert client.delete(f"/bills/{b['bill_id']}").status_code == 204
        assert client.get(f"/bills/{b['bill_id']}").status_code == 404


class TestAutomaticBillingOnDischarge:
    """Tests for automatic bill generation when a patient is discharged."""

    def test_discharge_creates_bill_with_room_charges(self, client):
        """Test that discharging a patient creates a bill with room charges."""
        patient = make_patient(client)
        doctor = make_doctor(client)
        room = make_room(client, charge_per_day="500.00")
        
        # Create admission
        admission = make_admission(
            client,
            patient_id=patient["patient_id"],
            room_id=room["room_id"],
            doctor_id=doctor["doctor_id"],
        )
        admission_id = admission["admission_id"]
        
        # Discharge patient
        r = client.put(f"/admissions/{admission_id}/discharge")
        assert r.status_code == 200
        
        # Get bills for patient - should have admission bill with room charges
        bills_r = client.get(f"/bills/?patient_id={patient['patient_id']}")
        bills = bills_r.json()
        
        # Should have at least one bill from admission
        admission_bills = [b for b in bills if b["admission_id"] == admission_id]
        assert len(admission_bills) > 0
        admission_bill = admission_bills[0]
        
        # Bill should include room charges
        assert float(admission_bill["room_charges"]) > 0
        assert admission_bill["payment_status"] == "Pending"

    def test_discharge_includes_medicine_charges(self, client):
        """Test that discharge bill includes medicine charges from prescriptions."""
        patient = make_patient(client)
        doctor = make_doctor(client)
        room = make_room(client, charge_per_day="500.00")
        medicine = make_medicine(client, unit_price="100.00")
        
        # Create admission
        admission = make_admission(
            client,
            patient_id=patient["patient_id"],
            room_id=room["room_id"],
            doctor_id=doctor["doctor_id"],
        )
        admission_id = admission["admission_id"]
        
        # Create medical record
        med_record = make_medical_record(
            client,
            patient_id=patient["patient_id"],
            doctor_id=doctor["doctor_id"],
        )
        
        # Add prescription
        prescription_r = client.post(
            f"/medical-records/{med_record['record_id']}/prescriptions",
            json={
                "medical_record_id": med_record["record_id"],
                "medicine_id": medicine["medicine_id"],
                "dosage": "1 tab",
                "frequency": "2x daily",
                "duration": "5 days",
                "quantity": 10,
            },
        )
        assert prescription_r.status_code == 201
        
        # Discharge patient
        r = client.put(f"/admissions/{admission_id}/discharge")
        assert r.status_code == 200
        
        # Get bills for patient
        bills_r = client.get(f"/bills/?patient_id={patient['patient_id']}")
        bills = bills_r.json()
        
        # Should have admission bill with medicine charges
        admission_bills = [b for b in bills if b["admission_id"] == admission_id]
        assert len(admission_bills) > 0
        admission_bill = admission_bills[0]
        
        # Bill should include both room and medicine charges
        assert float(admission_bill["room_charges"]) > 0
        assert float(admission_bill["medicine_charges"]) > 0


class TestAutomaticBillingOnPrescription:
    """Tests for automatic bill updates when medicines are prescribed."""

    def test_prescription_creates_bill_with_medicine_charges(self, client):
        """Test that adding a prescription creates/updates a bill with medicine charges."""
        patient = make_patient(client)
        doctor = make_doctor(client)
        medicine = make_medicine(client, unit_price="50.00")
        
        # Create medical record (appointment-based)
        appointment = make_appointment(client, patient["patient_id"], doctor["doctor_id"])
        med_record = make_medical_record(
            client,
            patient_id=patient["patient_id"],
            doctor_id=doctor["doctor_id"],
            appointment_id=appointment["appointment_id"],
        )
        
        # Add prescription
        prescription_r = client.post(
            f"/medical-records/{med_record['record_id']}/prescriptions",
            json={
                "medical_record_id": med_record["record_id"],
                "medicine_id": medicine["medicine_id"],
                "dosage": "1 tab",
                "frequency": "3x daily",
                "duration": "7 days",
                "quantity": 21,
            },
        )
        assert prescription_r.status_code == 201
        
        # Get bills for patient
        bills_r = client.get(f"/bills/?patient_id={patient['patient_id']}")
        bills = bills_r.json()
        
        # Should have bill with medicine charges (may be grouped with appointment bill)
        assert len(bills) > 0
        bill = bills[0]
        
        # Bill should include medicine charges
        # Expected: 50.00 * 21 = 1050.00
        assert float(bill["medicine_charges"]) == 1050.00

    def test_multiple_prescriptions_accumulate_charges(self, client):
        """Test that multiple prescriptions accumulate in the bill."""
        patient = make_patient(client)
        doctor = make_doctor(client)
        medicine1 = make_medicine(client, medicine_name="Med_A_1", unit_price="50.00")
        medicine2 = make_medicine(client, medicine_name="Med_B_2", unit_price="75.00")
        
        # Create medical record
        med_record = make_medical_record(
            client,
            patient_id=patient["patient_id"],
            doctor_id=doctor["doctor_id"],
        )
        
        # Add first prescription
        prescription_r1 = client.post(
            f"/medical-records/{med_record['record_id']}/prescriptions",
            json={
                "medical_record_id": med_record["record_id"],
                "medicine_id": medicine1["medicine_id"],
                "dosage": "1 tab",
                "frequency": "2x daily",
                "duration": "5 days",
                "quantity": 10,
            },
        )
        assert prescription_r1.status_code == 201
        
        # Add second prescription
        prescription_r2 = client.post(
            f"/medical-records/{med_record['record_id']}/prescriptions",
            json={
                "medical_record_id": med_record["record_id"],
                "medicine_id": medicine2["medicine_id"],
                "dosage": "1 cap",
                "frequency": "1x daily",
                "duration": "7 days",
                "quantity": 7,
            },
        )
        assert prescription_r2.status_code == 201
        
        # Get bills for patient
        bills_r = client.get(f"/bills/?patient_id={patient['patient_id']}")
        bills = bills_r.json()
        
        # Should have bill with accumulated medicine charges
        # Expected: (50 * 10) + (75 * 7) = 500 + 525 = 1025
        assert len(bills) > 0
        bill = bills[0]
        assert float(bill["medicine_charges"]) == 1025.00
