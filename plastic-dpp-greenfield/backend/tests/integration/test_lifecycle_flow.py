def test_full_lifecycle_flow(client, manufacturer_headers, consumer_headers, recycler_headers, regulator_headers):
    # register
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    created = client.post("/products", json=payload, headers=manufacturer_headers).json()
    dpp = created["dpp_id"]

    # lookup (read-only)
    assert client.get(f"/products/{dpp}", headers=consumer_headers).json()["current_state"] == "manufactured"

    # walk the full state machine, each gated by its own transaction
    steps = [
        ("owned", consumer_headers),
        ("collected", recycler_headers),
        ("recycled", recycler_headers),
        ("closed", recycler_headers),
    ]
    for target, headers in steps:
        txn = client.post("/transactions", json={"value": 1.0}, headers=headers).json()["transaction_id"]
        resp = client.post(
            f"/products/{dpp}/lifecycle-events",
            json={"target_state": target, "transaction_id": txn},
            headers=headers,
        )
        assert resp.status_code == 201, (target, resp.text)

    # final state and full history
    assert client.get(f"/products/{dpp}", headers=regulator_headers).json()["current_state"] == "closed"
    history = client.get(f"/products/{dpp}/history", headers=regulator_headers).json()["events"]
    assert [e["new_state"] for e in history] == ["owned", "collected", "recycled", "closed"]

    # closed product rejects further transitions
    txn = client.post("/transactions", json={"value": 1.0}, headers=recycler_headers).json()["transaction_id"]
    resp = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "closed", "transaction_id": txn},
        headers=recycler_headers,
    )
    assert resp.status_code == 409
