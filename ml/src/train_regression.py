"""
train_regression.py - Entraînement du modèle de régression ObRail Europe

Ce script industrialise l'entraînement du modèle XGBoost retenu
après comparaison de 5 modèles candidats dans le notebook 03_training.ipynb.

Les hyperparamètres ci-dessous ont été déterminés en deux étapes :
- L'analyse exploratoire (EDA) a confirmé que la relation entre
  les features et les émissions CO2 est non linéaire, orientant
  le choix vers des modèles basés sur des arbres de décision.
- Le GridSearchCV avec cross-validation k=5 a ensuite identifié
  la combinaison optimale parmi 54 combinaisons testées :

    n_estimators  = 300  : nombre d'arbres construits
    max_depth     = 5    : profondeur maximale de chaque arbre
    learning_rate = 0.1  : vitesse d'apprentissage
    subsample     = 0.8  : proportion des données utilisées par arbre

Performances obtenues :
    RMSE validation = 1.173 kg CO2
    RMSE test       = 1.419 kg CO2
    R²   test       = 0.959
"""

import pandas as pd
import numpy as np
import os
import joblib
import warnings
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLITS_DIR  = os.path.join(BASE_DIR, 'data', 'splits')
MODELS_DIR  = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')


def load_splits():
    """Charge les splits produits par preprocessing.py."""
    X_train = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv'))
    X_val   = pd.read_csv(os.path.join(SPLITS_DIR, 'X_val.csv'))
    X_test  = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv'))
    y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze()
    y_val   = pd.read_csv(os.path.join(SPLITS_DIR, 'y_val.csv')).squeeze()
    y_test  = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze()

    print(f"Train : {X_train.shape[0]} | Val : {X_val.shape[0]} | Test : {X_test.shape[0]}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_model(X_train, y_train):
    """Entraîne XGBoost avec les hyperparamètres optimisés."""
    model = XGBRegressor(
        n_estimators  = 300,
        max_depth     = 5,
        learning_rate = 0.1,
        subsample     = 0.8,
        random_state  = 42,
        verbosity     = 0
    )
    model.fit(X_train, y_train)
    print("Modèle entraîné")
    return model


def evaluer_modele(model, X, y, nom):
    """Calcule et affiche MAE, RMSE et R² sur un ensemble donné."""
    y_pred = model.predict(X)
    mae    = mean_absolute_error(y, y_pred)
    rmse   = mean_squared_error(y, y_pred) ** 0.5
    r2     = r2_score(y, y_pred)
    print(f"{nom} -> MAE={mae:.3f} RMSE={rmse:.3f} R²={r2:.3f}")
    return {'ensemble': nom, 'MAE': round(mae, 3), 'RMSE': round(rmse, 3), 'R2': round(r2, 3)}


def save_model(model):
    """Sauvegarde le modèle entraîné dans models/."""
    path = os.path.join(MODELS_DIR, 'model_regression.joblib')
    joblib.dump(model, path)
    print(f"Modèle sauvegardé : {path}")


if __name__ == '__main__':
    X_train, X_val, X_test, y_train, y_val, y_test = load_splits()

    model = train_model(X_train, y_train)

    resultats = []
    resultats.append(evaluer_modele(model, X_val,  y_val,  'Validation'))
    resultats.append(evaluer_modele(model, X_test, y_test, 'Test'))

    pd.DataFrame(resultats).to_csv(
        os.path.join(REPORTS_DIR, 'resultats_regression.csv'), index=False
    )
    print("Résultats sauvegardés : reports/resultats_regression.csv")

    save_model(model)
    print("Entraînement terminé")