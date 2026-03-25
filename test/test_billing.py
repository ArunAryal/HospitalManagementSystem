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
