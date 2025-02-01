from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:5001/"


def test_get_books():
    with sync_playwright() as p:
        request = p.request.new_context()
        response = request.get(BASE_URL)
        assert response.ok
        assert isinstance(response.json(), dict)
        assert response.json().get('api') == 'pleyades'


def test_get_book():
    with sync_playwright() as p:
        request = p.request.new_context()
        response = request.get(f"{BASE_URL}/1")
        assert response.ok
        assert response.json()["id"] == 1
