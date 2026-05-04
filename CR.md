# CR — Compte-Rendu de compréhension du projet ObRail Europe

> Ce document explique le projet dans son entièreté, pour quelqu'un qui débute.
> Il couvre : le backend, le frontend, la base de données, l'ETL, le monitoring et l'intégration continue (GitHub Actions).

---

## 1. Vue d'ensemble — c'est quoi ce projet ?

**ObRail Europe** est une application web de data science qui observe le réseau ferroviaire européen.

Elle répond à des questions comme :
- Combien de trajets existent entre deux pays ?
- Quelles sont les émissions CO₂ d'un trajet en train vs en avion ?
- Quels opérateurs ferroviaires couvrent quelles lignes ?

L'application est composée de **5 blocs** qui s'assemblent comme des briques :

```
Données brutes (CSV, JSON, GTFS)
        ↓
  [ETL Talend]  ← transforme et nettoie les données
        ↓
[Base PostgreSQL] ← stocke toutes les données propres
        ↓
  [Backend FastAPI] ← expose les données via une API REST
        ↓
[Dashboard Streamlit] ← affiche les données dans un navigateur
        ↑
  [Monitoring] ← surveille que tout fonctionne
```

---

## 2. La Base de données — PostgreSQL

### C'est quoi ?
PostgreSQL est un système de gestion de base de données (SGBD). On y stocke toutes les informations du projet dans des **tables** (comme des tableurs Excel liés entre eux).

### Comment elle est initialisée ?
Au premier démarrage de Docker, PostgreSQL charge automatiquement le fichier `talend/dump/mspr2_dump_2026-04-22.sql`. Ce fichier contient toutes les tables et les données déjà remplies.

### Les 8 tables principales :

| Table | Contenu |
|---|---|
| `pays` | Liste des pays européens (code ISO : FR, DE, ES…) |
| `gare` | Toutes les gares (nom, coordonnées GPS, pays) |
| `operateur` | Compagnies ferroviaires (SNCF, Eurostar, DB…) |
| `ligne` | Lignes ferroviaires (JOUR ou NUIT) |
| `type_train` | Catégories de trains (TGV, Intercity, Nightjet…) |
| `trajet` | Un trajet = gare de départ + arrivée + horaires |
| `itineraire` | Les arrêts intermédiaires d'un trajet |
| `emission` | Empreinte CO₂ en kg (train et avion comparés) |

### Comment les tables sont liées ?
Un `trajet` appartient à une `ligne`. Une `ligne` est exploitée par un `operateur`. Une `gare` est dans un `pays`. C'est ce qu'on appelle un **MCD** (Modèle Conceptuel de Données), visible dans `MCD_et_BDD/MCDFinal.jpg`.

### Accès local
- Hôte : `localhost`
- Port : `5433` (attention, pas 5432 — c'est pour éviter les conflits)
- Base : `mspr2`
- Utilisateur : configuré dans le fichier `.env`

---

## 3. L'ETL Talend — pipeline de données

### C'est quoi ?
ETL = **E**xtract **T**ransform **L**oad.
Talend est un outil qui lit des fichiers bruts (CSV, JSON, GTFS), les nettoie et les insère dans la base de données.

### Les sources de données
- `stations.csv` — gares issues d'OpenStreetMap
- `trips.json` — trajets européens (Back-on-Track)
- Fichiers GTFS SNCF — horaires officiels de la SNCF
- `lists_of_iso_3166.csv` — codes pays ISO

### Les 9 jobs (dans l'ordre d'exécution)
Chaque job est un programme Java compilé (`.jar`) qui traite une table :

1. `pays` — charge les codes pays
2. `gare` — charge les gares avec leurs coordonnées GPS
3. `operateur` — charge les compagnies ferroviaires
4. `type_train` — charge les types de matériel roulant
5. `ligne` — charge les lignes (JOUR/NUIT)
6. `trajet` — charge les trajets
7. `exploite` — lie opérateurs ↔ lignes
8. `itineraire` — charge les arrêts intermédiaires
9. `emission` — calcule les CO₂ (train depuis trips.json, avion = distance × 0.158)

### Comment le CO₂ avion est calculé ?
La formule est : `distance_km × 0.158` (facteur ADEME/BEIS).

### Pourquoi des `.jar` et pas du code source ?
Les jobs Talend sont compilés en Java. Le code source reste dans Talend Open Studio (logiciel externe), et on versionne uniquement les JAR pour les déployer.

---

## 4. Le Backend — FastAPI

### C'est quoi ?
FastAPI est un framework Python pour créer des **API REST**.
Une API REST, c'est un serveur qui répond à des requêtes HTTP (comme un navigateur qui demande une page, mais ici on demande des données JSON).

### Rôle
Le backend lit la base de données et expose les données via des URLs appelées **endpoints**.

### Les endpoints disponibles

| URL | Ce qu'elle retourne |
|---|---|
| `GET /health` | `{"status": "ok"}` — le backend fonctionne |
| `GET /gares` | Liste de toutes les gares |
| `GET /lignes` | Liste de toutes les lignes |
| `GET /trajets` | Liste de tous les trajets |
| `GET /trajets/{id}` | Détail d'un trajet précis |
| `GET /trajets/{id}/itineraire` | Les arrêts d'un trajet |
| `GET /stats/trajets/count` | Nombre total de trajets |
| `GET /stats/gares/count` | Nombre total de gares |
| `GET /stats/lignes/count` | Nombre total de lignes |
| `GET /stats/trajets/type` | Répartition JOUR / NUIT |
| `GET /stats/emissions` | Moyenne CO₂ train vs avion |
| `GET /stats/operateurs` | Nb de trajets par opérateur |
| `GET /stats/trajets/map` | Coordonnées GPS pour la carte |

### Documentation interactive
Quand le backend tourne, tu peux accéder à `http://localhost:8000/docs` pour tester tous les endpoints directement dans le navigateur (interface Swagger automatique).

### Architecture du code (`backend/app/`)

```
app/
├── main.py        ← point d'entrée, configure l'app et ses routes
├── database.py    ← connexion à PostgreSQL via SQLAlchemy
├── models/        ← les 8 tables de la BDD représentées en Python
├── schemas/       ← les formats de données attendus (validation Pydantic)
├── routes/        ← les 5 fichiers qui définissent les endpoints
└── services/      ← la logique métier (requêtes SQL complexes)
```

### Comment FastAPI parle à PostgreSQL ?
Via **SQLAlchemy** : une bibliothèque Python qui traduit les requêtes Python en SQL.
La connexion passe par la variable `DATABASE_URL` du fichier `.env`.

### Les tests du backend (`backend/tests/`)
8 fichiers de tests qui vérifient :
- Que `/health` répond bien
- Que les CORS sont corrects (sécurité navigateur)
- Que les données sont cohérentes
- Que les modèles fonctionnent
- Que les statistiques sont calculées correctement

---

## 5. Le Frontend — Streamlit (Dashboard)

### C'est quoi ?
Streamlit est un framework Python qui génère automatiquement des interfaces web à partir de code Python. Pas besoin de HTML/CSS/JavaScript.

### Rôle
Le dashboard affiche les données de l'API backend sous forme de graphiques, cartes et tableaux interactifs.

### Les 3 pages

| Page | Ce qu'elle montre |
|---|---|
| `observatoire.py` | Vue d'ensemble : métriques globales, graphiques principaux |
| `trajets.py` | Exploration détaillée : filtres, cartes de trajets, horaires |
| `supervision.py` | État du système : santé de l'API, statuts des services |

### Comment le dashboard parle au backend ?
Via `dashboard/services/api_service.py` : un client HTTP qui fait des requêtes `GET` vers `http://backend:8000` (en Docker) ou `http://localhost:8000` (en local).

### Les composants (`dashboard/components/`)
- `charts.py` — génère les graphiques Plotly (barres, lignes, secteurs)
- `map.py` — génère les cartes interactives Folium
- `icons.py` — wrapper pour les icônes Lucide

### Accès
- URL : `http://localhost:8501`

---

## 6. Le Monitoring — Prometheus + Grafana

### C'est quoi ?
Le monitoring permet de **surveiller en temps réel** que les services fonctionnent, sans avoir à les regarder manuellement.

### Prometheus
- C'est un outil qui **collecte des métriques** (données de performance) en interrogeant les services toutes les 15 secondes
- Il stocke l'historique de ces métriques dans un volume Docker persistant
- Il scrute l'endpoint `http://backend:8000/metrics`
- Accès : `http://localhost:9090`

### Grafana
- C'est l'outil de **visualisation** : il affiche les métriques Prometheus sous forme de dashboards graphiques
- Accès : `http://localhost:3010` (login : `admin` / mot de passe dans `.env`)

### Comment ils communiquent ?
```
Backend FastAPI (port 8000)
        │
        │  expose /metrics (toutes les 15s)
        ↓
Prometheus (port 9090)
        │
        │  requête PromQL
        ↓
Grafana (port 3010)
```

La configuration de Prometheus est dans `monitoring/prometheus.yml`.
La configuration de Grafana (sources de données + dashboards) est dans `monitoring/grafana/`.

---

### Pourquoi `prometheus-fastapi-instrumentator` ?

C'est la bibliothèque Python qui **expose automatiquement les métriques** du backend FastAPI.

Sans elle, Prometheus n'aurait rien à scruter : le backend n'aurait pas d'endpoint `/metrics`.

Elle est activée en deux lignes dans `backend/app/main.py` :

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

Ce que ça fait :
- `.instrument(app)` — injecte un middleware invisible qui mesure chaque requête HTTP (durée, code de réponse, endpoint appelé)
- `.expose(app)` — crée l'endpoint `/metrics` que Prometheus scrute toutes les 15 secondes

Les métriques exposées sont :
| Métrique | Ce qu'elle mesure |
|---|---|
| `http_request_duration_seconds` | Durée de chaque requête (histogramme) |
| `http_requests_inprogress` | Nombre de requêtes en cours à l'instant T |

---

### Pourquoi un dashboard custom et pas le dashboard 17242 ?

Lors de la mise en place du monitoring, l'objectif initial était d'importer le dashboard communautaire **17242** depuis Grafana Labs. Ce dashboard n'existe pas — l'ID 17242 retourne une 404 sur grafana.com.

Le dashboard FastAPI le plus connu sur Grafana Labs est le **16110** ("FastAPI Observability" par Blueswen). On a tenté de l'importer, mais il requiert **deux datasources** : Prometheus ET **Loki** (outil de collecte de logs). Notre stack ne comprend pas Loki — ajouter Loki aurait alourdi inutilement le projet.

**Décision** : créer un dashboard custom (`monitoring/grafana/dashboards/fastapi-observability.json`) qui utilise uniquement Prometheus, avec les métriques réellement pertinentes pour ce projet.

---

### Le dashboard "ObRail — FastAPI Metrics"

Accessible à : `http://localhost:3010/d/obrail-fastapi`

Il contient 6 panels :

| Panel | Type | Métrique PromQL | Pourquoi |
|---|---|---|---|
| **Requetes / seconde** | Time series | `rate(http_request_duration_seconds_count[1m])` | Mesure le trafic entrant par endpoint. Permet de détecter des pics ou des baisses d'activité |
| **Taux d'erreurs 4xx / 5xx** | Time series | `rate(...{status_code=~"4.."})` et `rate(...{status_code=~"5.."})` | Sépare les erreurs client (4xx = mauvaise requête) des erreurs serveur (5xx = bug backend). 4xx en orange, 5xx en rouge |
| **Latence p50/p95/p99** | Time series | `histogram_quantile(0.95, ...)` | Les percentiles sont plus fiables que la moyenne. p95 = 95% des requêtes répondent en moins de X ms. Détecte la lenteur sans que la moyenne le masque |
| **Requetes en cours** | Time series | `http_requests_inprogress` | Nombre de requêtes simultanées actives. Un pic inhabituel peut signaler un problème de performance |
| **Total requetes** | Stat | `sum(http_request_duration_seconds_count)` | Compteur global depuis le démarrage. Indicateur de volume d'utilisation |
| **Backend UP** | Stat | `up{job="obrail-backend"}` | Affiche vert (UP) ou rouge (DOWN). Premier indicateur de santé du service |

**Pourquoi les percentiles (p50, p95, p99) et pas la moyenne ?**

La moyenne ment. Si 99 requêtes répondent en 10ms et 1 requête met 10 secondes, la moyenne est d'environ 110ms — ça paraît acceptable. Le p99 révèle qu'1% des utilisateurs attendent 10 secondes.

---

### Comment le dashboard survit aux redémarrages ?

Le fichier JSON `monitoring/grafana/dashboards/fastapi-observability.json` est monté dans le container Grafana via le volume déclaré dans `docker-compose.yml`. Grafana relit ce dossier toutes les 30 secondes (`updateIntervalSeconds: 30` dans `monitoring/grafana/dashboards/dashboards.yml`).

Résultat : même après `docker compose down && docker compose up`, le dashboard réapparaît automatiquement sans aucune manipulation.

---

## 7. L'intégration continue — GitHub Actions (CI/CD)

### C'est quoi ?
CI/CD = **C**ontinuous **I**ntegration / **C**ontinuous **D**eployment.

C'est un système automatique qui, à chaque fois que tu pousses du code sur GitHub, exécute une série de vérifications pour s'assurer que rien n'est cassé.

### Quand ça se déclenche ?
- À chaque `git push` sur la branche `main` ou `develop`
- À chaque Pull Request vers `main`

### Les 8 étapes du pipeline (`.github/workflows/main.yml`)

#### Étape 1 — Détection des changements (`changes`)
Regarde quels dossiers ont changé (`dashboard/`, `backend/`, `talend/`). Inutile de tout retester si tu n'as modifié que le frontend.

#### Étape 2 — Tests du Frontend (`frontend-test`)
Sur un serveur Linux temporaire (Ubuntu), GitHub :
1. Installe Python 3.12
2. Installe les dépendances du dashboard
3. Vérifie la syntaxe du code avec **ruff** (linter Python)
4. Vérifie que tous les fichiers `.py` se parsent sans erreur
5. Lance les tests pytest du dashboard
6. Sauvegarde le rapport de couverture de tests

#### Étape 3 — Tests du Backend (`backend-test`)
Sur un serveur Ubuntu avec une PostgreSQL de test :
1. Installe Python 3.12 + dépendances backend
2. Lint avec ruff
3. Lance les 91 tests pytest avec une base de données réelle
4. Sauvegarde le rapport de couverture

#### Étape 4 — Validation Talend (`talend-lint`)
1. **ShellCheck** : vérifie que les scripts bash sont corrects
2. **Scan de secrets** : vérifie qu'il n'y a pas de mots de passe en clair dans les scripts
3. **Structure** : vérifie que les 9 fichiers `.jar` sont présents
4. **Intégrité** : vérifie que les JAR ne sont pas corrompus

#### Étape 5 — Dry-run ETL (`talend-etl-dryrun`)
Lance les 9 jobs Talend sur une base de test pour vérifier qu'ils s'exécutent sans crash.

#### Étapes 6 & 7 — Build Docker (`docker-frontend`, `docker-backend`)
**Seulement sur la branche `main`**, si les tests passent :
- Construit les images Docker du frontend et du backend
- Les pousse dans le registre `ghcr.io` (GitHub Container Registry)
- Elles sont taggées avec le nom de branche, le SHA du commit, et `latest`

#### Étape 8 — Résumé (`summary`)
Affiche un tableau récapitulatif des résultats dans GitHub :
```
| Bloc                | Statut  |
|---------------------|---------|
| Frontend tests      | success |
| Backend tests       | success |
| Talend lint         | success |
| Talend ETL dry-run  | success |
```

### Pourquoi c'est important ?
Sans CI/CD, si quelqu'un push du code qui casse le backend, tout le monde en souffre. Avec CI/CD, GitHub bloque automatiquement les merges qui font planter les tests.

---

## 8. Docker et Docker Compose

### C'est quoi Docker ?
Docker permet d'emballer une application avec tout ce dont elle a besoin (Python, bibliothèques, OS) dans une **image**. Cette image tourne dans un **container** — un environnement isolé, identique sur n'importe quelle machine.

### C'est quoi Docker Compose ?
Docker Compose permet de définir et lancer **plusieurs containers en même temps** avec un seul fichier (`docker-compose.yml`).

### Les 5 services du projet

| Service | Image | Port | Rôle |
|---|---|---|---|
| `postgres` | postgres:17-alpine | 5433 | Base de données |
| `backend` | Image custom Python | 8000 | API FastAPI |
| `frontend` | Image custom Python | 8501 | Dashboard Streamlit |
| `prometheus` | prom/prometheus | 9090 | Collecte métriques |
| `grafana` | grafana/grafana | 3010 | Visualisation métriques |

### Le réseau `obrail`
Tous les containers sont dans le même réseau Docker appelé `obrail`. Ils se parlent via leurs noms de service (ex: le backend appelle la BDD via `postgres:5432`, pas `localhost:5433`).

### Les volumes persistants
- `postgres_data` — les données de la BDD survivent aux redémarrages
- `prometheus_data` — l'historique des métriques est conservé
- `grafana_data` — les dashboards Grafana sont sauvegardés

---

## 9. Le fichier `.env`

### C'est quoi ?
Le fichier `.env` contient les **variables d'environnement** : les paramètres sensibles ou configurables (mots de passe, URLs, noms de base de données).

Il est lu automatiquement par Docker Compose.

### Variables du projet

| Variable | Rôle |
|---|---|
| `POSTGRES_DB` | Nom de la base de données |
| `POSTGRES_USER` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL |
| `CORS_ORIGINS` | Origines autorisées pour l'API (laisser vide = défaut) |
| `API_URL` | URL du backend vue depuis l'extérieur |
| `GRAFANA_USER` | Login Grafana |
| `GRAFANA_PASSWORD` | Mot de passe Grafana |
| `DATABASE_URL` | URL complète de connexion à PostgreSQL |

### Pourquoi ne pas commiter `.env` ?
Le `.env` contient des mots de passe. On ne le met jamais dans git (voir `.gitignore`). On fournit un `.env.example` comme modèle.

---

## 10. Structure des fichiers du projet

```
MSPR3/
├── backend/              ← API FastAPI (Python)
│   ├── app/              ← code source
│   ├── tests/            ← tests automatisés (91 tests)
│   ├── Dockerfile        ← recette de l'image Docker backend
│   └── requirements.txt  ← dépendances Python
│
├── dashboard/            ← Interface Streamlit (Python)
│   ├── _pages/           ← les 3 pages de l'app
│   ├── components/       ← graphiques, cartes, icônes
│   ├── services/         ← client HTTP vers le backend
│   ├── tests/            ← tests automatisés (31 tests)
│   ├── Dockerfile        ← recette de l'image Docker frontend
│   └── requirements.txt  ← dépendances Python
│
├── talend/               ← Pipeline ETL (Java compilé)
│   ├── Jobs/Jobs/        ← les 9 fichiers .jar
│   └── dump/             ← dumps SQL de la base de données
│
├── MCD_et_BDD/           ← Schéma de la base de données
├── monitoring/           ← Config Prometheus + Grafana
├── .github/workflows/    ← Pipeline CI/CD GitHub Actions
├── documentations/       ← Docs techniques PDF/MD
├── données/              ← Données brutes (GTFS, CSV)
│
├── docker-compose.yml    ← Lance toute la stack en une commande
├── Makefile              ← Raccourcis de commandes
├── .env                  ← Variables d'environnement (ne pas commiter)
├── .env.example          ← Modèle de .env à partager
└── CR.md                 ← Ce fichier
```

---

## 11. Résumé du flux de données

```
1. DONNÉES BRUTES
   CSV, JSON, GTFS (dans données/)
         ↓
2. ETL TALEND
   Lit → Nettoie → Transforme → Insère
   (talend/Jobs/Jobs/*.jar)
         ↓
3. POSTGRESQL
   8 tables, données propres et reliées
   (port 5433 en local)
         ↓
4. BACKEND FASTAPI
   Lit la BDD, expose des endpoints JSON
   http://localhost:8000
         ↓
5. DASHBOARD STREAMLIT
   Interroge le backend, affiche les graphiques
   http://localhost:8501
         ↓
6. MONITORING
   Prometheus scrute le backend → Grafana affiche
   http://localhost:3010
```

---

## 12. Les tests en détail — qui teste quoi et pourquoi

> Les tests permettent de s'assurer automatiquement que le code fonctionne correctement.
> À chaque modification du code, on relance les tests pour détecter immédiatement si quelque chose est cassé.
> Le projet contient **91 tests backend** et **31 tests dashboard**, organisés en catégories.

### Comment les tests sont organisés

Il existe 4 types de tests (marqués avec `@pytest.mark.XXX`) :

| Marqueur | Signification |
|---|---|
| `@pytest.mark.unit` | Teste une seule fonction de façon isolée, sans base de données |
| `@pytest.mark.integration` | Teste un endpoint complet avec une vraie base de données (de test) |
| `@pytest.mark.contract` | Vérifie que la forme des données retournées ne change pas |
| `@pytest.mark.quality` | Vérifie la cohérence et la qualité des données |

### Le fichier `conftest.py` — la préparation des tests

Avant chaque test, le fichier `conftest.py` prépare un environnement propre :

1. **Crée une base de données SQLite en mémoire** (une fausse base temporaire, créée et détruite à chaque test — pas la vraie PostgreSQL)
2. **Insère des données de test** (appelées "fixtures" ou "seed data") :
   - 4 pays : France, Allemagne, Italie, Autriche
   - 6 gares : Paris Nord, Paris Lyon, Berlin Hbf, München Hbf, Milano Centrale, Wien Hbf
   - 3 opérateurs : SNCF, ÖBB Nightjet, Deutsche Bahn
   - 3 lignes : Paris–Berlin (JOUR), Paris–Vienne (NUIT), Berlin–Milano (JOUR)
   - 4 trajets : SNC-1001, SNC-1002, OBB-2001, DBA-3001
   - Des itinéraires et des émissions CO₂ associées
3. **Crée un client de test FastAPI** qui appelle l'API sur ces données fictives

Cela garantit que chaque test part d'un état connu et que les tests ne se perturbent pas entre eux.

---

### BACKEND — les 8 fichiers de tests

#### `test_health.py` — Santé de l'API (3 tests)

**But** : vérifier que l'endpoint `/health` fonctionne toujours, avant même de vérifier quoi que ce soit d'autre. C'est le premier signal que le serveur est vivant.

| Test | Ce qu'il vérifie |
|---|---|
| `test_health_returns_200` | L'URL `/health` répond avec le code HTTP 200 (= succès) |
| `test_health_payload` | La réponse contient exactement `{"status": "ok"}` |
| `test_health_does_not_require_auth` | L'endpoint est accessible sans authentification (pas de header `WWW-Authenticate`) |

---

#### `test_contracts_cors.py` — Contrats d'API et sécurité CORS (7 tests)

**But** : s'assurer que la forme des réponses de l'API ne change jamais sans que les tests le signalent, et que la configuration CORS est correcte.

**C'est quoi CORS ?** Quand un navigateur web essaie d'appeler une API depuis un domaine différent (ex: le frontend sur `localhost:5173` appelle le backend sur `localhost:8000`), le navigateur exige que le serveur lui dise explicitement "oui, tu as le droit de m'appeler". C'est le mécanisme CORS.

| Test | Ce qu'il vérifie |
|---|---|
| `test_preflight_request` | Une requête `OPTIONS` (vérification préalable du navigateur) reçoit bien les headers CORS |
| `test_cors_allows_localhost_5173` | Le frontend de développement (port 5173) est autorisé à appeler le backend |
| `test_trajet_schema` | Un trajet retourné par l'API contient bien les champs `trajet_id`, `id_ligne`, `gare_depart`, `gare_arrivee`, `heure_depart`, `heure_arrivee` avec les bons types |
| `test_gare_schema` | Une gare contient bien `code_uic`, `nom_gare`, `latitude` (qui peut être null) |
| `test_count_schema` | L'endpoint de comptage retourne bien `{"total_trajets": nombre_entier}` |
| `test_repartition_schema` | La répartition JOUR/NUIT retourne bien deux clés entières `JOUR` et `NUIT` |
| `test_openapi_json_available` | La documentation JSON de l'API (`/openapi.json`) est accessible et porte le bon titre "ObRail Europe API" |
| `test_swagger_ui_available` | L'interface Swagger (`/docs`) est accessible et contient bien du HTML Swagger |

---

#### `test_data_quality.py` — Qualité et cohérence des données (10 tests)

**But** : vérifier que les données qui viennent de l'ETL Talend respectent des règles métier fondamentales. Ces tests détectent des bugs de données (doublons, valeurs aberrantes, données manquantes).

**TestInvariantsTrajets** — règles sur les trajets :

| Test | Ce qu'il vérifie | Pourquoi c'est important |
|---|---|---|
| `test_no_duplicate_trajet_ids` | Pas deux trajets avec le même `trajet_id` | Un doublon fausserait les comptages |
| `test_all_trajets_have_horaires` | Chaque trajet a une `heure_depart` et `heure_arrivee` non nulles | Un trajet sans horaire est inutilisable |
| `test_all_trajets_have_gares` | Chaque trajet a une gare de départ et d'arrivée | Un trajet sans gare n'a pas de sens |
| `test_no_circular_trajets` | La gare de départ ≠ la gare d'arrivée | Un trajet de Paris à Paris est une erreur ETL |

**TestInvariantsLignes** — règles sur les lignes :

| Test | Ce qu'il vérifie | Pourquoi c'est important |
|---|---|---|
| `test_type_service_only_jour_or_nuit` | Le `type_service` vaut uniquement `"JOUR"`, `"NUIT"` ou `null` | Toute autre valeur est une erreur de classification |

**TestInvariantsGares** — règles sur les gares :

| Test | Ce qu'il vérifie | Pourquoi c'est important |
|---|---|---|
| `test_no_duplicate_uic` | Pas deux gares avec le même `code_uic` | Le code UIC est censé être unique mondialement |
| `test_iso_pays_format` | Le code pays fait exactement 2 caractères majuscules (ex: `"FR"`, `"DE"`) | Respecte la norme ISO 3166 |
| `test_coordinates_within_europe_bounds` | Les coordonnées GPS sont dans les limites de l'Europe : latitude entre 35°N et 70°N, longitude entre -10°W et 35°E | Des coordonnées à Tokyo signifient une erreur d'injection |

---

#### `test_gares_lignes.py` — Endpoints gares et lignes (9 tests)

**But** : tester que les endpoints `/gares/` et `/lignes/` retournent les bonnes données avec la bonne structure.

**TestGares** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_200` | `/gares/` répond HTTP 200 |
| `test_returns_all_seeded_gares` | Retourne exactement 6 gares (les 6 insérées par le conftest) |
| `test_gare_has_required_fields` | Chaque gare a les champs : `code_uic`, `nom_gare`, `latitude`, `longitude`, `iso_pays` |
| `test_gares_have_iso_pays` | Les codes pays présents sont exactement FR, DE, IT, AT |

**TestLignes** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_200` | `/lignes/` répond HTTP 200 |
| `test_returns_all_seeded_lignes` | Retourne exactement 3 lignes |
| `test_ligne_has_required_fields` | Chaque ligne a : `id_ligne`, `nom_ligne`, `type_service`, `distance` |
| `test_lignes_type_service_in_jour_nuit` | Le `type_service` ne peut être que `"JOUR"`, `"NUIT"` ou `null` |
| `test_lignes_distance_is_positive` | La distance d'une ligne est toujours un nombre positif |

---

#### `test_models.py` — Modèles de données SQLAlchemy (18 tests)

**But** : vérifier que les classes Python qui représentent les tables de la BDD sont correctement définies. Ces tests ne font pas de requête HTTP — ils testent directement le code Python.

**TestModelsTableNames** — noms des tables :

| Test | Ce qu'il vérifie |
|---|---|
| `test_pays_table` | La classe `Pays` correspond à la table SQL `"pays"` |
| `test_gare_table` | La classe `Gare` correspond à `"gare"` |
| `test_operateur_table` | La classe `Operateur` correspond à `"operateur"` |
| `test_ligne_table` | La classe `Ligne` correspond à `"ligne"` |
| `test_trajet_table` | La classe `Trajet` correspond à `"trajet"` |
| `test_itineraire_table` | La classe `Itineraire` correspond à `"itineraire"` |
| `test_emission_table` | La classe `Emission` correspond à `"emission"` |

**TestModelsPrimaryKeys** — clés primaires :

| Test | Ce qu'il vérifie |
|---|---|
| `test_pays_pk_iso` | La clé primaire de `Pays` est bien `iso_pays` |
| `test_gare_pk_uic` | La clé primaire de `Gare` est bien `code_uic` |
| `test_operateur_pk_code` | La clé primaire de `Operateur` est bien `code_operateur` |
| `test_ligne_pk_id` | La clé primaire de `Ligne` est bien `id_ligne` |
| `test_trajet_pk_id` | La clé primaire de `Trajet` est bien `trajet_id` |
| `test_itineraire_composite_pk` | La clé primaire d'`Itineraire` est composite : `trajet_id` + `id_itineraire` (deux colonnes ensemble forment la clé) |

**TestModelsRelations** — liaisons entre tables :

| Test | Ce qu'il vérifie |
|---|---|
| `test_pays_has_gares` | La France a bien Paris Nord et Paris Lyon comme gares |
| `test_pays_has_operateurs` | La France a bien SNCF comme opérateur |
| `test_gare_back_to_pays` | La gare "Berlin Hbf" est bien reliée au pays "Allemagne" |
| `test_ligne_has_trajets` | La ligne 1 (Paris–Berlin) a bien les trajets SNC-1001 et SNC-1002 |
| `test_trajet_back_to_ligne` | Le trajet OBB-2001 est bien sur une ligne de type `"NUIT"` |
| `test_itineraire_links_trajet_and_gare` | OBB-2001 a bien 3 arrêts, chacun lié à une gare et au trajet |

**TestModelInstantiation** — création d'objets :

| Test | Ce qu'il vérifie |
|---|---|
| `test_pays` | On peut créer un `Pays(iso_pays="ES", nom_pays="Espagne")` et lire ses attributs |
| `test_gare_optional_coords` | Une gare peut exister sans coordonnées GPS (`latitude` et `longitude` sont `None` par défaut) |
| `test_emission_avec_distances` | Une émission peut être créée avec seulement les champs train (avion reste `None`) |

---

#### `test_services_helpers.py` — Fonctions utilitaires internes (11 tests)

**But** : tester deux fonctions internes du `trajet_service.py` qui corrigent les problèmes d'encodage des noms de gares.

**Contexte** : les données GTFS/CSV contiennent parfois des noms de villes mal encodés. Par exemple, "München" peut apparaître comme "MÃ¼nchen" (mojibake = texte encodé en UTF-8 mais lu comme latin-1). Ces fonctions les corrigent avant affichage.

**TestFixMojibake** — `_fix_mojibake()` corrige l'encodage cassé :

| Test | Ce qu'il vérifie |
|---|---|
| `test_munchen_double_encoded` | `"MÃ¼nchen"` → `"München"` (cas réel rencontré dans les données) |
| `test_unrecoverable_mojibake_returns_input` | Si la correction est impossible, retourne la chaîne originale sans planter |
| `test_already_clean_string` | `"Paris Nord"` → `"Paris Nord"` (rien à corriger) |
| `test_empty_string` | Une chaîne vide reste vide |
| `test_none` | `None` reste `None` (pas de crash) |

**TestNormalizeName** — `_normalize_name()` normalise pour la recherche/comparaison :

| Test | Ce qu'il vérifie |
|---|---|
| `test_lowercase` | `"Paris Nord"` → `"paris nord"` (tout en minuscules) |
| `test_strip_accents` | `"München"` → `"munchen"` (supprime les accents) |
| `test_strip_whitespace` | `"  Paris Nord  "` → `"paris nord"` (supprime les espaces en trop) |
| `test_mojibake_then_normalize` | `"MÃ¼nchen"`, `"München"` et `"Munchen"` donnent tous le même résultat normalisé — ce qui permet de les comparer |
| `test_empty` | Chaîne vide → chaîne vide |
| `test_none` | `None` → `""` (chaîne vide, pas de crash) |

---

#### `test_stats.py` — Endpoints de statistiques (18 tests)

**But** : vérifier que tous les calculs et agrégations de l'API renvoient des valeurs correctes par rapport aux données de test.

**TestKPICounts** — comptages globaux :

| Test | Ce qu'il vérifie |
|---|---|
| `test_count_trajets` | `/stats/trajets/count` retourne `{"total_trajets": 4}` (il y a 4 trajets dans les données de test) |
| `test_count_lignes` | `/stats/lignes/count` retourne `{"total_lignes": 3}` |
| `test_count_gares` | `/stats/gares/count` retourne `{"total_gares": 6}` |
| `test_count_pays` | `/stats/pays/count` retourne `{"total_pays": 4}` |

**TestRepartitionJourNuit** — répartition des trains de jour vs nuit :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_jour_nuit_keys` | La réponse contient bien les clés `"JOUR"` et `"NUIT"` |
| `test_jour_count` | Il y a 3 trajets de jour (SNC-1001, SNC-1002, DBA-3001) |
| `test_nuit_count` | Il y a 1 trajet de nuit (OBB-2001, ligne Paris–Vienne sleeper) |
| `test_total_matches_trajets_count` | JOUR + NUIT = 4 (cohérence avec le total des trajets) |

**TestStatsOperateurs** — statistiques par opérateur :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_list` | La réponse est une liste |
| `test_each_operateur_has_count` | Chaque élément de la liste a les champs `"operateur"` (texte) et `"trajets"` (entier) |
| `test_sncf_has_2_trajets` | SNCF apparaît dans la liste avec 2 trajets (SNC-1001 et SNC-1002) |
| `test_total_par_operateur_matches_trajets` | La somme des trajets de tous les opérateurs = 4 |

**TestStatsEmissions** — statistiques CO₂ :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_train_avion` | La réponse contient les clés `"train"` et `"avion"` |
| `test_train_lower_than_avion` | L'empreinte CO₂ du train est inférieure à celle de l'avion (vrai physiquement) |

**TestTrajetsMap** — données pour la carte :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_list` | La réponse est une liste de segments |
| `test_segments_have_coordinates` | Chaque segment a les 4 coordonnées : `lat_depart`, `lon_depart`, `lat_arrivee`, `lon_arrivee` |
| `test_obb_2001_produces_2_segments` | Le trajet OBB-2001 avec 3 arrêts génère au moins 2 segments de carte (Paris→München, München→Wien) |
| `test_segments_have_valid_lat_lon` | Les latitudes sont entre -90 et 90, les longitudes entre -180 et 180 |

---

#### `test_trajets.py` — Endpoints trajets (12 tests)

**But** : tester les 3 endpoints dédiés aux trajets : liste, détail, et itinéraire.

**TestTrajetsListe** — liste complète :

| Test | Ce qu'il vérifie |
|---|---|
| `test_get_all_returns_200` | `/trajets/` répond HTTP 200 |
| `test_get_all_returns_list` | Retourne une liste de 4 trajets |
| `test_trajet_has_required_fields` | Chaque trajet contient : `trajet_id`, `id_ligne`, `gare_depart`, `gare_arrivee`, `heure_depart`, `heure_arrivee` |
| `test_all_trajet_ids_are_unique` | Pas de doublon dans les identifiants retournés |

**TestTrajetDetail** — détail d'un trajet :

| Test | Ce qu'il vérifie |
|---|---|
| `test_get_existing_trajet` | `/trajets/SNC-1001` retourne le bon trajet avec `gare_depart="Paris Nord"` et `gare_arrivee="Berlin Hbf"` |
| `test_get_nonexistent_returns_404` | `/trajets/UNKNOWN-9999` retourne HTTP 404 avec le message `"Trajet not found"` |
| `test_get_trajet_returns_id_ligne` | Le trajet OBB-2001 est bien sur la ligne 2 |

**TestTrajetItineraire** — arrêts intermédiaires :

| Test | Ce qu'il vérifie |
|---|---|
| `test_itineraire_returns_ordered_gares` | `/trajets/OBB-2001/itineraire` retourne 3 gares dans l'ordre : Paris Lyon → München Hbf → Wien Hbf |
| `test_itineraire_includes_coordinates` | Le premier arrêt a des coordonnées GPS non nulles |
| `test_itineraire_includes_uic_and_iso` | Chaque arrêt contient son `code_uic` et son `iso_pays` |
| `test_itineraire_for_nonexistent_returns_404` | Un itinéraire d'un trajet inconnu retourne HTTP 404 |
| `test_itineraire_supports_slash_in_id` | Un `trajet_id` contenant un slash et un espace (`"CFR 78/1743"`) fonctionne correctement — cas réel trouvé dans les données GTFS |

---

### DASHBOARD — les 3 fichiers de tests

#### `test_api_service.py` — Client HTTP du dashboard (13 tests)

**But** : vérifier que le code Python du dashboard qui appelle le backend se comporte correctement, même quand le backend est indisponible ou retourne des erreurs.

**Technique utilisée** : les tests "mockent" (simulent) le backend avec `unittest.mock.patch`. Le vrai backend n'est pas lancé — on intercepte les appels HTTP et on retourne des réponses fictives.

**TestGetTrajets** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_calls_correct_url` | La fonction `get_trajets()` appelle bien `http://test-api:8000/trajets` avec un timeout de 10s |
| `test_returns_json` | La fonction retourne le JSON reçu du backend |

**TestGetTrajetItineraire** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_url_encodes_special_chars` | L'ID `"CFR 78/1743"` est URL-encodé en `"CFR%2078%2F1743"` dans l'URL (sinon le serveur ne comprend pas) |
| `test_returns_empty_list_on_404` | Si le backend répond 404, la fonction retourne `[]` au lieu de planter |
| `test_returns_empty_list_on_exception` | Si le réseau coupe (exception Python), la fonction retourne `[]` — le dashboard ne crashe pas |

**TestStatsEndpoints** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_get_trajets_count` | `get_trajets_count()` appelle le bon endpoint et retourne le JSON |
| `test_get_emissions` | `get_emissions()` retourne bien `{"train": 4.5, "avion": 185.0}` |

**TestGetOperateurs** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_list_when_200` | Si le backend répond 200, retourne la liste des opérateurs |
| `test_returns_empty_when_non_200` | Si le backend répond 500 (erreur serveur), retourne `[]` |
| `test_returns_empty_on_invalid_json` | Si le JSON est invalide, retourne `[]` sans planter le dashboard |

**TestGetTrajetsMap** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_uses_longer_timeout` | `get_trajets_map()` utilise un timeout d'au moins 15s (données volumineuses) |
| `test_returns_empty_on_500` | Retourne `[]` si le backend est en erreur |

**TestPing** :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_dict_with_ok_and_latency` | `ping()` retourne `{"ok": True, "latency_ms": X}` avec la latence en millisecondes |
| `test_handles_exception` | Si la connexion échoue, retourne `{"ok": False}` sans planter |

---

#### `test_charts.py` — Graphiques Plotly (11 tests)

**But** : vérifier que les fonctions qui génèrent les graphiques créent bien un objet graphique valide, même avec des données vides ou à zéro.

**TestJourNuitChart** — graphique en donut JOUR/NUIT :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_figure` | `trajets_jour_nuit_chart(300, 110)` retourne un objet `go.Figure` (graphique Plotly) |
| `test_has_donut_hole` | Le graphique est bien un donut (trou au centre, `hole > 0`) |
| `test_handles_zero_values` | Fonctionne avec `jour=0, nuit=0` sans crash |
| `test_labels_are_jour_nuit` | Les étiquettes sont `("Jour", "Nuit")` |

**TestCO2Chart** — graphique d'émissions CO₂ :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_figure` | `co2_chart({"train": 4.5, "avion": 185.0})` retourne un graphique |
| `test_handles_none_values` | Fonctionne si train et avion sont `None` (données manquantes) |

**TestOperateursChart** — graphique par opérateur :

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_figure_with_data` | Génère un graphique à partir d'une liste d'opérateurs |
| `test_handles_empty_list` | Fonctionne avec une liste vide |

**TestPaysBarChart** — graphique par pays :

| Test | Ce qu'il vérifie |
|---|---|
| `test_with_pandas_series` | Génère un graphique depuis un `pd.Series` (ex: `{"FR": 50, "DE": 30}`) |
| `test_with_empty_series` | Fonctionne avec une série vide |

**TestLatencyChart** — graphique de latence (page supervision) :

| Test | Ce qu'il vérifie |
|---|---|
| `test_with_history` | Génère un graphique depuis un historique de mesures `{ts, latency_ms, ok}` |
| `test_with_empty_history` | Fonctionne avec un historique vide |

---

#### `test_icons.py` — Composant d'icônes (5 tests)

**But** : vérifier que la fonction `lucide()` qui génère des icônes SVG fonctionne correctement.

| Test | Ce qu'il vérifie |
|---|---|
| `test_returns_svg_string` | `lucide("train")` retourne un `str` contenant `<svg>...</svg>` |
| `test_default_size` | Par défaut, l'icône fait 20×20 pixels |
| `test_custom_size` | `lucide("train", size=32)` génère une icône de 32×32 pixels |
| `test_custom_color` | `lucide("train", color="#ff0000")` inclut la couleur rouge dans le SVG |
| `test_unknown_icon_falls_back_gracefully` | Une icône inconnue ne fait pas planter le dashboard — elle retourne quand même un `str` |

---

### Résumé des tests

| Fichier | Nb tests | Type principal | Ce qu'il protège |
|---|---|---|---|
| `test_health.py` | 3 | integration | Le serveur répond |
| `test_contracts_cors.py` | 8 | contract | La forme des réponses + sécurité CORS |
| `test_data_quality.py` | 10 | quality | La cohérence des données ETL |
| `test_gares_lignes.py` | 9 | integration | Les endpoints `/gares/` et `/lignes/` |
| `test_models.py` | 18 | unit | Les classes Python des tables BDD |
| `test_services_helpers.py` | 11 | unit | Les fonctions d'encodage des noms |
| `test_stats.py` | 18 | integration | Tous les calculs statistiques |
| `test_trajets.py` | 12 | integration | Les endpoints trajets + cas limites |
| `test_api_service.py` | 13 | api | Le client HTTP du dashboard |
| `test_charts.py` | 11 | charts | La génération des graphiques Plotly |
| `test_icons.py` | 5 | unit | Le composant d'icônes SVG |
| **Total** | **118** | | |

---

## 13. Glossaire pour débutants

| Terme | Définition simple |
|---|---|
| **API REST** | Serveur qui répond à des requêtes HTTP en retournant du JSON |
| **endpoint** | Une URL précise de l'API (ex: `/gares`) |
| **JSON** | Format de données texte lisible par les machines (et les humains) |
| **ORM** | Bibliothèque qui traduit du Python en SQL automatiquement |
| **Docker** | Technologie pour empaqueter une app dans un container portable |
| **Container** | Boîte isolée qui contient une app et tout ce dont elle a besoin |
| **CI/CD** | Pipeline automatique qui teste et déploie le code à chaque push |
| **pytest** | Framework de tests Python |
| **linter (ruff)** | Outil qui vérifie que le code respecte les conventions de style |
| **ETL** | Extract Transform Load — pipeline de traitement de données |
| **GTFS** | Format standard de données de transport public |
| **Prometheus** | Outil de collecte de métriques (performances, erreurs…) |
| **Grafana** | Interface pour visualiser les métriques sous forme de graphs |
| **SHA** | Identifiant unique d'un commit Git |
| **MCD** | Modèle Conceptuel de Données — schéma des tables et relations |
