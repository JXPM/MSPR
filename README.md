# ObRail Europe — MSPR TPRE612

> **Certification Professionnelle Développeur en Intelligence Artificielle et Data Science** — RNCP36581  
> Bloc E6.1 · *Créer un modèle de données d'une solution I.A en utilisant des méthodes de Data Science*

Pipeline ETL automatisé · Base PostgreSQL relationnelle · API REST FastAPI · Dashboard analytique Streamlit  
appliqués aux flux ferroviaires européens pour l'observatoire **ObRail Europe**.

---

## Table des matières

1. [Contexte & objectifs](#1-contexte--objectifs)
2. [Architecture globale](#2-architecture-globale)
3. [Modélisation des données](#3-modélisation-des-données)
4. [Processus ETL — Talend](#4-processus-etl--talend)
5. [API REST — FastAPI](#5-api-rest--fastapi)
6. [Dashboard — Streamlit](#6-dashboard--streamlit)
7. [Installation pas à pas](#7-installation-pas-à-pas)
8. [Structure du projet](#8-structure-du-projet)
9. [Sources de données](#9-sources-de-données)
10. [Stack technique](#10-stack-technique)
11. [Équipe](#11-équipe)

---

## 1. Contexte & objectifs

**ObRail Europe** est un observatoire indépendant créé en 2018, spécialisé dans l'analyse des flux ferroviaires européens et la promotion de la mobilité durable. Il accompagne les institutions européennes (Commission, Parlement), les ONG environnementales (*Transport & Environnement*, *Back-on-Track*) et les opérateurs ferroviaires (SNCF, ÖBB Nightjet, DB, Trenitalia).

### Problématique

Les données ferroviaires européennes sont fragmentées entre de multiples sources hétérogènes (CSV, GTFS, JSON, API), sans référentiel commun entre pays. ObRail a besoin d'un **entrepôt de données unifié** pour :

| Objectif | Détail |
|---|---|
| Comparaison train de jour / nuit | Mesurer leur contribution au maillage ferroviaire européen |
| Impact environnemental | Évaluer le CO₂ rail vs avion sur les trajets intra-européens |
| Alimentation des modèles IA | Fournir un jeu de données fiable et harmonisé |
| API partenaires | Exposer les données aux institutions et ONG via REST |

### Contraintes identifiées

1. **Dispersion des sources** — CSV, GTFS, JSON, Excel, scraping ; chaque opérateur publie son propre format
2. **Qualité hétérogène** — doublons, codes UIC manquants, fuseaux horaires incohérents
3. **Absence de standard transfrontalier** — pas de référentiel commun entre pays européens
4. **Conformité RGPD** — transparence, documentation et sécurisation des données (aucune donnée personnelle traitée)
5. **Contrainte temporelle** — livraison avant fin d'année pour les travaux du Parlement européen

---

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOURCES DE DONNÉES                        │
│  stations.csv  │  trips.json (BoT)  │  GTFS SNCF  │  emission.csv│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │   ETL — Talend     │
                  │  Extract           │
                  │  Transform/Clean   │
                  │  Load (JDBC)       │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────┐
                  │  PostgreSQL 14+    │
                  │  Base : obrail     │
                  │  11 tables         │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────┐
                  │  API FastAPI       │  :8000
                  │  SQLAlchemy ORM    │
                  │  Pydantic schemas  │
                  └─────────┬──────────┘
                            │  HTTP/JSON
                  ┌─────────▼──────────┐
                  │  Dashboard         │  :8501
                  │  Streamlit         │
                  │  Plotly + Mapbox   │
                  └────────────────────┘
```

---

## 3. Modélisation des données

Le schéma est structuré en **trois couches logiques** garantissant une séparation claire entre structure réseau, circulation réelle et analyse environnementale.

### Diagramme conceptuel (MCD)

![MCD ObRail Europe](MCDFinal.jpg)

### Couche Référentiel

| Table | Clé primaire | Type / Format | Description |
|---|---|---|---|
| `pays` | `iso_pays` VARCHAR(2) | ISO 3166-1 α-2 | 24 pays européens + US, MA |
| `gare` | `code_uic` VARCHAR(10) | Code UIC à 7 chiffres | Nom, coordonnées GPS, pays |
| `operateur` | `code_operateur` VARCHAR(100) | Code interne | Opérateurs ferroviaires européens |
| `ligne` | `id_ligne` INT | `route_id` du GTFS | Nom, distance, type `JOUR`/`NUIT` |
| `type_train` | `id_type_train` SERIAL | Auto-incrémenté | Catégorie de matériel roulant |
| `source` | `id_source` SERIAL | Auto-incrémenté | Traçabilité ETL (URL, format, volume) |

### Couche Exploitation

| Table | Clé primaire | Description |
|---|---|---|
| `trajet` | `trajet_id` VARCHAR(50) | Circulation réelle : gare départ/arrivée, horaires VARCHAR(30) au format `HH:mm:ss` |
| `itineraire` | `(trajet_id, id_itineraire)` | Arrêts intermédiaires ordonnés par `ordre_passage`, rattachés au code UIC |

> **Choix technique** : `heure_depart` et `heure_arrivee` sont stockés en `VARCHAR(30)` car Talend ne convertit pas nativement `String → TIME`. Le format `HH:mm:ss` est normalisé à l'ETL.

### Couche Analyse

| Table | Clé primaire | Description |
|---|---|---|
| `emission` | `id_emission` SERIAL | `empreinte_train_kg` issu de `trips.json` ; `empreinte_avion_kg` = `distance_km × 0.158` (facteur ADEME/BEIS) |

### Tables d'association

| Table | Clés étrangères | Description |
|---|---|---|
| `exploite` | `(code_operateur, id_ligne)` | Opérateur exploite une Ligne, avec un rang |
| `utilisation` | `(code_operateur, id_type_train)` | Opérateur utilise un Type de train |

> Le script SQL complet est dans [`MCD_et_BDD/mspr.sql`](MCD_et_BDD/mspr.sql).  
> Les requêtes de vérification qualité sont dans [`MCD_et_BDD/requetes_verification.sql`](MCD_et_BDD/requetes_verification.sql).

---

## 4. Processus ETL — Talend

L'intégration est orchestrée avec **Talend Open Studio for Data Integration** via des jobs JDBC → PostgreSQL.

### Sources intégrées

| Table(s) cible(s) | Fichier source | Format | Traitement principal |
|---|---|---|---|
| `pays` | `lists_of_iso_3166.csv` | CSV | Mapping code ISO → nom |
| `gare` | `stations.csv` | CSV | Normalisation coordonnées GPS, filtre Europe |
| `source` | Fichier de référencement | XLSX | Traçabilité des imports |
| `operateur` / `ligne` / `trajet` / `itineraire` | `trips.json` (Back-on-Track) | JSON | Dépivotage JSON, jointure route/trip/stop |
| `type_train` | Données GTFS SNCF | ZIP/CSV | Extraction `route_type` |
| `emission` | `emission.csv` | CSV | `empreinte_avion_kg = distance × 0.158` |

### Pipeline de transformation en 5 étapes

```
1. Extraction      Lecture multi-sources (tJavaRaw, tFileInputCSV, tFileInputJSON)
2. Nettoyage       Suppression doublons (tUniqRow)
                   Gestion valeurs nulles (tMap avec valeur par défaut)
                   Normalisation codes UIC (padding 7 chiffres)
                   Homogénéisation horaires → HH:mm:ss
3. Mapping         Correspondance code_operateur ↔ code UIC ↔ ligne
4. Validation      Contrôle d'intégrité référentielle avant INSERT (tFilterRow)
5. Chargement      tPostgresqlOutput en mode INSERT avec gestion des conflits
```

### Calcul des émissions

```
empreinte_avion_kg = distance_km × 0.158
```
Facteur d'émission **ADEME / BEIS** : 0.158 kg CO₂e par km par passager pour l'aviation.  
L'empreinte train (`empreinte_train_kg`) est directement fournie par le champ `emissions_co2e` de `trips.json` (Back-on-Track).

---

## 5. API REST — FastAPI

L'API expose les données ferroviaires en JSON via une architecture RESTful.

**Base URL :** `http://localhost:8000`  
**Documentation interactive :** `http://localhost:8000/docs` *(Swagger UI auto-généré)*  
**Schéma OpenAPI :** `http://localhost:8000/openapi.json`

### Architecture interne

```
backend/
├── app/
│   ├── main.py          ← Initialisation FastAPI + inclusion des routers
│   ├── database.py      ← Engine SQLAlchemy + session factory + Base ORM
│   ├── models/          ← Classes ORM (SQLAlchemy declarative)
│   ├── schemas/         ← Schémas Pydantic (validation requête/réponse)
│   ├── routes/          ← Routers FastAPI (un fichier par domaine)
│   └── services/        ← Logique métier (séparation routes / requêtes DB)
```

### Référence complète des endpoints

#### Santé système

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` | Vérification que l'API répond |

#### Données ferroviaires

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/trajets` | `List[TrajetResponse]` | Tous les trajets |
| `GET` | `/trajets/{trajet_id}` | `TrajetResponse` ou `404` | Trajet par identifiant |
| `GET` | `/gares` | `List[GareResponse]` | Toutes les gares avec coordonnées GPS |
| `GET` | `/lignes` | `List[LigneResponse]` | Toutes les lignes avec type `JOUR`/`NUIT` |

#### Statistiques & KPIs (Dashboard)

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/stats/trajets/count` | `{"total_trajets": int}` | Nombre total de trajets |
| `GET` | `/stats/lignes/count` | `{"total_lignes": int}` | Nombre total de lignes |
| `GET` | `/stats/gares/count` | `{"total_gares": int}` | Nombre total de gares |
| `GET` | `/stats/trajets/type` | `{"JOUR": int, "NUIT": int}` | Répartition trajets jour vs nuit |
| `GET` | `/stats/emissions` | `{"train": float, "avion": float}` | Empreinte CO₂ moyenne par trajet (kg) |
| `GET` | `/stats/operateurs` | `[{"operateur": str, "trajets": int}]` | Volume de trajets par opérateur |
| `GET` | `/stats/trajets/map` | `[{"lat_depart", "lon_depart", "lat_arrivee", "lon_arrivee"}]` | Segments géographiques pour la carte |

### Exemples de réponses

**`GET /stats/trajets/type`**
```json
{
  "JOUR": 6845,
  "NUIT": 4419
}
```

**`GET /stats/emissions`**
```json
{
  "train": 125.4,
  "avion": 932.8
}
```

**`GET /stats/trajets/map`** (extrait)
```json
[
  {
    "lat_depart": 48.8534,
    "lon_depart": 2.3488,
    "lat_arrivee": 50.6292,
    "lon_arrivee": 3.0573
  }
]
```

**`GET /trajets/{trajet_id}` — 404**
```json
{
  "detail": "Trajet not found"
}
```

### Configuration base de données

Variables d'environnement dans `backend/.env` :

```env
DATABASE_URL=postgresql://postgres:<mot_de_passe>@localhost:5432/obrail
```

La connexion est gérée par SQLAlchemy avec un pool de sessions (`SessionLocal`) et le pattern de dépendance FastAPI `Depends(get_db)` pour l'injection automatique en fin de requête.

---

## 6. Dashboard — Streamlit

Tableau de bord analytique temps réel connecté à l'API FastAPI.

**URL :** `http://localhost:8501`

### Pages

| Page | Statut | Contenu |
|---|---|---|
| **Aperçu** | ✅ Disponible | KPIs, carte interactive, CO₂ train vs avion, qualité des données, opérateurs |
| **Réseau** | 🚧 En développement | Analyse de la couverture géographique |
| **Impact Environnemental** | 🚧 En développement | Comparaison détaillée des émissions |
| **Qualité des Données** | 🚧 En développement | Taux de complétude, doublons, anomalies |

### KPIs — Page Aperçu

| KPI | Source API | Description |
|---|---|---|
| Trajets | `/stats/trajets/count` | Nombre total de circulations |
| Opérateurs | `/stats/operateurs` | Nombre d'opérateurs actifs |
| Lignes | `/stats/lignes/count` | Nombre de lignes du réseau |
| Pays couverts | Statique | 24 pays européens |

### Composants

| Composant | Fichier | Librairie | Description |
|---|---|---|---|
| Pie Jour/Nuit | `components/charts.py` | Plotly | Répartition réelle depuis `/stats/trajets/type` |
| CO₂ Trains vs Avions | `components/charts.py` | Plotly | Barres verticales, facteur ADEME |
| Carte réseau | `components/map.py` | Plotly + Mapbox | Segments great-circle + gares avec effet glow |
| Qualité des données | `app.py` | `components.v1.html` | Taux de valeurs manquantes et doublons |
| Volume opérateurs | `components/charts.py` | Plotly | Barres horizontales par opérateur |

### Stratégie de cache

Toutes les données API sont mises en cache avec `@st.cache_data` pour éviter les requêtes répétées à chaque interaction utilisateur. Le cache est invalidé au redémarrage du serveur.

### Architecture client HTTP

Le service `dashboard/services/api_service.py` centralise tous les appels vers l'API FastAPI. Chaque fonction gère les erreurs réseau avec un `try/except` et retourne une valeur par défaut pour ne pas bloquer l'affichage.

---

## 7. Installation pas à pas

### Prérequis

| Outil | Version minimale | Usage |
|---|---|---|
| Python | 3.10+ | Backend + Dashboard |
| PostgreSQL | 14+ | Base de données |
| Talend Open Studio | 8.x | ETL (rejouer les jobs) |
| Git | — | Gestion de version |

### Étape 1 — Cloner le dépôt

```bash
git clone https://github.com/JXPM/MSPR.git
cd MSPR
git checkout api
```

### Étape 2 — Créer l'environnement virtuel (racine du projet)

```bash
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows
pip install -r backend/requirements.txt
pip install -r dashboard/requirements.txt
```

### Étape 3 — Configurer et initialiser la base de données

```bash
# Créer la base
psql -U postgres -c "CREATE DATABASE obrail;"

# Créer le schéma (11 tables)
psql -U postgres -d obrail -f MCD_et_BDD/mspr.sql

# Charger les données
psql -U postgres -d obrail -f MCD_et_BDD/remplissage.sql

# Vérifier la qualité des données (optionnel)
psql -U postgres -d obrail -f MCD_et_BDD/requetes_verification.sql
```

### Étape 4 — Configurer les variables d'environnement

```bash
# Créer le fichier .env dans le dossier backend
echo "DATABASE_URL=postgresql://postgres:<mot_de_passe>@localhost:5432/obrail" > backend/.env
```

### Étape 5 — Lancer l'API backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

> L'API est disponible sur `http://localhost:8000`  
> Swagger UI : `http://localhost:8000/docs`

### Étape 6 — Lancer le dashboard (dans un second terminal)

```bash
cd dashboard
streamlit run app.py
```

> Dashboard disponible sur `http://localhost:8501`

### Vérification rapide

```bash
# Tester l'API
curl http://localhost:8000/health
# Réponse attendue : {"status":"ok"}

curl http://localhost:8000/stats/trajets/type
# Réponse attendue : {"JOUR": X, "NUIT": Y}
```

---

## 8. Structure du projet

```
MSPR/
│
├── backend/                          # API REST FastAPI
│   ├── app/
│   │   ├── main.py                   # Point d'entrée — instancie FastAPI et include les routers
│   │   ├── database.py               # Engine SQLAlchemy, SessionLocal, Base, get_db()
│   │   ├── models/                   # ORM SQLAlchemy (un fichier par entité)
│   │   │   ├── pays.py
│   │   │   ├── gare.py
│   │   │   ├── operateur.py
│   │   │   ├── ligne.py
│   │   │   ├── trajet.py
│   │   │   ├── itineraire.py
│   │   │   ├── emission.py
│   │   │   └── type_train.py
│   │   ├── schemas/                  # Schémas Pydantic (validation I/O)
│   │   │   ├── gare_schema.py
│   │   │   ├── trajet_schema.py
│   │   │   ├── ligne_schema.py
│   │   │   ├── operateur_schema.py
│   │   │   ├── pays_schema.py
│   │   │   ├── emission_schema.py
│   │   │   ├── itineraire_schema.py
│   │   │   └── type_train_schema.py
│   │   ├── routes/                   # Routers FastAPI (un fichier par domaine)
│   │   │   ├── health_routes.py      # GET /health
│   │   │   ├── trajet_routes.py      # GET /trajets, GET /trajets/{id}
│   │   │   ├── gare_routes.py        # GET /gares
│   │   │   ├── ligne_routes.py       # GET /lignes
│   │   │   └── stats_routes.py       # GET /stats/...
│   │   └── services/                 # Logique métier (séparé des routes)
│   │       ├── stats_service.py      # count_trajets, count_lignes, count_gares
│   │       ├── trajet_service.py
│   │       ├── gare_service.py
│   │       └── ligne_service.py
│   ├── .env                          # Variables d'environnement (non versionné)
│   └── requirements.txt
│
├── dashboard/                        # Tableau de bord Streamlit
│   ├── app.py                        # Application principale + routing des pages
│   ├── components/
│   │   ├── charts.py                 # Graphiques Plotly (pie, CO2, opérateurs)
│   │   ├── kpi_cards.py              # Cartes KPI
│   │   └── map.py                    # Carte réseau ferroviaire (Scattermapbox)
│   ├── _pages/                       # Pages futures (non actives — préfixe _ exclut Streamlit)
│   │   ├── overview.py
│   │   ├── network.py
│   │   ├── environment.py
│   │   └── data_quality.py
│   ├── services/
│   │   └── api_service.py            # Client HTTP vers l'API FastAPI
│   ├── config/
│   │   └── api_config.py             # URL de base de l'API
│   └── requirements.txt
│
├── MCD_et_BDD/                       # Base de données & ETL
│   ├── mspr.sql                      # Script de création du schéma PostgreSQL (11 tables)
│   ├── remplissage.sql               # Script de chargement des données
│   ├── requetes_verification.sql     # Requêtes de contrôle qualité
│   ├── MCDFinal.loo                  # Fichier source Looping (MCD éditable)
│   └── integration via talend.txt   # Documentation des jobs ETL Talend
│
├── venv/                             # Environnement virtuel Python (non versionné)
├── MCDFinal.jpg                      # Export visuel du MCD
├── journal.sh                        # Journal de bord du projet
├── .gitignore
└── README.md                         # Ce fichier
```

---

## 9. Sources de données

| Source | Format | Tables alimentées | Licence | URL |
|---|---|---|---|---|
| Back-on-Track Night Train Database | JSON (`trips.json`) | `operateur`, `ligne`, `trajet`, `itineraire`, `emission` | Open Data | [back-on-track.eu](https://back-on-track.eu/) |
| Trainline EU — stations.csv | CSV | `gare` | Open Data (MIT) | [github.com/trainline-eu/stations](https://github.com/trainline-eu/stations) |
| ISO 3166-1 | CSV | `pays` | Domaine public | [iso.org](https://www.iso.org/iso-3166-country-codes.html) |
| SNCF Open Data (GTFS) | ZIP/CSV | `type_train` | Open Data | [transport.data.gouv.fr](https://transport.data.gouv.fr/) |
| emission.csv (calculé) | CSV | `emission` | Calculé (ADEME/BEIS) | Facteur : 0.158 kg CO₂e/km/passager |

### Webographie complémentaire

- [European Data Portal](https://data.europa.eu/) — Données ouvertes européennes
- [Eurostat Transport](https://ec.europa.eu/eurostat/web/transport) — Statistiques ferroviaires
- [MobilityDatabase](https://mobilitydatabase.org/) — Jeux de données GTFS internationaux
- [Transitland](https://www.transit.land/) — Réseau de transport mondial

---

## 10. Stack technique

### Backend

| Technologie | Version | Rôle |
|---|---|---|
| **Python** | 3.10+ | Langage principal |
| **FastAPI** | latest | Framework API REST asynchrone avec génération Swagger auto |
| **SQLAlchemy** | latest | ORM + gestion des sessions et du pool de connexions |
| **Pydantic** | v2 | Validation et sérialisation des schémas de données |
| **Alembic** | latest | Migrations de schéma (versionnement de la DB) |
| **PostgreSQL** | 14+ | SGBD relationnel — base `obrail` |
| **psycopg2-binary** | latest | Driver PostgreSQL pour Python |
| **python-dotenv** | latest | Chargement des variables d'environnement depuis `.env` |
| **pytest + httpx** | latest | Tests automatisés de l'API |
| **uvicorn** | latest | Serveur ASGI pour FastAPI |

### Dashboard

| Technologie | Version | Rôle |
|---|---|---|
| **Streamlit** | latest | Framework de tableau de bord web en Python |
| **Plotly** | latest | Visualisations interactives (graphiques, carte Mapbox) |
| **Pandas** | latest | Manipulation et analyse des DataFrames |
| **Requests** | latest | Client HTTP pour consommer l'API FastAPI |

### Data / ETL

| Technologie | Rôle |
|---|---|
| **Talend Open Studio 8** | Orchestration ETL — jobs d'extraction, transformation et chargement |
| **PostgreSQL JDBC** | Connexion Talend → PostgreSQL |

### Conformité RGPD

Aucune donnée personnelle n'est collectée ou traitée. Toutes les sources sont issues de l'**open data** public. La traçabilité des imports est assurée par la table `source` (URL, format, date, volume). Les accès à la base sont restreints par authentification PostgreSQL.

---

## 11. Équipe

Projet réalisé dans le cadre de la **MSPR TPRE612** — Promotion 2025-2026 DIA/DIADS  
Certification Professionnelle Développeur en Intelligence Artificielle et Data Science (RNCP36581)

| Membre | Rôle principal |
|---|---|
| **Kouamé Johan BILÉ** | API REST FastAPI, Dashboard Streamlit, Documentation, Conformité RGPD |
| **Joseph HACCANDY** | ETL Talend, Modélisation BDD, Sources de données, Documentation |
| **Glody KUTUMBAKANA** | ETL Talend, Modélisation BDD, Documentation |
| **Nabil DIA** | API REST FastAPI, Dashboard Streamlit |

---

*Projet pédagogique encadré — Promotion 2025-2026 · Certification RNCP36581*
