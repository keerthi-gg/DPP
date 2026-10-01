def test_create_transaction_confirmed(client, consumer_headers):
    response = client.post("/transactions", json={"value": 5.0}, headers=consumer_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["transaction_id"].startswith("TXN-")
    assert body["status"] == "confirmed"
    assert body["linked_event_id"] is None
