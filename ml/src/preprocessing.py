import pandas as pd
import numpy as np
import os
import joblib
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR       = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
SPLITS_DIR    = os.path.join(BASE_DIR, 'data', 'splits')
MODELS_DIR    = os.path.join(BASE_DIR, 'models')

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(SPLITS_DIR,    exist_ok=True)
os.makedirs(MODELS_DIR,    exist_ok=True)


def load_data():
    """Charge le dataset brut depuis data/raw."""
    path = os.path.join(RAW_DIR, 'dataset_final.csv')
    df = pd.read_csv(path)
    print(f"Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


def clean_data(df):
    """Supprime les colonnes inutiles, calcule la durée du trajet,
    supprime les anomalies et encode type_service."""

    df = df.drop(columns=['trajet_id', 'gare_depart', 'gare_arrivee', 'pays_operateur'])

    df['heure_depart']  = pd.to_datetime(df['heure_depart'])
    df['heure_arrivee'] = pd.to_datetime(df['heure_arrivee'])

    df['duree_trajet_min'] = (
        df['heure_arrivee'] - df['heure_depart']
    ).dt.total_seconds() / 60

    df['duree_trajet_min'] = df['duree_trajet_min'].apply(
        lambda x: x + 1440 if x < 0 else x
    )

    # Imputation des valeurs manquantes par la médiane
    df['duree_trajet_min'] = df['duree_trajet_min'].fillna(df['duree_trajet_min'].median())

    avant = df.shape[0]
    df = df[
        ~((df['duree_trajet_min'] < 30) & (df['distance_km'] > 1000))
    ].reset_index(drop=True)
    print(f"Anomalies supprimées : {avant - df.shape[0]} lignes")

    df = df.drop(columns=['heure_depart', 'heure_arrivee'])
    df['type_service'] = df['type_service'].map({'JOUR': 0, 'NUIT': 1})

    print(f"Dataset nettoyé : {df.shape[0]} lignes")
    return df


def split_data(df):
    """Découpe le dataset en train/val/test (70/15/15)."""

    features = ['distance_km', 'operateur', 'type_service', 'duree_trajet_min']
    cible    = 'empreinte_train_kg'

    X = df[features]
    y = df[cible]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42
    )

    print(f"Train : {X_train.shape[0]} | Val : {X_val.shape[0]} | Test : {X_test.shape[0]}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def encode_operateur(X_train, X_val, X_test, y_train):
    """Applique le Target Encoding sur operateur
    en se basant uniquement sur les données d'entraînement."""

    temp = X_train.copy()
    temp['empreinte_train_kg'] = y_train.values
    encoding_map = temp.groupby('operateur')['empreinte_train_kg'].mean()

    moyenne_globale = y_train.mean()

    for X in [X_train, X_val, X_test]:
        X['operateur'] = X['operateur'].map(encoding_map).fillna(moyenne_globale)

    encoding_map.reset_index().rename(
        columns={'empreinte_train_kg': 'target_encoding'}
    ).to_csv(os.path.join(PROCESSED_DIR, 'target_encoding.csv'), index=False)

    print("Target Encoding appliqué et sauvegardé")
    return X_train, X_val, X_test


def normalize_data(X_train, X_val, X_test, features):
    """Applique StandardScaler fitté sur le train uniquement."""

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=features)
    X_val_scaled   = pd.DataFrame(scaler.transform(X_val),       columns=features)
    X_test_scaled  = pd.DataFrame(scaler.transform(X_test),      columns=features)

    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.joblib'))
    print("Scaler sauvegardé")
    return X_train_scaled, X_val_scaled, X_test_scaled


def save_splits(X_train, X_val, X_test, y_train, y_val, y_test, df):
    """Sauvegarde tous les fichiers dans data/splits et data/processed."""

    X_train.to_csv(os.path.join(SPLITS_DIR, 'X_train.csv'), index=False)
    X_val.to_csv(os.path.join(SPLITS_DIR,   'X_val.csv'),   index=False)
    X_test.to_csv(os.path.join(SPLITS_DIR,  'X_test.csv'),  index=False)

    y_train.to_csv(os.path.join(SPLITS_DIR, 'y_train.csv'), index=False)
    y_val.to_csv(os.path.join(SPLITS_DIR,   'y_val.csv'),   index=False)
    y_test.to_csv(os.path.join(SPLITS_DIR,  'y_test.csv'),  index=False)

    df.to_csv(os.path.join(PROCESSED_DIR, 'dataset_cleaned.csv'), index=False)
    print("Tous les fichiers sauvegardés")


if __name__ == '__main__':
    features = ['distance_km', 'operateur', 'type_service', 'duree_trajet_min']

    df                                              = load_data()
    df                                              = clean_data(df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df)
    X_train, X_val, X_test                         = encode_operateur(X_train, X_val, X_test, y_train)
    X_train, X_val, X_test                         = normalize_data(X_train, X_val, X_test, features)
    save_splits(X_train, X_val, X_test, y_train, y_val, y_test, df)

    print("Preprocessing terminé")