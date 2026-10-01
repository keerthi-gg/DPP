def _register(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    return client.post("/products", json=payload, headers=manufacturer_headers).json()


def test_report_success(client, manufacturer_headers, regulator_headers):
    _register(client, manufacturer_headers)
    response = client.get("/regulator/report", headers=regulator_headers)
    assert response.status_code == 200
    body = response.json()
    assert "total_products" in body
    assert "by_state" in body
    assert body["total_products"] >= 1
    assert body["by_state"]["manufactured"] >= 1


def test_report_counts_reflect_transitions(client, manufacturer_headers, consumer_headers, regulator_headers):
    created = _register(client, manufacturer_headers)
    dpp = created["dpp_id"]
    txn = client.post("/transactions", json={"value": 1.0}, headers=consumer_headers).json()["transaction_id"]
    client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=consumer_headers,
    )
    body = client.get("/regulator/report", headers=regulator_headers).json()
    assert body["by_state"]["owned"] >= 1


def test_report_non_regulator_returns_403(client, consumer_headers):
    response = client.get("/regulator/report", headers=consumer_headers)
    assert response.status_code == 403
