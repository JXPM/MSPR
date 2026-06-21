"""Tests de la supervision du modele ML (metriques Prometheus).

Verifie que les endpoints /predict/* alimentent bien les metriques exposees
sur /metrics. Les modeles sont moques (pas besoin des .joblib en CI).
"""

from unittest.mock import patch

import pytest

MOCK_MODELS = {"loaded": True}
MOCK_EMISSION = 12.47
MOCK_CLUSTER = (1, "Potentiel modere")


@pytest.fixture
def ml_mocks():
    with patch.multiple(
        "app.routes.predict_routes",
        _MODELS=MOCK_MODELS,
        _predict_emissions_fn=lambda *args: MOCK_EMISSION,
        _predict_cluster_fn=lambda *args: MOCK_CLUSTER,
    ):
        yield


@pytest.mark.integration
class TestMlMetrics:
    def test_full_prediction_feeds_model_metrics(self, client, ml_mocks):
        """Un /predict/full incremente les compteurs du modele exposes sur /metrics."""
        client.post(
            "/predict/full",
            json={
                "distance_km": 800.0,
                "operateur": "OBB Nightjet",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        metrics = client.get("/metrics").text
        assert "obrail_model_loaded" in metrics
        assert 'obrail_predict_requests_total{endpoint="full",status="success"}' in metrics
        assert "obrail_predict_emission_kg" in metrics
        assert 'obrail_predict_cluster_total{cluster="1"}' in metrics
        assert 'obrail_predict_service_total{type_service="NUIT"}' in metrics

    def test_prediction_error_increments_error_counter(self, client, ml_mocks):
        """Une erreur d'inference incremente le compteur status=error."""
        def boom(*args):
            raise RuntimeError("inference failed")

        with patch("app.routes.predict_routes._predict_emissions_fn", boom):
            response = client.post(
                "/predict/emissions",
                json={
                    "distance_km": 800.0,
                    "operateur": "OBB Nightjet",
                    "type_service": "NUIT",
                    "duree_trajet_min": 480.0,
                },
            )
        assert response.status_code == 500
        metrics = client.get("/metrics").text
        assert 'obrail_predict_requests_total{endpoint="emissions",status="error"}' in metrics
