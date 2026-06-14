"""Tests des routes /predict/* du backend ObRail Europe.

Les modeles ML (joblib) sont moques pour que les tests s'executent
sans avoir besoin des fichiers .joblib dans l'environnement de CI.
"""

from unittest.mock import patch

import pytest


MOCK_MODELS = {"loaded": True}
MOCK_EMISSION = 12.47
MOCK_CLUSTER = (1, "Potentiel modere")


@pytest.fixture
def ml_mocks():
    """Patche les fonctions ML et le dictionnaire de modeles.

    Remplace les references globales du module predict_routes par des
    valeurs de test deterministiques.
    """
    with patch.multiple(
        "app.routes.predict_routes",
        _MODELS=MOCK_MODELS,
        _predict_emissions_fn=lambda *args: MOCK_EMISSION,
        _predict_cluster_fn=lambda *args: MOCK_CLUSTER,
    ):
        yield


@pytest.mark.integration
class TestPredictEmissions:
    def test_predict_emissions_returns_200(self, client, ml_mocks):
        """Un appel valide renvoie 200 avec l'empreinte predite."""
        response = client.post(
            "/predict/emissions",
            json={
                "distance_km": 800.0,
                "operateur": "OBB Nightjet",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        assert response.status_code == 200

    def test_predict_emissions_response_fields(self, client, ml_mocks):
        """La reponse contient tous les champs attendus."""
        response = client.post(
            "/predict/emissions",
            json={
                "distance_km": 800.0,
                "operateur": "OBB Nightjet",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        data = response.json()
        assert "empreinte_train_kg" in data
        assert "unite" in data
        assert data["unite"] == "kg CO2"
        assert data["empreinte_train_kg"] == MOCK_EMISSION

    def test_predict_emissions_invalid_type_service_returns_422(self, client, ml_mocks):
        """Un type_service invalide renvoie une erreur de validation 422."""
        response = client.post(
            "/predict/emissions",
            json={
                "distance_km": 800.0,
                "operateur": "OBB Nightjet",
                "type_service": "AVION",
                "duree_trajet_min": 480.0,
            },
        )
        assert response.status_code == 422

    def test_predict_emissions_negative_distance_returns_422(self, client, ml_mocks):
        """Une distance negative renvoie une erreur de validation 422."""
        response = client.post(
            "/predict/emissions",
            json={
                "distance_km": -100.0,
                "operateur": "OBB Nightjet",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        assert response.status_code == 422

    def test_predict_emissions_zero_distance_returns_422(self, client, ml_mocks):
        """Une distance de 0 (valeur limite gt=0) renvoie 422."""
        response = client.post(
            "/predict/emissions",
            json={
                "distance_km": 0.0,
                "operateur": "OBB Nightjet",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestPredictCluster:
    def test_predict_cluster_returns_200(self, client, ml_mocks):
        """Un appel valide renvoie 200 avec le cluster identifie."""
        response = client.post(
            "/predict/cluster",
            json={
                "distance_km": 800.0,
                "empreinte_train_kg": 12.5,
                "empreinte_avion_kg": 126.4,
                "ratio_co2": 0.099,
            },
        )
        assert response.status_code == 200

    def test_predict_cluster_label_valid(self, client, ml_mocks):
        """Le label renvoye correspond au mock et est non vide."""
        response = client.post(
            "/predict/cluster",
            json={
                "distance_km": 800.0,
                "empreinte_train_kg": 12.5,
                "empreinte_avion_kg": 126.4,
                "ratio_co2": 0.099,
            },
        )
        data = response.json()
        assert data["cluster"] == MOCK_CLUSTER[0]
        assert data["label"] == MOCK_CLUSTER[1]
        assert isinstance(data["description"], str)
        assert len(data["description"]) > 0

    def test_predict_cluster_negative_distance_returns_422(self, client, ml_mocks):
        """Une distance negative renvoie 422."""
        response = client.post(
            "/predict/cluster",
            json={
                "distance_km": -50.0,
                "empreinte_train_kg": 12.5,
                "empreinte_avion_kg": 126.4,
                "ratio_co2": 0.099,
            },
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestPredictFull:
    def test_predict_full_returns_200(self, client, ml_mocks):
        """Un appel valide renvoie 200."""
        response = client.post(
            "/predict/full",
            json={
                "distance_km": 891.0,
                "operateur": "PKP Intercity S.A.",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        assert response.status_code == 200

    def test_predict_full_contains_both_results(self, client, ml_mocks):
        """La reponse contient les champs de regression et de clustering."""
        response = client.post(
            "/predict/full",
            json={
                "distance_km": 891.0,
                "operateur": "PKP Intercity S.A.",
                "type_service": "NUIT",
                "duree_trajet_min": 480.0,
            },
        )
        data = response.json()
        assert "empreinte_train_kg" in data
        assert "cluster" in data
        assert "label" in data
        assert "description" in data
        assert data["empreinte_train_kg"] == MOCK_EMISSION
        assert data["cluster"] == MOCK_CLUSTER[0]

    def test_predict_full_type_jour_accepted(self, client, ml_mocks):
        """Le type_service JOUR est accepte comme valeur valide."""
        response = client.post(
            "/predict/full",
            json={
                "distance_km": 500.0,
                "operateur": "SNCF",
                "type_service": "JOUR",
                "duree_trajet_min": 200.0,
            },
        )
        assert response.status_code == 200

    def test_predict_full_models_unavailable_returns_500(self, client):
        """Sans modeles charges, l'endpoint renvoie 500."""
        with patch("app.routes.predict_routes._MODELS", new=None):
            response = client.post(
                "/predict/full",
                json={
                    "distance_km": 800.0,
                    "operateur": "OBB",
                    "type_service": "NUIT",
                    "duree_trajet_min": 480.0,
                },
            )
        assert response.status_code == 500
