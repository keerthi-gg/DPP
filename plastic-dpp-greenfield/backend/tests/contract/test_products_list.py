def test_list_products_returns_list(client, regulator_headers):
    response = client.get("/products", headers=regulator_headers)
    assert response.status_code == 200
    body = response.json()
    assert "products" in body
    assert isinstance(body["products"], list)
