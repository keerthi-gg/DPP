def test_regulator_cannot_register_product(client, regulator_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    response = client.post("/products", json=payload, headers=regulator_headers)
    assert response.status_code == 403


def test_regulator_cannot_transition(client, manufacturer_headers, consumer_headers, regulator_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    dpp = client.post("/products", json=payload, headers=manufacturer_headers).json()["dpp_id"]
    txn = client.post("/transactions", json={"value": 1.0}, headers=consumer_headers).json()["transaction_id"]
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=regulator_headers,
    )
    assert response.status_code == 403
