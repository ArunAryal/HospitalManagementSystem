from tests.conftest import make_medicine


class TestCreateMedicine:
    def test_success(self, client):
        r = client.post("/medicines/", json={
            "medicine_name": "Ibuprofen",
            "unit_price": "15.00",
            "stock_quantity": 200,
        })
        assert r.status_code == 201
        assert r.json()["medicine_name"] == "Ibuprofen"

    def test_duplicate_name_rejected(self, client):
        make_medicine(client, medicine_name="Amoxicillin")
        r = client.post("/medicines/", json={
            "medicine_name": "Amoxicillin",
            "unit_price": "20.00",
            "stock_quantity": 50,
        })
        assert r.status_code == 400

    def test_negative_price_rejected(self, client):
        r = client.post("/medicines/", json={
            "medicine_name": "FakeMed",
            "unit_price": "-5.00",
            "stock_quantity": 10,
        })
        assert r.status_code == 422

    def test_negative_stock_rejected(self, client):
        r = client.post("/medicines/", json={
            "medicine_name": "BadStock",
            "unit_price": "5.00",
            "stock_quantity": -1,
        })
        assert r.status_code == 422


class TestGetMedicine:
    def test_get_existing(self, client):
        m = make_medicine(client)
        r = client.get(f"/medicines/{m['medicine_id']}")
        assert r.status_code == 200
        assert r.json()["medicine_id"] == m["medicine_id"]

    def test_get_nonexistent(self, client):
        assert client.get("/medicines/99999").status_code == 404


class TestListMedicines:
    def test_returns_all(self, client):
        make_medicine(client, medicine_name="DrugA")
        make_medicine(client, medicine_name="DrugB")
        r = client.get("/medicines/")
        assert len(r.json()) == 2

    def test_search_by_name(self, client):
        make_medicine(client, medicine_name="Metformin")
        make_medicine(client, medicine_name="Aspirin")
        r = client.get("/medicines/?search=Metformin")
        assert len(r.json()) == 1
        assert r.json()[0]["medicine_name"] == "Metformin"

    def test_low_stock_filter(self, client):
        make_medicine(client, medicine_name="LowDrug", stock_quantity=5, reorder_level=10)
        make_medicine(client, medicine_name="HighDrug", stock_quantity=100, reorder_level=10)
        r = client.get("/medicines/?low_stock=true")
        names = [m["medicine_name"] for m in r.json()]
        assert "LowDrug" in names
        assert "HighDrug" not in names


class TestLowStockEndpoint:
    def test_dedicated_low_stock_route(self, client):
        make_medicine(client, medicine_name="NearEmpty", stock_quantity=2, reorder_level=10)
        make_medicine(client, medicine_name="FullStock", stock_quantity=500, reorder_level=10)
        r = client.get("/medicines/low-stock")
        assert r.status_code == 200
        names = [m["medicine_name"] for m in r.json()]
        assert "NearEmpty" in names
        assert "FullStock" not in names


class TestUpdateMedicine:
    def test_update_price(self, client):
        m = make_medicine(client)
        r = client.put(f"/medicines/{m['medicine_id']}", json={"unit_price": "25.00"})
        assert r.status_code == 200
        assert float(r.json()["unit_price"]) == 25.0

    def test_update_stock(self, client):
        m = make_medicine(client)
        r = client.put(f"/medicines/{m['medicine_id']}", json={"stock_quantity": 500})
        assert r.json()["stock_quantity"] == 500


class TestRestockMedicine:
    def test_restock_adds_quantity(self, client):
        m = make_medicine(client, stock_quantity=50)
        r = client.patch(f"/medicines/{m['medicine_id']}/restock?quantity=30")
        assert r.status_code == 200
        assert r.json()["stock_quantity"] == 80

    def test_restock_zero_rejected(self, client):
        m = make_medicine(client)
        r = client.patch(f"/medicines/{m['medicine_id']}/restock?quantity=0")
        assert r.status_code == 422


class TestDeleteMedicine:
    def test_delete_success(self, client):
        m = make_medicine(client)
        assert client.delete(f"/medicines/{m['medicine_id']}").status_code == 204
        assert client.get(f"/medicines/{m['medicine_id']}").status_code == 404
