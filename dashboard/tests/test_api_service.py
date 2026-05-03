"""
Tests du client API du dashboard
==================================
Le module services/api_service.py est le SEUL point de contact avec le
backend. Tests basés sur des mocks `requests` pour vérifier :
  - les bonnes URLs construites
  - les bons timeouts utilisés
  - la robustesse aux erreurs (404, timeout, JSON invalide)

Compétence MSPR : « Permettre l'exploitation du jeu de données par les
                   autres composants du projet »
"""
from unittest.mock import patch, MagicMock

import pytest

from services import api_service


@pytest.fixture(autouse=True)
def reset_api_url(monkeypatch):
    """S'assure qu'on travaille sur une URL prévisible."""
    monkeypatch.setattr(api_service, "API_URL", "http://test-api:8000")


@pytest.mark.api
class TestGetTrajets:
    @patch("services.api_service.requests.get")
    def test_calls_correct_url(self, mock_get):
        mock_get.return_value.json.return_value = []
        api_service.get_trajets()
        mock_get.assert_called_once_with(
            "http://test-api:8000/trajets", timeout=10
        )

    @patch("services.api_service.requests.get")
    def test_returns_json(self, mock_get):
        mock_get.return_value.json.return_value = [
            {"trajet_id": "SNC-1001", "gare_depart": "Paris Nord"}
        ]
        result = api_service.get_trajets()
        assert result == [{"trajet_id": "SNC-1001", "gare_depart": "Paris Nord"}]


@pytest.mark.api
class TestGetTrajetItineraire:
    @patch("services.api_service.requests.get")
    def test_url_encodes_special_chars(self, mock_get):
        """Le slash et l'espace dans 'CFR 78/1743' doivent être URL-encodés."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        api_service.get_trajet_itineraire("CFR 78/1743")

        call_url = mock_get.call_args[0][0]
        # '%20' pour espace et '%2F' pour slash
        assert "CFR%2078%2F1743" in call_url

    @patch("services.api_service.requests.get")
    def test_returns_empty_list_on_404(self, mock_get):
        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response
        assert api_service.get_trajet_itineraire("UNKNOWN") == []

    @patch("services.api_service.requests.get")
    def test_returns_empty_list_on_exception(self, mock_get):
        """Doit échouer silencieusement (le dashboard ne doit pas planter)."""
        mock_get.side_effect = Exception("network error")
        assert api_service.get_trajet_itineraire("ANY") == []


@pytest.mark.api
class TestStatsEndpoints:
    @patch("services.api_service.requests.get")
    def test_get_trajets_count(self, mock_get):
        mock_get.return_value.json.return_value = {"total_trajets": 42}
        assert api_service.get_trajets_count() == {"total_trajets": 42}
        assert mock_get.call_args[0][0] == "http://test-api:8000/stats/trajets/count"

    @patch("services.api_service.requests.get")
    def test_get_emissions(self, mock_get):
        mock_get.return_value.json.return_value = {"train": 4.5, "avion": 185.0}
        result = api_service.get_emissions()
        assert result["train"] == 4.5
        assert result["avion"] == 185.0


@pytest.mark.api
class TestGetOperateurs:
    @patch("services.api_service.requests.get")
    def test_returns_list_when_200(self, mock_get):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = [{"operateur": "SNCF", "trajets": 12}]
        mock_get.return_value = mock_response
        result = api_service.get_operateurs()
        assert result == [{"operateur": "SNCF", "trajets": 12}]

    @patch("services.api_service.requests.get")
    def test_returns_empty_when_non_200(self, mock_get):
        mock_response = MagicMock(status_code=500)
        mock_get.return_value = mock_response
        assert api_service.get_operateurs() == []

    @patch("services.api_service.requests.get")
    def test_returns_empty_on_invalid_json(self, mock_get):
        """Si le JSON est invalide, ne pas planter le dashboard."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.side_effect = ValueError("invalid json")
        mock_get.return_value = mock_response
        assert api_service.get_operateurs() == []


@pytest.mark.api
class TestGetTrajetsMap:
    @patch("services.api_service.requests.get")
    def test_uses_longer_timeout(self, mock_get):
        """Cet endpoint est lourd, on prévoit 15s au lieu de 10."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        api_service.get_trajets_map()
        kwargs = mock_get.call_args.kwargs
        assert kwargs.get("timeout", 10) >= 15

    @patch("services.api_service.requests.get")
    def test_returns_empty_on_500(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)
        assert api_service.get_trajets_map() == []


@pytest.mark.api
class TestPing:
    @patch("services.api_service.requests.get")
    def test_returns_dict_with_ok_and_latency(self, mock_get):
        mock_response = MagicMock(status_code=200)
        mock_get.return_value = mock_response
        result = api_service.ping()
        assert "ok" in result
        assert result["ok"] is True
        assert "latency_ms" in result
        assert isinstance(result["latency_ms"], (int, float))
        assert result["latency_ms"] >= 0

    @patch("services.api_service.requests.get")
    def test_handles_exception(self, mock_get):
        mock_get.side_effect = Exception("connection refused")
        result = api_service.ping()
        assert result["ok"] is False
