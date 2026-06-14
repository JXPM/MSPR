"""
train_clustering.py - Entraînement du modèle de clustering ObRail Europe

Ce script industrialise l'entraînement du modèle KMeans retenu
après comparaison de 4 modèles candidats dans le notebook 03_training.ipynb.

Les paramètres ci-dessous ont été déterminés en deux étapes :
- L'analyse exploratoire (EDA) via t-SNE a révélé entre 3 et 4
  groupes naturels dans les données.
- La méthode du coude et le silhouette score (SS) ont confirmé
  k=3 comme nombre optimal de clusters.
- KMeans a été retenu avec un silhouette score (SS) de 0.467,
  meilleur parmi les 4 modèles testés (KMeans, DBSCAN,
  AgglomerativeClustering, GaussianMixture).

Labels métier des clusters :
    Cluster 0 (70 trajets)  : Fort potentiel de substitution avion/train
    Cluster 1 (224 trajets) : Potentiel modéré
    Cluster 2 (103 trajets) : Potentiel limité
"""

import pandas as pd
import numpy as np
import os
import joblib
import warnings
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

warnings.filterwarnings('ignore')

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MODELS_DIR    = os.path.join(BASE_DIR, 'models')


def load_data():
    """Charge le dataset nettoyé depuis data/processed."""
    path = os.path.join(PROCESSED_DIR, 'dataset_cleaned.csv')
    df   = pd.read_csv(path)
    print(f"Dataset chargé : {df.shape[0]} lignes")
    return df


def prepare_features(df):
    """Extrait et normalise les features de clustering."""
    features = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']
    X        = df[features].copy()

    scaler   = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features)

    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler_clustering.joblib'))
    print("Scaler clustering sauvegardé")

    return X_scaled


def train_model(X_scaled):
    """Entraîne KMeans avec k=3."""
    model  = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)

    score  = silhouette_score(X_scaled, labels)
    print(f"Modèle entraîné - Silhouette score (SS) : {score:.3f}")

    return model, labels


def analyser_clusters(df, labels):
    """Affiche le profil moyen de chaque cluster."""
    features          = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']
    df_clust          = df[features].copy()
    df_clust['cluster'] = labels

    profil = df_clust.groupby('cluster')[features].mean().round(2)
    taille = df_clust['cluster'].value_counts().sort_index()

    print("\nProfil moyen par cluster :")
    print(profil)
    print("\nNombre de trajets par cluster :")
    print(taille)


def save_model(model):
    """Sauvegarde le modèle KMeans dans models/."""
    path = os.path.join(MODELS_DIR, 'model_clustering.joblib')
    joblib.dump(model, path)
    print(f"Modèle sauvegardé : {path}")


if __name__ == '__main__':
    df      = load_data()
    X_scaled = prepare_features(df)
    model, labels = train_model(X_scaled)
    analyser_clusters(df, labels)
    save_model(model)
    print("Entraînement clustering terminé")
    