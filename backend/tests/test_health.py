import pytest


@pytest.mark.integration
class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_payload(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}

    def test_health_does_not_require_auth(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert "WWW-Authenticate" not in response.headers
