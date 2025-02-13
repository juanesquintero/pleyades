def test_root_json_data(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json.get("api") == "Pleyades"
