"""
predict.py - Script de prédiction ObRail Europe

Ce script charge les modèles entraînés et expose deux fonctions :
- predict_emissions : prédit l'empreinte CO2 d'un trajet ferroviaire
  à partir de la distance, de l'opérateur, du type de service et de la durée.
- predict_cluster : identifie le profil de substitution avion/train
  d'un trajet à partir de ses caractéristiques d'émissions.

Ces deux fonctions seront appelées par route_predict.py
pour répondre aux requêtes de l'API FastAPI.
"""

import joblib
import pandas as pd
import numpy as np
import os

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR    = os.path.join(BASE_DIR, 'models')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')


def load_models():
    """Charge les modèles et scalers depuis models/."""
    scaler_regression = joblib.load(os.path.join(MODELS_DIR, 'scaler.joblib'))
    model_regression  = joblib.load(os.path.join(MODELS_DIR, 'model_regression.joblib'))
    scaler_clustering = joblib.load(os.path.join(MODELS_DIR, 'scaler_clustering.joblib'))
    model_clustering  = joblib.load(os.path.join(MODELS_DIR, 'model_clustering.joblib'))
    target_encoding   = pd.read_csv(os.path.join(PROCESSED_DIR, 'target_encoding.csv'))

    # Pre-calcul de la table d'encodage et de la moyenne globale : faits une
    # seule fois au chargement plutot qu'a chaque appel de predict_emissions.
    encoding_map    = target_encoding.set_index('operateur')['target_encoding']
    moyenne_globale = float(encoding_map.mean())

    return {
        'scaler_regression' : scaler_regression,
        'model_regression'  : model_regression,
        'scaler_clustering' : scaler_clustering,
        'model_clustering'  : model_clustering,
        'target_encoding'   : target_encoding,
        'encoding_map'      : encoding_map,
        'moyenne_globale'   : moyenne_globale,
    }


def predict_emissions(distance_km, operateur, type_service, duree_trajet_min, models):
    """Prédit l'empreinte CO2 d'un trajet ferroviaire.

    Args:
        distance_km      : distance du trajet en km
        operateur        : nom de l'opérateur ferroviaire
        type_service     : type de service (JOUR ou NUIT)
        duree_trajet_min : durée du trajet en minutes
        models           : dictionnaire des modèles chargés

    Returns:
        float : empreinte CO2 prédite en kg
    """
    # Reutilise la table pre-calculee si presente (cf. load_models), sinon
    # retombe sur l'ancien comportement pour rester retro-compatible.
    encoding_map    = models.get('encoding_map')
    if encoding_map is None:
        encoding_map = models['target_encoding'].set_index('operateur')['target_encoding']
    moyenne_globale = models.get('moyenne_globale', float(encoding_map.mean()))
    operateur_enc   = encoding_map.get(operateur, moyenne_globale)
    type_enc        = 0 if type_service == 'JOUR' else 1

    X = pd.DataFrame(
        [[distance_km, operateur_enc, type_enc, duree_trajet_min]],
        columns=['distance_km', 'operateur', 'type_service', 'duree_trajet_min']
    )

    X_scaled   = models['scaler_regression'].transform(X)
    prediction = models['model_regression'].predict(X_scaled)[0]

    return round(float(prediction), 2)


def predict_cluster(distance_km, empreinte_train_kg, empreinte_avion_kg, ratio_co2, models):
    """Identifie le profil de substitution avion/train d'un trajet.

    Args:
        distance_km        : distance du trajet en km
        empreinte_train_kg : empreinte CO2 du train en kg
        empreinte_avion_kg : empreinte CO2 de l'avion en kg
        ratio_co2          : ratio empreinte_train / empreinte_avion
        models             : dictionnaire des modèles chargés

    Returns:
        int : numéro du cluster (0, 1 ou 2)
        str : label métier du cluster
    """
    labels = {
        0: 'Fort potentiel de substitution avion/train',
        1: 'Potentiel modéré',
        2: 'Potentiel limité'
    }

    X = pd.DataFrame(
        [[distance_km, empreinte_train_kg, empreinte_avion_kg, ratio_co2]],
        columns=['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']
    )

    X_scaled = models['scaler_clustering'].transform(X.values)
    cluster  = int(models['model_clustering'].predict(
        pd.DataFrame(X_scaled, columns=['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2'])
    )[0])

    return cluster, labels.get(cluster, 'Inconnu')


if __name__ == '__main__':
    models = load_models()

    emission = predict_emissions(
        distance_km      = 891,
        operateur        = 'PKP Intercity S.A.',
        type_service     = 'NUIT',
        duree_trajet_min = 480,
        models           = models
    )
    print(f"Empreinte CO2 prédite : {emission} kg")

    cluster, label = predict_cluster(
        distance_km        = 891,
        empreinte_train_kg = emission,
        empreinte_avion_kg = 891 * 0.158,
        ratio_co2          = emission / (891 * 0.158),
        models             = models
    )
    print(f"Cluster : {cluster} - {label}")
