from tests.conftest import make_doctor


class TestCreateDoctor:
    def test_success(self, client):
        r = client.post("/doctors/", json={
            "first_name": "Dr. Bob",
            "last_name": "Jones",
            "specialization": "Neurology",
            "phone": "9800000010",
            "email": "bob@hospital.com",
            "consultation_fee": "800.00",
            "joined_date": "2019-06-01",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["specialization"] == "Neurology"
        assert data["is_available"] is True

    def test_duplicate_email_rejected(self, client):
        make_doctor(client, email="unique@hospital.com")
        r = client.post("/doctors/", json={
            "first_name": "Copy",
            "last_name": "Cat",
            "specialization": "ENT",
            "phone": "9800000011",
            "email": "unique@hospital.com",
            "consultation_fee": "300.00",
            "joined_date": "2021-01-01",
        })
        assert r.status_code == 400

    def test_negative_fee_rejected(self, client):
        r = client.post("/doctors/", json={
            "first_name": "X",
            "last_name": "Y",
            "specialization": "GP",
            "phone": "000",
            "email": "x@y.com",
            "consultation_fee": "-100",
            "joined_date": "2021-01-01",
        })
        assert r.status_code == 422


class TestGetDoctor:
    def test_get_existing(self, client):
        d = make_doctor(client)
        r = client.get(f"/doctors/{d['doctor_id']}")
        assert r.status_code == 200
        assert r.json()["doctor_id"] == d["doctor_id"]

    def test_get_nonexistent(self, client):
        assert client.get("/doctors/99999").status_code == 404


class TestListDoctors:
    def test_returns_all(self, client):
        make_doctor(client, email="a@h.com")
        make_doctor(client, email="b@h.com", specialization="ENT")
        r = client.get("/doctors/")
        assert len(r.json()) == 2

    def test_filter_by_specialization(self, client):
        make_doctor(client, email="c@h.com", specialization="Cardiology")
        make_doctor(client, email="d@h.com", specialization="Neurology")
        r = client.get("/doctors/?specialization=Cardiology")
        assert all(d["specialization"] == "Cardiology" for d in r.json())

    def test_filter_available_only(self, client):
        d = make_doctor(client, email="e@h.com")
        client.put(f"/doctors/{d['doctor_id']}", json={"is_available": False})
        make_doctor(client, email="f@h.com")
        r = client.get("/doctors/?available_only=true")
        assert all(doc["is_available"] for doc in r.json())


class TestUpdateDoctor:
    def test_update_fee(self, client):
        d = make_doctor(client)
        r = client.put(f"/doctors/{d['doctor_id']}", json={"consultation_fee": "999.00"})
        assert r.status_code == 200
        assert float(r.json()["consultation_fee"]) == 999.0

    def test_toggle_availability(self, client):
        d = make_doctor(client)
        r = client.put(f"/doctors/{d['doctor_id']}", json={"is_available": False})
        assert r.json()["is_available"] is False


class TestDeleteDoctor:
    def test_delete_success(self, client):
        d = make_doctor(client)
        assert client.delete(f"/doctors/{d['doctor_id']}").status_code == 204
        assert client.get(f"/doctors/{d['doctor_id']}").status_code == 404

    def test_delete_nonexistent(self, client):
        assert client.delete("/doctors/99999").status_code == 404
