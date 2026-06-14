import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.predict import load_models, predict_emissions, predict_cluster

models = load_models()


def test_predict_emissions_valeur_positive():
    emission = predict_emissions(
        distance_km=500, operateur='SNCF Voyageurs SA',
        type_service='JOUR', duree_trajet_min=180, models=models
    )
    assert emission > 0


def test_predict_emissions_plage_realiste():
    emission = predict_emissions(
        distance_km=800, operateur='PKP Intercity S.A.',
        type_service='NUIT', duree_trajet_min=480, models=models
    )
    assert 0 < emission < 35


def test_predict_emissions_operateur_inconnu():
    emission = predict_emissions(
        distance_km=600, operateur='Operateur Inconnu',
        type_service='JOUR', duree_trajet_min=240, models=models
    )
    assert emission > 0


def test_predict_cluster_valeur_valide():
    cluster, label = predict_cluster(
        distance_km=820, empreinte_train_kg=3.23,
        empreinte_avion_kg=129.56, ratio_co2=0.03, models=models
    )
    assert cluster in [0, 1, 2]


def test_predict_cluster_label_non_vide():
    cluster, label = predict_cluster(
        distance_km=673, empreinte_train_kg=15.15,
        empreinte_avion_kg=106.34, ratio_co2=0.14, models=models
    )
    assert label != ''
    assert label != 'Inconnu'


def test_predict_emissions_type_service_jour():
    emission_jour = predict_emissions(
        distance_km=700, operateur='Trenitalia S.p.A',
        type_service='JOUR', duree_trajet_min=300, models=models
    )
    emission_nuit = predict_emissions(
        distance_km=700, operateur='Trenitalia S.p.A',
        type_service='NUIT', duree_trajet_min=300, models=models
    )
    assert emission_jour != emission_nuit