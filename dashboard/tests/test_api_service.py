from unittest.mock import patch, MagicMock

import pytest

from services import api_service


@pytest.fixture(autouse=True)
def reset_api_url(monkeypatch):
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

    @patch("services.api_service.time.sleep")  # n'attend pas vraiment entre les essais
    @patch("services.api_service.requests.get")
    def test_returns_empty_on_invalid_json(self, mock_get, _sleep):
        # Cold start Render : le backend renvoie une page HTML, pas du JSON.
        mock_response = MagicMock(status_code=200)
        mock_response.json.side_effect = ValueError("Expecting value")
        mock_get.return_value = mock_response
        assert api_service.get_trajets() == []

    @patch("services.api_service.time.sleep")
    @patch("services.api_service.requests.get")
    def test_returns_empty_on_http_error(self, mock_get, _sleep):
        # Backend endormi / redéploiement : 502 -> raise_for_status lève.
        mock_response = MagicMock(status_code=502)
        mock_response.raise_for_status.side_effect = Exception("502 Bad Gateway")
        mock_get.return_value = mock_response
        assert api_service.get_trajets() == []


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
class TestPredictEmissions:
    @patch("services.api_service.requests.post")
    def test_appelle_le_bon_endpoint_avec_payload(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"empreinte_train_kg": 10.0}
        api_service.predict_emissions(450, "SNCF", "JOUR", 130)
        assert mock_post.call_args[0][0] == "http://test-api:8000/predict/emissions"
        payload = mock_post.call_args.kwargs["json"]
        assert payload == {
            "distance_km": 450,
            "operateur": "SNCF",
            "type_service": "JOUR",
            "duree_trajet_min": 130,
        }

    @patch("services.api_service.requests.post")
    def test_retourne_json_sur_200(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"empreinte_train_kg": 10.08}
        assert api_service.predict_emissions(450, "SNCF", "JOUR", 130) == {
            "empreinte_train_kg": 10.08
        }

    @patch("services.api_service.requests.post")
    def test_retourne_dict_vide_sur_non_200(self, mock_post):
        mock_post.return_value = MagicMock(status_code=422)
        assert api_service.predict_emissions(450, "SNCF", "JOUR", 130) == {}

    @patch("services.api_service.requests.post")
    def test_retourne_dict_vide_sur_exception(self, mock_post):
        mock_post.side_effect = Exception("connection refused")
        assert api_service.predict_emissions(450, "SNCF", "JOUR", 130) == {}


@pytest.mark.api
class TestPredictCluster:
    @patch("services.api_service.requests.post")
    def test_appelle_le_bon_endpoint(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"cluster": 1}
        api_service.predict_cluster(450, 10.0, 71.0, 0.14)
        assert mock_post.call_args[0][0] == "http://test-api:8000/predict/cluster"

    @patch("services.api_service.requests.post")
    def test_retourne_dict_vide_sur_exception(self, mock_post):
        mock_post.side_effect = Exception("boom")
        assert api_service.predict_cluster(450, 10.0, 71.0, 0.14) == {}


@pytest.mark.api
class TestPredictFull:
    @patch("services.api_service.requests.post")
    def test_appelle_le_bon_endpoint_avec_payload(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "empreinte_train_kg": 10.08, "cluster": 1, "label": "Potentiel modere"
        }
        api_service.predict_full(450, "SNCF", "JOUR", 130)
        assert mock_post.call_args[0][0] == "http://test-api:8000/predict/full"
        payload = mock_post.call_args.kwargs["json"]
        assert payload["operateur"] == "SNCF"
        assert payload["type_service"] == "JOUR"

    @patch("services.api_service.requests.post")
    def test_retourne_prediction_complete_sur_200(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "empreinte_train_kg": 10.08, "cluster": 1, "label": "Potentiel modere"
        }
        result = api_service.predict_full(450, "SNCF", "JOUR", 130)
        assert result["empreinte_train_kg"] == 10.08
        assert result["cluster"] == 1

    @patch("services.api_service.requests.post")
    def test_retourne_dict_vide_sur_500(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500)
        assert api_service.predict_full(450, "SNCF", "JOUR", 130) == {}

    @patch("services.api_service.requests.post")
    def test_retourne_dict_vide_sur_exception(self, mock_post):
        mock_post.side_effect = Exception("timeout")
        assert api_service.predict_full(450, "SNCF", "JOUR", 130) == {}


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
