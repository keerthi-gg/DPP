def _register(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    return client.post("/products", json=payload, headers=manufacturer_headers).json()


def test_lookup_by_dpp_id_success(client, manufacturer_headers, consumer_headers):
    created = _register(client, manufacturer_headers)
    response = client.get(f"/products/{created['dpp_id']}", headers=consumer_headers)
    assert response.status_code == 200
    assert response.json()["dpp_id"] == created["dpp_id"]


def test_lookup_by_dpp_id_not_found(client, consumer_headers):
    response = client.get("/products/DPP-999999", headers=consumer_headers)
    assert response.status_code == 404
