def _register(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    return client.post("/products", json=payload, headers=manufacturer_headers).json()


def test_history_empty_then_populated(client, manufacturer_headers, consumer_headers, regulator_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    empty = client.get(f"/products/{dpp}/history", headers=regulator_headers)
    assert empty.status_code == 200
    assert empty.json()["events"] == []

    txn = client.post("/transactions", json={"value": 1.0}, headers=consumer_headers).json()["transaction_id"]
    client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=consumer_headers,
    )
    populated = client.get(f"/products/{dpp}/history", headers=regulator_headers)
    assert populated.status_code == 200
    events = populated.json()["events"]
    assert len(events) == 1
    assert events[0]["new_state"] == "owned"


def test_history_unknown_product_returns_404(client, regulator_headers):
    response = client.get("/products/DPP-999999/history", headers=regulator_headers)
    assert response.status_code == 404
