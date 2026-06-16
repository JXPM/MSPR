# CLAUDE.md — ObRail Europe · MSPR TPRE622 + TPRE642

Ce fichier décrit l'état exact du projet et ce qu'il reste à construire.
Lis-le entièrement avant d'écrire la moindre ligne de code.

---

## Contexte du projet

**ObRail Europe** est un observatoire ferroviaire européen.
Ce dépôt contient deux phases de travail :

| Phase | Code | Statut |
|---|---|---|
| MSPR1 — Infrastructure data | TPRE532 | **TERMINÉ — ne pas modifier** |
| MSPR2 — Machine Learning | TPRE622 + TPRE642 | **À construire** |

---

## Ce qui EST DÉJÀ FAIT (TPRE532 — ne pas toucher)

### Backend FastAPI — `backend/`
- API REST Python 3.12 + FastAPI + SQLAlchemy ORM
- Base URL : `http://localhost:8000` — Swagger : `/docs` — Métriques : `/metrics`
- Endpoints existants : `/health`, `/trajets`, `/trajets/{id}`, `/gares`, `/lignes`, `/stats/*`
- Rate limiting 60 req/min par IP sur `/trajets` et `/stats/*`
- Headers sécurité : X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- CORS : origines `localhost:5173`, `localhost:4173`, `localhost:8501` (configurable via `CORS_ORIGINS` dans `.env`)
- 91 tests pytest dans `backend/tests/`
- **Point d'intégration MSPR2** : ajouter `api/route_predict.py` comme nouveau router dans `backend/app/main.py`

### Dashboard Streamlit — `dashboard/`
- 3 pages : Trajets, Observatoire, Supervision
- Conformité RGAA : contraste 5.2:1, skip link, navigation clavier
- 31 tests unitaires + tests E2E Playwright dans `dashboard/tests_e2e/`

### ETL Talend — `talend/`
- 9 jobs compilés JDBC → PostgreSQL
- Dump final de la base : `talend/dump/mspr2_dump_2026-04-22.sql`

### Monitoring — `monitoring/`
- Prometheus (port 9090) + Grafana (port 3010, login admin/admin)
- Dashboard 6 panels : req/s, erreurs 4xx/5xx, latence p50/p95/p99, req en cours, total, backend UP/DOWN

### Base de données PostgreSQL
- Port Docker : 5433 — BDD : `mspr2` — User : `postgres`
- Initialisée depuis `talend/dump/dump_mspr2.sql` au démarrage Docker
- Schema principal (tables pertinentes pour le ML) :

```
emission  (id_emission, empreinte_train_kg NUMERIC, empreinte_avion_kg NUMERIC, distance_km NUMERIC, trajet_id FK)
trajet    (trajet_id VARCHAR PK, gare_depart, gare_arrivee, heure_depart, heure_arrivee, id_ligne FK)
ligne     (id_ligne INT PK, nom_ligne, distance, type_service)
operateur (code_operateur VARCHAR PK, nom_operateur, iso_pays)
exploite  (code_operateur FK, id_ligne FK, rang)  ← table d'association opérateur ↔ ligne
```

**Données disponibles dans le dump :**
- ~310 trajets de nuit (100% NUIT — aucun trajet de jour dans le dataset)
- 25 opérateurs (ex. ATC, BDŽ, ČD, CFM, CFR, CS, ES, FS, GA, GWR, HŽPP, MÁV, MT, ÖBB, OTE, PKP, RDC, RJ…)
- Exemple de ligne emission : `id=1861 | train=14.0 kg | avion=95.432 kg | distance=604 km | trajet=ATC IR 11501`

### Infrastructure Docker — `docker-compose.yml`
5 services : `postgres` (5433), `backend` (8000), `frontend` (8501), `prometheus` (9090), `grafana` (3010)

### Variables d'environnement — `.env.example`
```
POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD
DATABASE_URL=postgresql://user:pass@localhost/mspr2
CORS_ORIGINS=
API_URL=http://localhost:8000
GRAFANA_USER / GRAFANA_PASSWORD
```

---

## Ce qui RESTE À CONSTRUIRE (TPRE622 + TPRE642)

Tout le volet Machine Learning. Créer un dossier `ml/` à la racine du projet.

### Structure de fichiers à créer

```
ml/
├── notebooks/
│   ├── 01_eda.ipynb              ← EDA pur — AUCUN fit(), AUCUN split, AUCUNE transformation
│   └── 02_preprocessing.ipynb   ← Visualise et valide les transformations appliquées
│
├── src/
│   ├── preprocessing.py          ← Fonctions : clean_data(), encode_operator(), split_data()
│   ├── train_regression.py       ← 4 pipelines + GridSearchCV + courbes apprentissage + SHAP
│   ├── train_clustering.py       ← KMeans k=2..8, coude, silhouette, PCA 2D, t-SNE
│   └── utils.py                  ← Fonctions partagées : plot_learning_curves(), compute_metrics(), plot_shap()
│
├── api/
│   ├── predict.py                ← Script autonome (charge le joblib, prédit sans FastAPI)
│   └── route_predict.py          ← Router FastAPI /predict à inclure dans backend/app/main.py
│
├── data/
│   ├── raw/
│   │   └── dataset_final.csv     ← Extrait du dump SQL — NE JAMAIS MODIFIER
│   ├── processed/                ← Données après nettoyage et encodage
│   └── splits/
│       ├── X_train.csv
│       ├── X_val.csv
│       ├── X_test.csv
│       ├── y_train.csv
│       ├── y_val.csv
│       └── y_test.csv
│
├── models/
│   └── model_final.joblib        ← Pipeline sklearn complet — dans .gitignore
│
├── reports/
│   ├── figures/                  ← Tous les graphiques générés (PNG, dpi=150)
│   └── tableau_comparatif.csv    ← MAE / RMSE / R² des 4 modèles
│
├── tests/
│   └── test_predict.py           ← pytest : vérifie que predict.py retourne un float valide
│
├── requirements.txt              ← Versions EXACTES (ex: scikit-learn==1.4.2)
└── README.md                     ← Comment lancer le projet ML de A à Z
```

---

## Dataset `data/raw/dataset_final.csv`

### Comment le générer

Extraire depuis le dump SQL `talend/dump/mspr2_dump_2026-04-22.sql` avec la requête JOIN suivante :

```sql
SELECT
    e.distance_km,
    e.empreinte_train_kg,
    e.empreinte_avion_kg,
    ROUND(e.empreinte_train_kg / NULLIF(e.empreinte_avion_kg, 0), 4) AS ratio_co2,
    o.nom_operateur                                                    AS operateur,
    t.trajet_id,
    t.gare_depart,
    t.gare_arrivee,
    l.type_service
FROM emission e
JOIN trajet   t ON e.trajet_id     = t.trajet_id
JOIN ligne    l ON t.id_ligne      = l.id_ligne
JOIN exploite x ON l.id_ligne      = x.id_ligne
JOIN operateur o ON x.code_operateur = o.code_operateur
WHERE e.distance_km IS NOT NULL
  AND e.empreinte_train_kg IS NOT NULL;
```

### Colonnes du dataset

| Colonne | Type | Usage |
|---|---|---|
| `distance_km` | float | Feature — régression + clustering |
| `empreinte_train_kg` | float | **Cible régression** |
| `empreinte_avion_kg` | float | Feature — clustering seulement |
| `ratio_co2` | float | Feature — clustering seulement |
| `operateur` | str | Feature — régression + clustering (à encoder) |
| `trajet_id` | str | **Exclure** — identifiant sans valeur prédictive (RGPD Art. 5.1.c) |
| `gare_depart` | str | **Exclure** — trop de modalités + identification possible (RGPD) |
| `gare_arrivee` | str | **Exclure** — idem |
| `type_service` | str | **Exclure** — 100% NUIT, variance nulle, n'apporte rien au modèle |

---

## Règles techniques ABSOLUES

```
random_state=42         — partout sans exception : splits, KMeans, RandomForest, XGBoost
Split AVANT tout        — train_test_split() est la PREMIÈRE opération de preprocessing
Fit sur train only      — StandardScaler.fit() et TargetEncoder.fit() uniquement sur X_train
Pas de fit() dans EDA   — 01_eda.ipynb ne contient aucun fit(), transform(), ou split
data leakage interdit   — ne jamais calculer des stats sur le test set avant de l'utiliser
```

---

## Phase 2 — EDA (`notebooks/01_eda.ipynb`)

Observations pures uniquement. Produit des constats écrits, pas des transformations.

**Étapes obligatoires :**
1. Chargement + vue d'ensemble : `df.shape`, `df.dtypes`, `df.head(10)`, `df.describe()`
2. Valeurs manquantes : `df.isnull().sum()` + visualisation `missingno`
3. Distributions : histogrammes des 4 variables numériques + skewness
4. Outliers : méthode IQR sur chaque colonne numérique + boxplots
5. Corrélations : matrice de Pearson + heatmap seaborn
6. VIF (Variance Inflation Factor) : détecter la multicolinéarité (seuil < 5)
7. Biais opérateur : compter les occurrences par opérateur (UZ représente ~28%)
8. PCA 2D : `PCA(n_components=2)` — visualisation de la structure globale
9. t-SNE 2D : `TSNE(n_components=2, random_state=42, perplexity=30)` — clusters non linéaires

**Figures à sauvegarder dans `reports/figures/` :**
`distributions.png`, `boxplots.png`, `correlation_heatmap.png`, `vif_bar.png`, `pca_2d.png`, `tsne_2d.png`

---

## Phase 3 — Preprocessing (`src/preprocessing.py`)

```python
def split_data(df):
    # PREMIER — avant toute transformation
    # 70% train / 15% val / 15% test — random_state=42
    ...

def encode_operator(X_train, X_val, X_test):
    # Target encoding calculé UNIQUEMENT sur X_train
    # Jamais de fit sur val ou test
    ...

def clean_data(df):
    # Imputation médiane sur les valeurs manquantes (médiane calculée sur train)
    # Suppression des colonnes exclues : trajet_id, gare_depart, gare_arrivee, type_service
    ...
```

Splits à sauvegarder dans `data/splits/` après le preprocessing.

---

## Phase 4 — Régression (`src/train_regression.py`)

**4 modèles candidats avec Pipeline sklearn :**

| Modèle | Justification | Risque |
|---|---|---|
| `LinearRegression` | Baseline — teste si la relation est linéaire | Underfitting si relation non linéaire |
| `Ridge(alpha=1.0)` | Régularisation L2 — réduit l'overfitting vs Linear | Peu d'amélioration si pas de multicolinéarité |
| `RandomForestRegressor(n_estimators=200, random_state=42)` | Capture les non-linéarités, robuste aux outliers | Lent à entraîner |
| `XGBRegressor(n_estimators=200, random_state=42, verbosity=0)` | Meilleur en général sur données tabulaires | Overfitting probable sur 310 lignes |

**Chaque pipeline :** `[('scaler', StandardScaler()), ('model', ...)]`

**GridSearchCV obligatoire** sur Ridge et RandomForest :
- Ridge : `{'model__alpha': [0.01, 0.1, 1, 10, 100, 1000]}`
- RandomForest : `{'model__n_estimators': [100, 200, 500], 'model__max_depth': [3, 5, 10]}`

**Métriques à calculer** pour chaque modèle sur val set + cross-validation 5-fold :
- MAE, RMSE, R² (val set)
- R² mean ± std (CV 5-fold sur train set)

**Sauvegarder** dans `reports/tableau_comparatif.csv`.

**SHAP** sur le modèle final sélectionné :
- `shap.Explainer` + `shap.summary_plot()` → `reports/figures/shap_summary.png`

**Sauvegarder le meilleur pipeline :**
```python
import joblib
joblib.dump(best_pipeline, 'models/model_final.joblib')
```

---

## Phase 4 — Clustering (`src/train_clustering.py`)

**KMeans de k=2 à k=8** avec `random_state=42` :
- Méthode du coude : inertie en fonction de k → `reports/figures/elbow_curve.png`
- Silhouette score pour chaque k → choisir le k optimal (convergence des deux critères)
- PCA 2D des clusters → `reports/figures/kmeans_pca_clusters.png`
- t-SNE 2D des clusters → `reports/figures/kmeans_tsne_clusters.png`

**Variables pour le clustering :** `distance_km`, `empreinte_train_kg`, `empreinte_avion_kg`, `ratio_co2`
(pas `operateur` — pas de target encoding ici)

**Interpréter chaque cluster en termes métier ObRail** dans un bloc Markdown :
- ex. Cluster 0 : "Liaisons courtes < 500 km, faibles émissions, fort potentiel local"

---

## Phase 6 — Déploiement

### `api/predict.py` — Script autonome
```python
import joblib, pandas as pd

def predict(distance_km: float, operateur: str) -> float:
    pipeline = joblib.load('models/model_final.joblib')
    X = pd.DataFrame([{'distance_km': distance_km, 'operateur': operateur}])
    return float(pipeline.predict(X)[0])

if __name__ == '__main__':
    print(predict(850, 'ÖBB'))
```

### `api/route_predict.py` — Router FastAPI
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/predict", tags=["ML"])

class PredictRequest(BaseModel):
    distance_km: float
    operateur: str

class PredictResponse(BaseModel):
    empreinte_train_kg: float

@router.post("/", response_model=PredictResponse)
def predict_co2(request: PredictRequest):
    ...
```

**Intégration dans `backend/app/main.py` :**
Ajouter `from api.route_predict import router as predict_router` et `app.include_router(predict_router)`.

### `tests/test_predict.py`
```python
def test_predict_returns_float():
    result = predict(850, 'ÖBB')
    assert isinstance(result, float)
    assert result > 0

def test_predict_scales_with_distance():
    assert predict(1500, 'ÖBB') > predict(500, 'ÖBB')
```

---

## `requirements.txt` (versions exactes)

```
scikit-learn==1.4.2
xgboost==2.0.3
pandas==2.2.1
numpy==1.26.4
matplotlib==3.8.3
seaborn==0.13.2
shap==0.44.1
joblib==1.3.2
jupyter==1.0.0
missingno==0.5.2
scipy==1.13.0
```

---

## `.gitignore` additions pour le ML

```
models/*.joblib
data/raw/*.csv
data/splits/*.csv
data/processed/*.csv
__pycache__/
.ipynb_checkpoints/
```

---

## Livrables et responsables

| # | Livrable | Responsable | Bloc |
|---|---|---|---|
| 1 | `notebooks/01_eda.ipynb` + `data/raw/dataset_final.csv` | Joseph Haccandy | TPRE622 |
| 2 | `requirements.txt` + `README.md` + structure complète | Glody Kutumbakana | TPRE622 |
| 3 | `src/train_regression.py` + `reports/tableau_comparatif.csv` | Joseph Haccandy | TPRE622 |
| 4 | `src/train_clustering.py` + figures clusters + silhouette | Kouamé Johan Bilé | TPRE622 |
| 5 | Rapport évaluation + toutes les figures + SHAP | Toute l'équipe | TPRE622 |
| 6 | Benchmark AWS / GCP / Azure / HuggingFace (tableau) | Nabil Dia | TPRE622+642 |
| 7 | `models/model_final.joblib` + `api/predict.py` | Glody Kutumbakana | TPRE622 |
| 8 | `api/route_predict.py` + `tests/test_predict.py` + CI | Glody Kutumbakana | TPRE622 |
| 9 | Rapport technique complet + section veille (2+ pages) | Nabil Dia | TPRE622+642 |
| 10 | Support soutenance 15 slides | Toute l'équipe | TPRE622+642 |
| 11 | GitHub Projects kanban actif et à jour | Joseph Haccandy | TPRE642 |
| 12 | Section accessibilité / 6 familles de handicap | Nabil Dia | TPRE642 |

---

## Checklist avant soutenance

- [ ] `01_eda.ipynb` tourne de A à Z sans erreur et sans aucun `fit()`
- [ ] `train_regression.py` et `train_clustering.py` tournent sans intervention
- [ ] `model_final.joblib` est généré et chargé correctement par `predict.py`
- [ ] L'endpoint `/predict` répond (tester : `curl -X POST http://localhost:8000/predict -d '{"distance_km":850,"operateur":"ÖBB"}'`)
- [ ] GitHub Projects kanban à jour (toutes les tâches terminées en **Done** avec PR associée)
- [ ] Rapport contient : EDA, minimisation RGPD, PCA + t-SNE, multi-modèles justifiés, métriques commentées, SHAP, benchmark cloud, veille technique, accessibilité/handicap, limites
- [ ] Chaque membre peut expliquer n'importe quel concept du guide sans regarder ses notes

---

## Questions jury garanties (réponses à connaître)

**Régression vs classification ?**
Régression = nombre continu (17.3 kg CO₂). Classification = catégorie (JOUR/NUIT). KMeans produit des catégories mais n'est pas de la classification car pas de cible connue.

**Pourquoi 4 modèles et pas juste XGBoost ?**
On ne sait pas a priori quel modèle sera optimal. LinearRegression est la baseline. Si elle performe aussi bien, la relation est linéaire et un modèle simple suffit. C'est la démarche scientifique.

**Comment avez-vous choisi k pour KMeans ?**
Deux critères indépendants : méthode du coude (inertie) + silhouette score. Le k optimal est là où les deux convergent.

**Pourquoi exclure gare_depart et trajet_id ?**
RGPD Art. 5.1.c — minimisation des données. `trajet_id` est un identifiant sans valeur prédictive. `gare_depart` a trop de modalités et permettrait d'identifier des trajets spécifiques.

**Pourquoi un modèle maison plutôt qu'AWS SageMaker ?**
RGPD (données restent en infrastructure locale), coût zéro, interprétabilité SHAP, 310 lignes ne nécessitent pas la puissance cloud.

**Limites à verbaliser obligatoirement :**
310 lignes (petit dataset), 100% NUIT (non généralisable aux trains de jour), biais UZ à 28%, variables absentes (type de traction, vitesse, nombre d'arrêts).
