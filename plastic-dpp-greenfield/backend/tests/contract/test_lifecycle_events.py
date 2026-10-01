def _register(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    return client.post("/products", json=payload, headers=manufacturer_headers).json()


def _txn(client, headers):
    return client.post("/transactions", json={"value": 1.0}, headers=headers).json()["transaction_id"]


def test_transition_success(client, manufacturer_headers, consumer_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    txn = _txn(client, consumer_headers)
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=consumer_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["prior_state"] == "manufactured"
    assert body["new_state"] == "owned"
    assert body["transaction_id"] == txn


def test_transition_missing_transaction_returns_400(client, manufacturer_headers, consumer_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": "TXN-000000"},
        headers=consumer_headers,
    )
    assert response.status_code == 400


def test_transition_reused_transaction_returns_400(client, manufacturer_headers, consumer_headers, recycler_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    txn = _txn(client, consumer_headers)
    client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=consumer_headers,
    )
    # reuse the same transaction for the next transition
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "collected", "transaction_id": txn},
        headers=recycler_headers,
    )
    assert response.status_code == 400


def test_transition_wrong_role_returns_403(client, manufacturer_headers, consumer_headers, recycler_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    txn = _txn(client, recycler_headers)
    # recycler cannot perform the consumer-only manufactured->owned transition
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=recycler_headers,
    )
    assert response.status_code == 403


def test_transition_unknown_product_returns_404(client, consumer_headers):
    txn = _txn(client, consumer_headers)
    response = client.post(
        "/products/DPP-999999/lifecycle-events",
        json={"target_state": "owned", "transaction_id": txn},
        headers=consumer_headers,
    )
    assert response.status_code == 404


def test_transition_out_of_order_returns_409(client, manufacturer_headers, recycler_headers):
    dpp = _register(client, manufacturer_headers)["dpp_id"]
    txn = _txn(client, recycler_headers)
    # skipping manufactured->owned straight to collected is invalid
    response = client.post(
        f"/products/{dpp}/lifecycle-events",
        json={"target_state": "collected", "transaction_id": txn},
        headers=recycler_headers,
    )
    assert response.status_code == 409
