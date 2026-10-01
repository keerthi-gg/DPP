def test_lookup_does_not_change_state(client, manufacturer_headers, consumer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    created = client.post("/products", json=payload, headers=manufacturer_headers).json()
    dpp_id = created["dpp_id"]

    for _ in range(3):
        client.get(f"/products/{dpp_id}", headers=consumer_headers)
        client.get("/products/lookup", params={"qr_code": created["qr_code_ref"]}, headers=consumer_headers)

    after = client.get(f"/products/{dpp_id}", headers=consumer_headers).json()
    assert after["current_state"] == "manufactured"
