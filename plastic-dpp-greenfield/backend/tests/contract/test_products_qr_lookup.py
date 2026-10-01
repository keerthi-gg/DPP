def _register(client, manufacturer_headers):
    payload = {
        "product_type": "PET bottle",
        "material_summary": "PET, food-grade",
        "manufacture_date": "2026-09-30",
    }
    return client.post("/products", json=payload, headers=manufacturer_headers).json()


def test_lookup_by_qr_success(client, manufacturer_headers, recycler_headers):
    created = _register(client, manufacturer_headers)
    response = client.get(
        "/products/lookup",
        params={"qr_code": created["qr_code_ref"]},
        headers=recycler_headers,
    )
    assert response.status_code == 200
    assert response.json()["dpp_id"] == created["dpp_id"]


def test_lookup_by_qr_not_found(client, recycler_headers):
    response = client.get(
        "/products/lookup", params={"qr_code": "qr://does-not-exist"}, headers=recycler_headers
    )
    assert response.status_code == 404
