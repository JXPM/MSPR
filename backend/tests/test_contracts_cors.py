"""
Tests transversaux : CORS et contrats Pydantic
================================================
Le frontend Streamlit (sur 8501) consomme l'API (sur 8000) en cross-origin.
Si CORS est mal configuré, le navigateur bloque les requêtes silencieusement.

Compétence MSPR : « Endpoints sécurisés [...] facilement exploitables par
                   les utilisateurs finaux » + « Accessibilité numérique »
"""
import pytest


@pytest.mark.contract
class TestCORS:
    def test_preflight_request(self, client):
        """OPTIONS /trajets/ avec Origin doit retourner les headers CORS."""
        response = client.options(
            "/trajets/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI répond 200 ou 405 selon la config — on vérifie juste les headers
        assert "access-control-allow-origin" in (
            h.lower() for h in response.headers.keys()
        )

    def test_cors_allows_localhost_5173(self, client):
        """Le frontend dev React (port 5173) doit être autorisé."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == \
            "http://localhost:5173"


@pytest.mark.contract
class TestSchemasContract:
    """Vérifie que la forme exacte des réponses ne changera pas sans test."""

    def test_trajet_schema(self, client):
        trajet = client.get("/trajets/SNC-1001").json()
        # Les champs de TrajetResponse
        assert isinstance(trajet["trajet_id"], str)
        assert isinstance(trajet["id_ligne"], int)
        assert isinstance(trajet["gare_depart"], str)
        assert isinstance(trajet["gare_arrivee"], str)
        assert isinstance(trajet["heure_depart"], str)
        assert isinstance(trajet["heure_arrivee"], str)

    def test_gare_schema(self, client):
        gare = next(
            g for g in client.get("/gares/").json() if g["code_uic"] == "FRPNO"
        )
        assert isinstance(gare["code_uic"], str)
        assert isinstance(gare["nom_gare"], str)
        assert gare["latitude"] is None or isinstance(gare["latitude"], (int, float))

    def test_count_schema(self, client):
        """Tous les /count retournent un objet avec une seule clé total_*."""
        count = client.get("/stats/trajets/count").json()
        assert "total_trajets" in count
        assert isinstance(count["total_trajets"], int)
        assert count["total_trajets"] >= 0

    def test_repartition_schema(self, client):
        """{ JOUR: int, NUIT: int }"""
        rep = client.get("/stats/trajets/type").json()
        assert isinstance(rep["JOUR"], int)
        assert isinstance(rep["NUIT"], int)


@pytest.mark.contract
class TestOpenAPIDoc:
    """L'API doit exposer sa documentation OpenAPI (Swagger UI à /docs)."""

    def test_openapi_json_available(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert spec["info"]["title"] == "ObRail Europe API"

    def test_swagger_ui_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
