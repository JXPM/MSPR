"""
Tests du endpoint /health
==========================
Le healthcheck est utilisé par Docker pour décider si le service est prêt,
et par la page Supervision du frontend. Il doit toujours répondre 200.

Compétence MSPR : « Mise à disposition via API REST [...] endpoints clairs »
"""
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
        """Le healthcheck doit être public (pas de token requis)."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "WWW-Authenticate" not in response.headers
