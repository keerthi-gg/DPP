def test_register_product_success(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    response = client.post("/products", json=payload, headers=manufacturer_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["dpp_id"].startswith("DPP-")
    assert body["qr_code_ref"]
    assert body["current_state"] == "manufactured"
    assert body["product_type"] == payload["product_type"]


def test_register_product_missing_field_returns_400(client, manufacturer_headers):
    payload = {"product_type": "PET bottle"}
    response = client.post("/products", json=payload, headers=manufacturer_headers)
    assert response.status_code == 422 or response.status_code == 400


def test_register_product_wrong_role_returns_403(client, consumer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    response = client.post("/products", json=payload, headers=consumer_headers)
    assert response.status_code == 403
