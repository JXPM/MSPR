# ObRail Europe - Module Machine Learning

## Presentation du projet

ObRail Europe est un observatoire ferroviaire europeen qui analyse et compare
les emissions de CO2 (dioxyde de carbone) des liaisons ferroviaires nocturnes
en Europe face a l'avion equivalent. Ce module contient le volet ML (Machine
Learning, apprentissage automatique) du projet, developpe dans le cadre du
MSPR (Mission de Synthese Professionnelle en Reseaux) TPRE622 et TPRE642.

## Les trois problematiques du module

**1. Prediction des emissions carbone.**
A partir de la distance d'un trajet en kilometres et de l'operateur ferroviaire
qui l'exploite, peut-on estimer l'empreinte en kg de CO2 ? Cette question est
traitee par un modele de regression supervisee (XGBoost) entraine sur environ
400 trajets de nuit europeens.

**2. Identification des liaisons prioritaires.**
Peut-on regrouper les trajets ferroviaires selon leur profil d'emissions afin
d'identifier ceux qui presentent le plus fort potentiel de substitution avion
vers train ? Cette question est traitee par un algorithme de clustering
(regroupement non supervise) KMeans (K-Means, centroide mobile) en k=3 groupes.

**3. Exposition des predictions via une API (Application Programming Interface).**
Comment rendre ces predictions accessibles au tableau de bord Streamlit sans
exposer le code d'entrainement ? Cette question est traitee par un endpoint
REST (Representational State Transfer) integre dans le backend FastAPI du projet.

## Prerequis

- Python 3.11 ou superieur
- Docker (optionnel, pour lancer le backend complet)
- Les fichiers `.joblib` dans `ml/models/` (generes par `train_regression.py`
  et `train_clustering.py`)

## Installation

```bash
cd ml
python -m venv env
source env/bin/activate       # Linux / macOS
env\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Lancement du pipeline complet

Executer les scripts dans cet ordre depuis le dossier `ml/` :

```bash
# Etape 1 - Nettoyer et decouper les donnees
python src/preprocessing.py

# Etape 2 - Entrainer le modele de regression
python src/train_regression.py

# Etape 3 - Entrainer le modele de clustering
python src/train_clustering.py

# Etape 4 - Tester les predictions
python api/predict.py

# Etape 5 - Lancer les tests unitaires
pytest tests/ -v
```

## Description des scripts

### `src/preprocessing.py`

Prepare les donnees brutes avant l'entrainement :

- `load_data()` : charge `data/raw/dataset_final.csv` (extrait par requete SQL JOIN
  sur les tables `emission`, `trajet`, `ligne`, `operateur` et `exploite`).
- `clean_data()` : supprime les colonnes exclues pour des raisons de
  confidentialite RGPD (Reglement General sur la Protection des Donnees),
  calcule la duree du trajet en minutes, filtre les anomalies (duree < 30 min
  et distance > 1000 km), encode `type_service` en 0/1.
- `split_data()` : decoupe en 70% train, 15% validation, 15% test.
  **Ce decoupage est toujours la premiere operation** pour eviter toute fuite
  d'information (data leakage).
- `encode_operateur()` : applique le Target Encoding (encodage par la cible
  moyenne) sur la colonne `operateur`, calcule uniquement sur le jeu
  d'entrainement. Les operateurs inconnus recevront la moyenne globale.
- `normalize_data()` : applique un StandardScaler (normalisation par ecart-type)
  en le fittant uniquement sur le train.
- `save_splits()` : sauvegarde les 6 CSV de splits dans `data/splits/` et le
  dataset nettoye dans `data/processed/`.

### `src/train_regression.py`

Entraine le modele de regression retenu apres comparaison de 5 candidats :

- `load_splits()` : charge les 6 CSV produits par `preprocessing.py`.
- `train_model()` : entraine un XGBRegressor (XGBoost, eXtreme Gradient
  Boosting) avec les hyperparametres optimises par GridSearchCV :
  `n_estimators=300`, `max_depth=5`, `learning_rate=0.1`, `subsample=0.8`.
- `evaluer_modele()` : calcule MAE (Mean Absolute Error, erreur absolue
  moyenne), RMSE (Root Mean Squared Error, racine de l'erreur quadratique
  moyenne) et R2 (coefficient de determination).
- `save_model()` : sauvegarde le modele dans `models/model_regression.joblib`.

### `src/train_clustering.py`

Entraine le modele de clustering retenu apres comparaison de 4 candidats :

- `prepare_features()` : extrait les 4 variables de clustering
  (`distance_km`, `empreinte_train_kg`, `empreinte_avion_kg`, `ratio_co2`),
  applique un StandardScaler et le sauvegarde dans
  `models/scaler_clustering.joblib`.
- `train_model()` : entraine un KMeans avec `k=3` et `n_init=10`. Le nombre
  de clusters a ete determine par la methode du coude (elbow method) et le
  score de silhouette (silhouette score).
- `analyser_clusters()` : affiche le profil moyen de chaque cluster et
  le nombre de trajets par groupe.
- `save_model()` : sauvegarde le modele dans `models/model_clustering.joblib`.

### `api/predict.py`

Script de prediction autonome utilise par le backend FastAPI :

- `load_models()` : charge les 4 fichiers `.joblib` depuis `models/` et
  la table d'encodage depuis `data/processed/target_encoding.csv`.
- `predict_emissions(distance_km, operateur, type_service, duree_trajet_min, models)`:
  encode l'operateur via Target Encoding, normalise les features, predit
  l'empreinte CO2 en kg avec XGBoost. Retourne un `float` arrondi a 2 decimales.
- `predict_cluster(distance_km, empreinte_train_kg, empreinte_avion_kg, ratio_co2, models)`:
  normalise les features de clustering, predit le cluster KMeans.
  Retourne un tuple `(int, str)` contenant l'identifiant et le label metier.

## Performances des modeles

### Regression - XGBoost

| Metrique | Validation | Test |
|----------|-----------|------|
| RMSE (kg CO2) | 1.173 | 1.419 |
| MAE (kg CO2) | - | 0.758 |
| R2 | - | 0.959 |

Un R2 de 0.959 signifie que le modele explique 95.9% de la variance des
emissions, ce qui est excellent pour un dataset de 400 lignes.

### Clustering - KMeans k=3

| Metrique | Valeur |
|----------|--------|
| Score de silhouette | 0.467 |
| Nombre de clusters | 3 |

Le score de silhouette (entre -1 et 1) mesure la coherence interne des
clusters. 0.467 indique des groupes bien separes.

**Profils des clusters :**

| Cluster | Label | Taille | Caracteristique principale |
|---------|-------|--------|---------------------------|
| 0 | Fort potentiel de substitution | 70 trajets | ratio_co2 tres faible (~0.03) |
| 1 | Potentiel modere | 224 trajets | ratio_co2 intermediaire (~0.14) |
| 2 | Potentiel limite | 103 trajets | distance elevee, ratio variable |

## Fichiers joblib generes

| Fichier | Taille | Description |
|---------|--------|-------------|
| `models/model_regression.joblib` | ~598 KB | XGBoost entraine, predit `empreinte_train_kg` |
| `models/scaler.joblib` | ~1 KB | StandardScaler pour la regression |
| `models/model_clustering.joblib` | ~3 KB | KMeans k=3, assigne un cluster |
| `models/scaler_clustering.joblib` | ~1 KB | StandardScaler pour le clustering |

Ces fichiers sont charges via `joblib.load()` dans `api/predict.py`. Ils ne
sont pas commites dans Git (voir `.gitignore`) car leur taille et leur
dependance a une version precise de scikit-learn les rendent difficiles a
versionner proprement.

## Limitations connues

- **Taille du dataset** : environ 400 trajets, ce qui est peu pour generaliser.
- **100% trains de nuit** : le modele n'est pas applicable aux trains de jour.
- **Biais operateur** : l'operateur UZ represente environ 28% du dataset.
- **Variables absentes** : type de traction, vitesse, nombre d'arrets - ces
  variables amelioreraient la precision mais ne sont pas disponibles.

## Structure des dossiers

```
ml/
├── api/
│   ├── predict.py           - Script de prediction (charge les joblib)
│   └── route_predict.py     - Router FastAPI /predict (integration backend)
├── data/
│   ├── raw/
│   │   └── dataset_final.csv       - Donnees brutes (ne jamais modifier)
│   ├── processed/
│   │   ├── dataset_cleaned.csv     - Apres nettoyage
│   │   └── target_encoding.csv     - Mapping operateur -> valeur encodee
│   └── splits/
│       ├── X_train.csv / X_val.csv / X_test.csv
│       └── y_train.csv / y_val.csv / y_test.csv
├── models/
│   ├── model_regression.joblib     - XGBoost (regression)
│   ├── scaler.joblib               - StandardScaler (regression)
│   ├── model_clustering.joblib     - KMeans (clustering)
│   └── scaler_clustering.joblib    - StandardScaler (clustering)
├── notebooks/
│   ├── 01_eda.ipynb               - Analyse exploratoire des donnees
│   ├── 02_preprocessing.ipynb     - Visualisation des transformations
│   └── 03_training.ipynb          - Entrainement et comparaison des modeles
├── reports/
│   ├── figures/                   - Graphiques (PNG)
│   ├── resultats_regression.csv   - MAE, RMSE, R2 par ensemble
│   └── tableau_comparatif.csv     - Comparaison des 5 modeles candidats
├── src/
│   ├── preprocessing.py           - Nettoyage, split, encodage
│   ├── train_regression.py        - Entrainement XGBoost
│   └── train_clustering.py        - Entrainement KMeans
├── tests/
│   ├── test_predict.py            - Tests unitaires des fonctions de prediction
│   └── test_clustering.py         - Tests unitaires du clustering
└── requirements.txt               - Dependances Python avec versions figees
```

## Auteurs

- Joseph Haccandy (EDA, regression, suivi GitHub Projects)
- Kouame Johan Bile (clustering, structure du projet, README)
- Glody Kutumbakana (joblib, api/predict.py, route_predict.py, CI)
- Nabil Dia (rapport technique, benchmark cloud, veille, accessibilite)
