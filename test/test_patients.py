from tests.conftest import make_patient


class TestCreatePatient:
    def test_success(self, client):
        r = client.post("/patients/", json={
            "first_name": "Jane",
            "last_name": "Doe",
            "date_of_birth": "1995-03-20",
            "gender": "Female",
            "phone": "9811111111",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["first_name"] == "Jane"
        assert data["phone"] == "9811111111"
        assert "patient_id" in data

    def test_duplicate_phone_rejected(self, client):
        make_patient(client, phone="9800000099")
        r = client.post("/patients/", json={
            "first_name": "Bob",
            "last_name": "Builder",
            "date_of_birth": "1988-01-01",
            "gender": "Male",
            "phone": "9800000099",
        })
        assert r.status_code == 400
        assert "phone" in r.json()["detail"].lower()

    def test_invalid_gender_rejected(self, client):
        r = client.post("/patients/", json={
            "first_name": "X",
            "last_name": "Y",
            "date_of_birth": "1990-01-01",
            "gender": "Robot",
            "phone": "9800000077",
        })
        assert r.status_code == 422

    def test_missing_required_fields(self, client):
        r = client.post("/patients/", json={"first_name": "OnlyName"})
        assert r.status_code == 422


class TestGetPatient:
    def test_get_existing(self, client):
        p = make_patient(client)
        r = client.get(f"/patients/{p['patient_id']}")
        assert r.status_code == 200
        assert r.json()["patient_id"] == p["patient_id"]

    def test_get_nonexistent(self, client):
        r = client.get("/patients/99999")
        assert r.status_code == 404


class TestListPatients:
    def test_returns_all(self, client):
        make_patient(client, phone="111")
        make_patient(client, phone="222")
        r = client.get("/patients/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_search_by_name(self, client):
        make_patient(client, first_name="Alice", phone="333")
        make_patient(client, first_name="Bob", phone="444")
        r = client.get("/patients/?search=Alice")
        assert r.status_code == 200
        results = r.json()
        assert len(results) == 1
        assert results[0]["first_name"] == "Alice"

    def test_search_by_phone(self, client):
        make_patient(client, phone="9876543210")
        r = client.get("/patients/?search=9876543210")
        assert len(r.json()) == 1

    def test_pagination(self, client):
        for i in range(5):
            make_patient(client, phone=f"100000000{i}")
        r = client.get("/patients/?skip=2&limit=2")
        assert len(r.json()) == 2


class TestUpdatePatient:
    def test_update_fields(self, client):
        p = make_patient(client)
        r = client.put(f"/patients/{p['patient_id']}", json={"address": "123 Main St"})
        assert r.status_code == 200
        assert r.json()["address"] == "123 Main St"

    def test_update_nonexistent(self, client):
        r = client.put("/patients/99999", json={"address": "Nowhere"})
        assert r.status_code == 404


class TestDeletePatient:
    def test_delete_success(self, client):
        p = make_patient(client)
        r = client.delete(f"/patients/{p['patient_id']}")
        assert r.status_code == 204
        assert client.get(f"/patients/{p['patient_id']}").status_code == 404

    def test_delete_nonexistent(self, client):
        r = client.delete("/patients/99999")
        assert r.status_code == 404
