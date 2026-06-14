"""
test_clustering.py - Tests unitaires pour le modèle de clustering ObRail Europe

Ce script vérifie que le modèle KMeans retourne des résultats
cohérents et dans les plages attendues.
"""

import sys
import os
import pytest
import joblib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR    = os.path.join(BASE_DIR, 'models')

model_clustering  = joblib.load(os.path.join(MODELS_DIR, 'model_clustering.joblib'))
scaler_clustering = joblib.load(os.path.join(MODELS_DIR, 'scaler_clustering.joblib'))


def predire_cluster(distance_km, empreinte_train_kg, empreinte_avion_kg, ratio_co2):
    """Prédit le cluster d'un trajet."""
    X = pd.DataFrame(
        [[distance_km, empreinte_train_kg, empreinte_avion_kg, ratio_co2]],
        columns=['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']
    )
    X_scaled = scaler_clustering.transform(X.values)
    cluster  = int(model_clustering.predict(
        pd.DataFrame(X_scaled, columns=['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2'])
    )[0])
    return cluster


def test_cluster_valeur_valide():
    """Le cluster prédit doit être 0, 1 ou 2."""
    cluster = predire_cluster(820, 3.23, 129.56, 0.03)
    assert cluster in [0, 1, 2]


def test_cluster_fort_potentiel():
    """Un trajet avec ratio_co2 très faible doit être dans le cluster 0."""
    cluster = predire_cluster(820, 3.23, 129.56, 0.03)
    assert cluster == 0


def test_cluster_potentiel_modere():
    """Un trajet moyen doit être dans le cluster 1."""
    cluster = predire_cluster(673, 15.15, 106.29, 0.14)
    assert cluster == 1


def test_cluster_potentiel_limite():
    """Un trajet long avec forte empreinte doit être dans le cluster 2."""
    cluster = predire_cluster(1202, 21.09, 189.88, 0.11)
    assert cluster == 2


def test_cluster_retourne_entier():
    """Le cluster prédit doit être un entier."""
    cluster = predire_cluster(700, 15.0, 110.6, 0.14)
    assert isinstance(cluster, int)


def test_cluster_stable():
    """Le même trajet doit toujours retourner le même cluster."""
    cluster1 = predire_cluster(820, 3.23, 129.56, 0.03)
    cluster2 = predire_cluster(820, 3.23, 129.56, 0.03)
    assert cluster1 == cluster2