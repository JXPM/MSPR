# ObRail Europe — MSPR TPRE532

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
7. [Monitoring & Observabilité](#7-monitoring--observabilité)
8. [Sécurité](#8-sécurité)
9. [Tests](#9-tests)
10. [Installation Docker (recommandée)](#10-installation-docker-recommandée)
11. [Structure du projet](#11-structure-du-projet)
12. [Sources de données](#12-sources-de-données)
13. [Stack technique](#13-stack-technique)
14. [Équipe](#14-équipe)

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
                  │  PostgreSQL 17     │
                  │  Base : mspr2      │
                  │  11 tables         │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────┐
                  │  API FastAPI       │  :8000
                  │  SQLAlchemy ORM    │
                  │  Rate limiting     │
                  │  Security headers  │
                  │  /metrics (Prom.)  │
                  └──────┬──────┬──────┘
                         │      │
              HTTP/JSON  │      │ /metrics
                  ┌──────▼──┐  ┌▼──────────┐
                  │Dashboard│  │ Prometheus │  :9090
                  │Streamlit│  │  scraping  │
                  │  :8501  │  └─────┬──────┘
                  └─────────┘        │
                                ┌────▼──────┐
                                │  Grafana  │  :3010
                                │ dashboard │
                                └───────────┘
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
**Métriques Prometheus :** `http://localhost:8000/metrics`

### Architecture interne

```
backend/
├── app/
│   ├── main.py          ← FastAPI + middlewares sécurité + rate limiting + Prometheus
│   ├── database.py      ← Engine SQLAlchemy + session factory
│   ├── models/          ← Classes ORM (SQLAlchemy declarative)
│   ├── schemas/         ← Schémas Pydantic (validation requête/réponse)
│   ├── routes/          ← Routers FastAPI (un fichier par domaine)
│   └── services/        ← Logique métier
```

### Référence complète des endpoints

#### Santé système

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` | Vérification que l'API répond |
| `GET` | `/metrics` | texte Prometheus | Métriques pour Prometheus |

#### Données ferroviaires

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/trajets` | `List[TrajetResponse]` | Tous les trajets *(rate limité)* |
| `GET` | `/trajets/{trajet_id}` | `TrajetResponse` ou `404` | Trajet par identifiant *(rate limité)* |
| `GET` | `/gares` | `List[GareResponse]` | Toutes les gares avec coordonnées GPS |
| `GET` | `/lignes` | `List[LigneResponse]` | Toutes les lignes avec type `JOUR`/`NUIT` |

#### Statistiques & KPIs *(rate limités)*

| Méthode | Endpoint | Réponse | Description |
|---|---|---|---|
| `GET` | `/stats/trajets/count` | `{"total_trajets": int}` | Nombre total de trajets |
| `GET` | `/stats/lignes/count` | `{"total_lignes": int}` | Nombre total de lignes |
| `GET` | `/stats/gares/count` | `{"total_gares": int}` | Nombre total de gares |
| `GET` | `/stats/pays/count` | `{"total_pays": int}` | Nombre de pays couverts |
| `GET` | `/stats/trajets/type` | `{"JOUR": int, "NUIT": int}` | Répartition trajets jour vs nuit |
| `GET` | `/stats/emissions` | `{"train": float, "avion": float}` | Empreinte CO₂ moyenne par trajet (kg) |
| `GET` | `/stats/operateurs` | `[{"operateur": str, "trajets": int}]` | Volume de trajets par opérateur |
| `GET` | `/stats/trajets/map` | `[{lat/lon départ/arrivée}]` | Segments géographiques pour la carte |

> Les endpoints `/trajets` et `/stats/*` retournent **HTTP 429** au-delà de 60 requêtes/minute par IP.

---

## 6. Dashboard — Streamlit

Tableau de bord analytique temps réel connecté à l'API FastAPI.

**URL :** `http://localhost:8501`

### Pages

| Page | Contenu |
|---|---|
| **Trajets** | Liste des trajets, itinéraires, carte réseau |
| **Observatoire** | KPIs, CO₂ train vs avion, répartition jour/nuit, opérateurs |
| **Supervision** | État des endpoints, latence, taux d'erreur 5xx (via Prometheus) |

### Accessibilité RGAA

- Contraste texte `--muted` : ratio **5.2:1** (conforme RGAA AA, seuil 4.5:1)
- Skip link "Aller au contenu principal" présent dans le DOM
- Navigation clavier fonctionnelle

### Architecture client HTTP

`dashboard/services/api_service.py` centralise tous les appels API et les requêtes Prometheus. Chaque fonction est défensive : elle retourne une valeur par défaut sans lever d'exception en cas d'erreur réseau.

---

## 7. Monitoring & Observabilité

La stack de monitoring collecte et visualise les métriques de l'API en temps réel.

### Composants

| Service | URL | Rôle |
|---|---|---|
| **Prometheus** | http://localhost:9090 | Collecte les métriques `/metrics` du backend toutes les 15s |
| **Grafana** | http://localhost:3010 | Visualisation — login `admin` / `admin` |

### Dashboard Grafana — ObRail FastAPI Metrics

Le dashboard `monitoring/grafana/dashboards/fastapi-observability.json` contient 6 panels :

| Panel | Métrique PromQL |
|---|---|
| Requêtes / seconde | `sum(rate(http_request_duration_seconds_count[1m])) by (handler)` |
| Taux d'erreurs 4xx / 5xx | `sum(rate(...{status_code=~"4.."}[1m]))` |
| Latence p50 / p95 / p99 | `histogram_quantile(0.50/0.95/0.99, ...)` |
| Requêtes en cours | `http_requests_inprogress` |
| Total requêtes | `sum(http_request_duration_seconds_count)` |
| Backend UP/DOWN | `up{job="obrail-backend"}` |

### Reproductibilité

La datasource Prometheus dispose d'un **UID fixe** `obrail-prometheus` défini dans `monitoring/grafana/datasources/prometheus.yml`. Le dashboard JSON référence cet UID littéralement — le dashboard s'affiche immédiatement sur toute machine sans configuration manuelle.

---

## 8. Sécurité

### Rate Limiting

Les endpoints `/trajets` et `/stats/*` sont limités à **60 requêtes/minute par IP**. Au-delà, l'API retourne :

```json
HTTP 429 Too Many Requests
{"detail": "Rate limit exceeded. Try again in 60 seconds."}
```

Implémentation : middleware `RateLimitMiddleware` dans `backend/app/main.py`, utilisant `slowapi` comme dépendance.

### Headers de sécurité HTTP

Chaque réponse de l'API inclut ces headers injectés par `SecurityHeadersMiddleware` :

| Header | Valeur | Protection |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Empêche le MIME sniffing |
| `X-Frame-Options` | `DENY` | Empêche le clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Filtre XSS navigateurs anciens |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Contrôle les informations de référent |

### CORS

L'API accepte les requêtes cross-origin uniquement depuis `http://localhost:5173` et `http://localhost:4173` (environnements de développement Vite). En production, configurer `CORS_ORIGINS` dans le `.env`.

### RGPD

Aucune donnée personnelle collectée ni traitée. Toutes les sources sont issues de l'open data public. Traçabilité des imports assurée par la table `source`.

---

## 9. Tests

### Tests unitaires

| Suite | Commande | Couverture |
|---|---|---|
| Backend (91 tests) | `cd backend && pytest tests/ -v` | Routes, services, modèles, qualité des données |
| Dashboard (31 tests) | `cd dashboard && pytest tests/ -v` | Client API, graphiques Plotly, composants UI |

### Tests E2E Playwright

```bash
# Installer le navigateur (une seule fois)
playwright install chromium

# Lancer les tests (nécessite la stack en cours d'exécution)
cd dashboard && pytest tests_e2e/ -v
```

| Test | Description |
|---|---|
| `test_home_loads` | La page charge et contient "ObRail" |
| `test_nav_trajets` | Navigation vers Trajets, tableau visible |
| `test_nav_observatoire` | Page Observatoire sans erreur |
| `test_nav_supervision` | Page Supervision contient "health" ou "api" |
| `test_skip_link_exists` | Skip link RGAA présent dans le DOM |
| `test_h1_present` | Balise `<h1>` présente sur la page |

### CI/CD GitHub Actions

Le pipeline `.github/workflows/main.yml` exécute automatiquement à chaque push :

| Job | Déclencheur | Description |
|---|---|---|
| `frontend-test` | Changements `dashboard/` | Lint ruff + tests unitaires |
| `backend-test` | Changements `backend/` | Lint ruff + tests avec PostgreSQL |
| `talend-lint` | Changements `talend/` | ShellCheck + scan secrets |
| `talend-etl-dryrun` | Changements `talend/` | Exécution ETL complète en base test |
| `e2e-test` | Après frontend + backend | Stack Docker + tests Playwright |
| `docker-frontend` | Push sur `main` | Build + push image GHCR |
| `docker-backend` | Push sur `main` | Build + push image GHCR |

---

## 10. Installation Docker (recommandée)

La stack complète se lance en une commande. Voir [`LANCEMENT.md`](LANCEMENT.md) pour le guide détaillé.

### Démarrage rapide

```bash
# 1. Cloner le projet
git clone https://github.com/JXPM/MSPR.git
cd MSPR

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec les mots de passe souhaités

# 3. Lancer toute la stack (5 services)
docker compose up -d --build
```

### Services démarrés

| Service | URL | Description |
|---|---|---|
| Dashboard | http://localhost:8501 | Interface principale |
| API | http://localhost:8000/docs | Documentation Swagger |
| Grafana | http://localhost:3010 | Monitoring (admin/admin) |
| Prometheus | http://localhost:9090 | Métriques brutes |
| PostgreSQL | localhost:5433 | Base de données |

### Commandes utiles (avec `make`)

```bash
make up          # Démarrer
make down        # Arrêter
make logs        # Voir les logs
make test        # Lancer tous les tests
make ps          # État des containers
make db-shell    # Shell PostgreSQL
```

---

## 11. Structure du projet

```
MSPR3/
├── backend/                          # API REST FastAPI
│   ├── app/
│   │   ├── main.py                   # FastAPI + middlewares sécurité + rate limiting
│   │   ├── database.py               # Engine SQLAlchemy, SessionLocal
│   │   ├── models/                   # ORM SQLAlchemy
│   │   ├── schemas/                  # Schémas Pydantic
│   │   ├── routes/                   # Routers (health, trajet, gare, ligne, stats)
│   │   └── services/                 # Logique métier
│   ├── tests/                        # 91 tests unitaires pytest
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                        # Tableau de bord Streamlit
│   ├── app.py                        # Application principale
│   ├── components/                   # Charts, KPI, carte
│   ├── _pages/                       # Pages (Trajets, Observatoire, Supervision)
│   ├── services/
│   │   └── api_service.py            # Client HTTP API + requêtes Prometheus
│   ├── tests/                        # 31 tests unitaires pytest
│   ├── tests_e2e/                    # Tests Playwright (navigation + accessibilité)
│   ├── Dockerfile
│   └── requirements.txt
│
├── monitoring/
│   ├── prometheus.yml                # Config scraping Prometheus
│   └── grafana/
│       ├── dashboards/
│       │   ├── dashboards.yml        # Provisioning Grafana
│       │   └── fastapi-observability.json  # Dashboard 6 panels
│       └── datasources/
│           └── prometheus.yml        # Datasource UID fixe : obrail-prometheus
│
├── talend/                           # ETL Talend
│   ├── Jobs/                         # 9 jobs compilés (.jar)
│   ├── dump/                         # Dumps PostgreSQL
│   └── lancement/                    # Scripts de lancement
│
├── .github/workflows/main.yml        # CI/CD GitHub Actions
├── docker-compose.yml                # Orchestration 5 services
├── Makefile                          # Commandes raccourcies
├── .env.example                      # Template variables d'environnement
├── why.md                            # Journal des modifications techniques
├── LANCEMENT.md                      # Guide de démarrage détaillé
└── README.md                         # Ce fichier
```

---

## 12. Sources de données

| Source | Format | Tables alimentées | Licence |
|---|---|---|---|
| Back-on-Track Night Train Database | JSON | `operateur`, `ligne`, `trajet`, `itineraire`, `emission` | Open Data |
| Trainline EU — stations.csv | CSV | `gare` | Open Data (MIT) |
| ISO 3166-1 | CSV | `pays` | Domaine public |
| SNCF Open Data (GTFS) | ZIP/CSV | `type_train` | Open Data |
| emission.csv (calculé) | CSV | `emission` | Calculé (ADEME/BEIS 0.158 kg CO₂e/km) |

---

## 13. Stack technique

### Backend

| Technologie | Rôle |
|---|---|
| **Python 3.12** | Langage principal |
| **FastAPI** | Framework API REST asynchrone + Swagger auto |
| **SQLAlchemy** | ORM + pool de connexions |
| **Pydantic v2** | Validation et sérialisation |
| **Alembic** | Migrations de schéma |
| **PostgreSQL 17** | SGBD relationnel |
| **prometheus-fastapi-instrumentator** | Exposition des métriques `/metrics` |
| **slowapi** | Rate limiting par IP |
| **pytest + httpx** | Tests automatisés |

### Dashboard

| Technologie | Rôle |
|---|---|
| **Streamlit** | Framework tableau de bord web |
| **Plotly** | Visualisations interactives |
| **Pandas** | Manipulation des données |
| **Requests** | Client HTTP vers l'API |
| **Playwright** | Tests E2E navigateur |

### Monitoring

| Technologie | Rôle |
|---|---|
| **Prometheus 2.55** | Collecte de métriques (scraping toutes les 15s) |
| **Grafana 11.3** | Visualisation + alerting |

### Infrastructure

| Technologie | Rôle |
|---|---|
| **Docker + Docker Compose** | Conteneurisation et orchestration des 5 services |
| **GitHub Actions** | CI/CD — tests, lint, build images, E2E |

### Data / ETL

| Technologie | Rôle |
|---|---|
| **Talend Open Studio 8** | Orchestration ETL |
| **PostgreSQL JDBC** | Connexion Talend → PostgreSQL |

---

## 14. Équipe

Projet réalisé dans le cadre de la **MSPR TPRE532** — Promotion 2025-2026 DIA/DIADS
Certification Professionnelle Développeur en Intelligence Artificielle et Data Science (RNCP36581)

| Membre | Rôle principal |
|---|---|
| **Kouamé Johan BILÉ** | API REST FastAPI, Dashboard Streamlit, Documentation |
| **Joseph HACCANDY** | ETL Talend, Modélisation BDD, Sources de données, Sécurité, Monitoring |
| **Glody KUTUMBAKANA** | ETL Talend, Modélisation BDD, Documentation |
| **Nabil DIA** | API REST FastAPI, Dashboard Streamlit |

---

*Projet pédagogique encadré — Promotion 2025-2026 · Certification RNCP36581*
