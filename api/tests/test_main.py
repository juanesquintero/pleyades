


def test_json_data(client):
    response = client.get("/", )
    assert response.json.get("api") == "pleyades"
