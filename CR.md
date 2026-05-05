# RAPPORT TECHNIQUE

## ObRail Europe

### Mise en production d'une solution d'intelligence artificielle

Référence : MSPR TPRE532 Bloc E6.3

Certification : Professionnelle Développeur en Intelligence Artificielle et Data Science RNCP36581

Membres du groupe : Kouamé Johan BILÉ, Joseph HACCANDY, Glody KUTUMBAKANA, Nabil DIA

Date de soutenance : à remplir

---

# CHAPITRE 1 : INTRODUCTION

## 1.1 Contexte du projet

ObRail Europe est un observatoire indépendant fondé en 2018, dont la mission principale est d'analyser les flux ferroviaires à l'échelle du continent européen et de promouvoir la mobilité durable. L'organisation travaille en étroite collaboration avec les institutions européennes, notamment la Commission européenne et le Parlement européen, ainsi qu'avec des organisations non gouvernementales spécialisées dans la transition écologique des transports, comme Transport et Environnement et Back-on-Track. Elle entretient également des partenariats avec les grands opérateurs ferroviaires du continent, parmi lesquels la SNCF, ÖBB Nightjet ou encore Deutsche Bahn.

Le projet s'inscrit dans deux cadres stratégiques européens majeurs. D'une part, il répond aux objectifs du Pacte Vert européen, connu sous le nom de Green Deal, qui vise à réduire de 55 % les émissions de gaz à effet de serre d'ici 2030 et à décarboner le secteur des transports. D'autre part, il s'articule avec le programme TEN-T, le réseau transeuropéen de transport, qui cherche à renforcer les liaisons ferroviaires entre les pays membres de l'Union européenne.

Dans ce contexte, la question centrale posée par ObRail Europe est celle de la contribution respective des trains de jour et des trains de nuit à une mobilité interurbaine durable à l'échelle continentale. Les trains de nuit, en particulier, connaissent un regain d'intérêt depuis plusieurs années, car ils permettent de relier des métropoles éloignées sans recourir à l'avion, tout en limitant significativement les émissions de carbone. Comprendre leur répartition géographique, leur empreinte environnementale comparée à celle de l'avion et la manière dont les opérateurs les déploient est devenu un enjeu de politique publique.

## 1.2 Problématique

Pour répondre à ces questions, ObRail Europe se heurte à un ensemble de contraintes techniques majeures. Premièrement, les données ferroviaires européennes sont extrêmement dispersées : elles proviennent de sources hétérogènes telles que des fichiers CSV issus d'OpenStreetMap, des fichiers JSON publiés par Back-on-Track, des flux GTFS (General Transit Feed Specification, le format standard des données de transport public) fournis par la SNCF, ou encore des fichiers Excel internes. Chaque opérateur publie ses données dans son propre format, sans référentiel commun entre les pays.

Deuxièmement, la qualité de ces données est inégale : on y trouve des doublons, des codes UIC manquants, des fuseaux horaires incohérents et des noms de villes parfois mal encodés. Troisièmement, il n'existe pas de standard transfrontalier permettant d'harmoniser les informations d'un pays à l'autre. Quatrièmement, le traitement de ces données doit respecter le Règlement Général sur la Protection des Données, le RGPD, qui impose une transparence totale sur les traitements effectués. Cinquièmement, le projet est soumis à une contrainte temporelle forte, les résultats devant être disponibles avant la fin de l'année pour alimenter les travaux du Parlement européen.

À cela s'ajoute une contrainte héritée du projet précédent, le MSPR2 : un prototype fonctionnel avait été livré, reposant sur une base de données PostgreSQL et une API REST. Mais ce prototype présentait des limites importantes : son déploiement était entièrement manuel, aucun test automatisé n'était en place, et il n'existait aucun mécanisme de supervision pour détecter les incidents. En somme, le prototype fonctionnait dans un environnement contrôlé, mais il n'était pas industrialisable.

La problématique de ce MSPR3 peut donc se formuler ainsi : comment passer d'un prototype fonctionnel à une application web industrialisée, testée de façon exhaustive, supervisée en temps réel, et capable d'accueillir un futur modèle d'intelligence artificielle ?

## 1.3 Objectifs opérationnels

Pour répondre à cette problématique, le groupe s'est fixé sept objectifs opérationnels clairs. Le premier est l'industrialisation de la stack technique grâce à Docker et Docker Compose, afin d'assurer une reproductibilité totale de l'environnement sur n'importe quelle machine. Le deuxième est la création d'une interface professionnelle respectant les exigences du Référentiel Général d'Amélioration de l'Accessibilité, le RGAA, niveau AA. Le troisième est la mise en place d'une stratégie de tests complète, couvrant les tests unitaires, d'intégration, de contrat, de qualité et de bout en bout. Le quatrième est l'automatisation de l'intégration et de la livraison continues via GitHub Actions. Le cinquième est l'instrumentation du backend avec Prometheus et Grafana pour superviser les performances en temps réel. Le sixième est la mise en conformité réglementaire, en particulier sur le plan de la sécurité et du RGPD. Le septième, enfin, est la rédaction d'un rapport technique complet documentant l'ensemble des choix effectués.

## 1.4 Organisation du rapport

Ce rapport suit la structure logique du projet, en partant des fondations techniques pour remonter jusqu'aux couches supérieures. Il commence par la base de données et le pipeline ETL, puis décrit le backend et le frontend, avant d'aborder la stratégie de tests et l'intégration continue, le monitoring, le déploiement et enfin la conclusion, qui met en perspective les compétences couvertes et les évolutions possibles vers l'intelligence artificielle.

## 1.5 Structure du projet

```
MSPR3/
├── backend/                              API REST FastAPI
│   ├── app/
│   │   ├── main.py                       Point d'entrée, middlewares, rate limiting, Prometheus
│   │   ├── database.py                   Connexion SQLAlchemy, SessionLocal
│   │   ├── models/                       Classes ORM des 8 tables
│   │   │   ├── pays.py
│   │   │   ├── gare.py
│   │   │   ├── operateur.py
│   │   │   ├── ligne.py
│   │   │   ├── type_train.py
│   │   │   ├── trajet.py
│   │   │   ├── itineraire.py
│   │   │   └── emission.py
│   │   ├── schemas/                      Schémas Pydantic (validation requête/réponse)
│   │   │   ├── gare_schema.py
│   │   │   ├── ligne_schema.py
│   │   │   ├── trajet_schema.py
│   │   │   ├── itineraire_schema.py
│   │   │   ├── emission_schema.py
│   │   │   ├── operateur_schema.py
│   │   │   ├── pays_schema.py
│   │   │   └── type_train_schema.py
│   │   ├── routes/                       Endpoints FastAPI (5 fichiers)
│   │   │   ├── health_routes.py
│   │   │   ├── trajet_routes.py
│   │   │   ├── gare_routes.py
│   │   │   ├── ligne_routes.py
│   │   │   └── stats_routes.py
│   │   └── services/                     Logique métier et requêtes SQL
│   │       ├── trajet_service.py
│   │       ├── gare_service.py
│   │       ├── ligne_service.py
│   │       └── stats_service.py
│   ├── tests/                            91 tests pytest (8 fichiers)
│   │   ├── conftest.py                   Base SQLite en mémoire + données de test
│   │   ├── test_health.py
│   │   ├── test_contracts_cors.py
│   │   ├── test_data_quality.py
│   │   ├── test_gares_lignes.py
│   │   ├── test_models.py
│   │   ├── test_services_helpers.py
│   │   ├── test_stats.py
│   │   └── test_trajets.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                            Tableau de bord Streamlit
│   ├── app.py                            Point d'entrée, navigation, styles RGAA
│   ├── _pages/                           3 pages fonctionnelles
│   │   ├── trajets.py
│   │   ├── observatoire.py
│   │   └── supervision.py
│   ├── components/                       Composants réutilisables
│   │   ├── charts.py                     Graphiques Plotly
│   │   ├── map.py                        Cartes Folium
│   │   └── icons.py                      Icônes SVG
│   ├── config/
│   │   └── api_config.py                 URLs et constantes
│   ├── services/
│   │   └── api_service.py                Client HTTP backend + requêtes Prometheus
│   ├── tests/                            31 tests pytest (3 fichiers)
│   │   ├── conftest.py
│   │   ├── test_api_service.py
│   │   ├── test_charts.py
│   │   └── test_icons.py
│   ├── tests_e2e/                        6 tests Playwright (2 fichiers)
│   │   ├── conftest.py
│   │   ├── test_navigation.py
│   │   └── test_accessibility.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── monitoring/                           Configuration Prometheus + Grafana
│   ├── prometheus.yml                    Scraping toutes les 15s
│   └── grafana/
│       ├── dashboards/
│       │   ├── dashboards.yml            Provisioning automatique
│       │   └── fastapi-observability.json Dashboard 6 panels
│       └── datasources/
│           └── prometheus.yml            UID fixe : obrail-prometheus
│
├── talend/                               Pipeline ETL
│   ├── Jobs/Jobs/                        9 jobs compilés (.jar)
│   │   ├── pays/
│   │   ├── gare/
│   │   ├── operateur/
│   │   ├── type_train/
│   │   ├── ligne/
│   │   ├── trajet/
│   │   ├── exploite/
│   │   ├── itineraire/
│   │   └── emission/
│   ├── dump/
│   │   └── mspr2_dump_2026-04-22.sql     Données préchargées au démarrage Docker
│   ├── execution_etl/
│   │   └── activation.sh                 Lancement ETL Linux
│   ├── lancement/
│   │   ├── lancement.sh
│   │   └── lancement.bat
│   └── planication/
│       └── planification.sh              Cron mensuel Linux
│
├── MCD_et_BDD/                           Schéma de la base de données
│   ├── MCDFinal.jpg
│   ├── mspr.sql
│   └── requetes_verification.sql
│
├── .github/
│   └── workflows/
│       └── main.yml                      Pipeline CI/CD (9 jobs)
│
├── docker-compose.yml                    Orchestration des 5 services
├── Makefile                              Raccourcis de commandes
├── .env.example                          Template variables d'environnement
├── why.md                                Journal des décisions techniques
├── LANCEMENT.md                          Guide de démarrage
└── README.md                             Documentation principale
```

---

# CHAPITRE 2 : BASE DE DONNÉES

## 2.1 Modèle conceptuel

La base de données constitue le socle de toute l'application. Elle est structurée autour de onze tables organisées en trois couches logiques. La première couche, dite couche référentiel, regroupe les données de structure du réseau ferroviaire : la table pays stocke les vingt-six pays européens identifiés par leur code ISO à deux lettres, comme FR pour la France ou DE pour l'Allemagne. La table gare recense toutes les gares du réseau avec leur nom, leurs coordonnées GPS et leur appartenance à un pays. La table operateur liste les compagnies ferroviaires. La table ligne décrit les lignes ferroviaires avec leur nom, leur distance et leur type, qui peut être JOUR ou NUIT. La table type_train référence les catégories de matériel roulant. La table source assure la traçabilité des imports ETL en enregistrant l'URL, le format et le volume de chaque source.

La deuxième couche, dite couche exploitation, couvre les circulations réelles. La table trajet représente un aller simple entre une gare de départ et une gare d'arrivée, avec les horaires de départ et d'arrivée stockés au format texte HH:mm:ss. La table itineraire détaille les arrêts intermédiaires de chaque trajet, ordonnés par leur rang de passage et rattachés à leurs coordonnées géographiques via le code UIC de chaque gare.

La troisième couche, la couche analyse, contient une unique table emission qui stocke l'empreinte carbone de chaque trajet, à la fois pour le train et pour l'avion. Deux tables d'association complètent ce modèle : la table exploite lie les opérateurs aux lignes qu'ils exploitent, et la table utilisation associe les opérateurs aux types de matériel roulant qu'ils emploient.

Les clés primaires suivent des logiques différentes selon les tables : la table pays utilise le code ISO à deux caractères comme clé naturelle, la table gare utilise le code UIC à sept chiffres, la table trajet utilise un identifiant alphanumérique issu des données sources, et la table itineraire utilise une clé composite formée de l'identifiant du trajet et du rang de l'arrêt.

## 2.2 Choix de PostgreSQL

Le choix du système de gestion de base de données s'est porté sur PostgreSQL plutôt que sur ses concurrents pour plusieurs raisons complémentaires. Par rapport à MySQL, PostgreSQL offre un meilleur support des contraintes d'intégrité référentielle et une conformité plus stricte au standard SQL, ce qui garantit la cohérence des relations entre les onze tables. Par rapport à SQLite, PostgreSQL gère nativement la concurrence d'accès, ce qui est indispensable dès lors que plusieurs services Docker lisent simultanément la même base. Par rapport à MongoDB, un système de base de données orientée documents, PostgreSQL impose un schéma relationnel strict qui correspond exactement à la nature des données ferroviaires, dans lesquelles chaque trajet appartient à une ligne, chaque ligne est exploitée par un opérateur, et chaque gare est localisée dans un pays. Enfin, PostgreSQL est le système de gestion de base de données de référence pour la bibliothèque SQLAlchemy que nous utilisons dans le backend, et il satisfait pleinement aux exigences de conformité ACID, acronyme désignant les propriétés d'Atomicité, Cohérence, Isolation et Durabilité des transactions.

## 2.3 ETL Talend

L'ETL, acronyme d'Extract Transform Load désignant le pipeline de traitement des données, est orchestré avec Talend Open Studio for Data Integration. Talend lit les sources brutes, les nettoie, les transforme et les insère dans PostgreSQL via des connecteurs JDBC, le protocole standard de connexion Java aux bases de données.

Les sources de données mobilisées sont au nombre de trois principales. Le fichier stations.csv issu d'OpenStreetMap fournit les gares avec leurs coordonnées géographiques. Le fichier trips.json publié par Back-on-Track contient les trajets ferroviaires européens, notamment les trains de nuit, avec les informations d'opérateurs, de lignes, d'itinéraires et d'émissions de CO2. Les fichiers GTFS de la SNCF, au format ZIP contenant des fichiers CSV, fournissent les catégories de matériel roulant.

Le choix de Talend s'explique par sa capacité à traiter simultanément des formats multi-sources très hétérogènes, par sa traçabilité graphique qui permet de visualiser et de documenter chaque étape de transformation, et par le fait que les jobs compilés sous forme de fichiers JAR sont réutilisables sans dépendance à l'environnement de développement.

Le pipeline Talend est composé de neuf jobs exécutés dans un ordre précis qui respecte les dépendances entre tables. Le premier job charge la table pays à partir des codes ISO. Le deuxième charge les gares depuis le fichier stations.csv. Le troisième charge les opérateurs ferroviaires. Le quatrième charge les types de matériel roulant depuis les données GTFS. Le cinquième charge les lignes. Le sixième charge les trajets. Le septième, le job exploite, établit les liens entre opérateurs et lignes. Le huitième charge les itinéraires, c'est-à-dire les arrêts intermédiaires. Le neuvième, enfin, calcule et insère les émissions de CO2.

Le calcul de l'empreinte carbone de l'avion suit la formule suivante : l'empreinte en kilogrammes est égale à la distance en kilomètres multipliée par le facteur d'émission 0,158 kilogramme de CO2 équivalent par passager et par kilomètre. Ce facteur est issu des référentiels de l'ADEME, l'Agence de la transition écologique française, et du BEIS, le département britannique équivalent. L'empreinte carbone du train, quant à elle, est directement lue depuis le champ emissions_co2e du fichier trips.json fourni par Back-on-Track.

## 2.4 Flux de données

Le flux de données suit une chaîne linéaire et déterministe. Les sources brutes, qu'il s'agisse de CSV, de JSON ou de fichiers GTFS, sont lues par les neuf jobs Talend qui effectuent l'extraction, le nettoyage, le mapping et la validation de chaque enregistrement avant son insertion dans PostgreSQL. Ce processus aboutit à une base relationnelle propre, déduplicatée et cohérente, qui constitue la seule source de vérité pour le reste de l'application. Au premier démarrage de Docker, la base est préchargée automatiquement depuis le dump SQL versé dans le dépôt, ce qui évite de devoir relancer l'ETL complet à chaque déploiement.

## 2.5 Conformité RGPD

Le projet ne traite aucune donnée à caractère personnel. Toutes les données utilisées proviennent de l'open data public : les horaires de trains, les coordonnées des gares et les émissions de CO2 sont des informations publiques qui ne permettent pas d'identifier un individu. Plusieurs mesures techniques renforcent néanmoins la conformité réglementaire. Les journaux applicatifs ne contiennent aucune adresse IP d'utilisateur. Les secrets de connexion à la base de données, comme les mots de passe, ne sont jamais versionnés dans le dépôt Git mais sont gérés via un fichier d'environnement non versionné et via les GitHub Secrets pour le pipeline CI/CD. L'historique des métriques Prometheus est limité à trente jours par paramétrage explicite, ce qui évite l'accumulation indéfinie de données. Enfin, un fichier d'exemple documenté est fourni pour permettre à tout nouveau contributeur de configurer son environnement sans accéder aux vraies credentials.

---

# CHAPITRE 3 : BACKEND

## 3.1 Architecture technique

Le backend est une API REST, c'est-à-dire un serveur qui reçoit des requêtes HTTP et répond avec des données au format JSON. Son code est organisé en couches séparées dont chacune a une responsabilité précise.

Le fichier main.py est le point d'entrée de l'application. C'est lui qui instancie le framework FastAPI, enregistre les middlewares de sécurité, active le rate limiting et connecte l'instrumentation Prometheus. Le fichier database.py gère la connexion à PostgreSQL via SQLAlchemy et fournit une factory de sessions de base de données. Le dossier models regroupe les classes Python qui représentent les onze tables de la base de données : chaque colonne SQL est modélisée comme un attribut Python typé. Le dossier schemas contient les schémas de validation Pydantic, qui définissent la forme exacte que doivent avoir les données entrantes et sortantes. Le dossier routes définit les endpoints de l'API, regroupés par domaine fonctionnel en cinq fichiers. Enfin, le dossier services contient la logique métier, notamment les requêtes SQL complexes et les fonctions de normalisation des noms de gares.

## 3.2 Choix techniques

Le choix de Python comme langage principal est naturel dans un projet de data science : son écosystème est le plus riche du domaine, avec des bibliothèques matures pour la manipulation de données, la validation et la création d'API.

Le choix de FastAPI comme framework d'API plutôt que Flask s'explique par deux avantages décisifs. D'une part, FastAPI génère automatiquement une documentation Swagger interactive à partir des annotations Python, ce qui évite de maintenir une documentation séparée qui peut diverger du code. D'autre part, FastAPI intègre nativement Pydantic pour la validation des données, ce qui permet de détecter immédiatement les erreurs de format avant même que la logique métier soit exécutée.

SQLAlchemy est utilisé comme ORM, c'est-à-dire comme traducteur automatique entre les objets Python et les requêtes SQL. C'est le standard de facto pour Python, et il prend en charge les relations complexes entre tables telles que celles de notre modèle.

Pydantic assure le typage fort et la validation des réponses, garantissant que les données envoyées au frontend sont toujours dans le format attendu. Uvicorn sert de serveur ASGI, un protocole asynchrone plus performant que le WSGI traditionnel, et il supporte les workers multiples pour gérer la concurrence.

## 3.3 Endpoints de l'API

L'API expose treize endpoints couvrant l'ensemble des besoins du dashboard et de la supervision. L'endpoint GET /health retourne simplement l'état de santé du serveur sous la forme d'un objet JSON confirmant que l'API répond. L'endpoint GET /metrics expose les métriques de performance au format texte que Prometheus scrute toutes les quinze secondes. L'endpoint GET /trajets retourne la liste de tous les trajets disponibles. L'endpoint GET /trajets/{id} retourne le détail d'un trajet précis identifié par son identifiant. L'endpoint GET /trajets/{id}/itineraire retourne les arrêts intermédiaires ordonnés d'un trajet donné. L'endpoint GET /gares retourne la liste de toutes les gares avec leurs coordonnées GPS. L'endpoint GET /lignes retourne la liste de toutes les lignes ferroviaires avec leur type jour ou nuit.

Du côté des statistiques, l'endpoint GET /stats/trajets/count retourne le nombre total de trajets. L'endpoint GET /stats/trajets/type retourne la répartition entre trains de jour et trains de nuit. L'endpoint GET /stats/emissions retourne l'empreinte carbone moyenne d'un trajet en train comparée à l'avion. L'endpoint GET /stats/operateurs retourne le volume de trajets par opérateur ferroviaire. L'endpoint GET /stats/trajets/map retourne les segments géographiques nécessaires au tracé de la carte du réseau. Enfin, l'endpoint GET /docs donne accès à la documentation interactive Swagger générée automatiquement.

Les endpoints /trajets et tous les endpoints /stats sont soumis à un rate limiting, c'est-à-dire une limitation du débit de requêtes.

## 3.4 Sécurité

Deux mécanismes de sécurité sont implémentés directement dans main.py. Le premier est le rate limiting, mis en œuvre grâce à la bibliothèque slowapi. Il limite à soixante requêtes par minute et par adresse IP l'accès aux endpoints /trajets et /stats. Lorsque cette limite est dépassée, l'API répond avec le code HTTP 429, qui signifie "Trop de requêtes", accompagné d'un message invitant à réessayer dans soixante secondes. Ce mécanisme protège l'API contre le scraping massif automatisé.

Le second mécanisme est l'injection automatique de quatre headers de sécurité HTTP dans chaque réponse de l'API. Le header X-Content-Type-Options avec la valeur nosniff empêche les navigateurs de deviner le type d'un fichier, ce qui bloque un vecteur d'attaque dit de MIME sniffing. Le header X-Frame-Options avec la valeur DENY interdit l'intégration de l'API dans une iframe, ce qui protège contre le clickjacking, une attaque consistant à superposer un contenu frauduleux sur l'interface légitime. Le header X-XSS-Protection active le filtre de protection contre les injections de scripts des anciens navigateurs. Le header Referrer-Policy contrôle quelles informations de provenance sont transmises lors des requêtes cross-origin.

## 3.5 Documentation automatique

FastAPI génère automatiquement une interface Swagger UI accessible à l'adresse /docs. Cette interface, toujours synchronisée avec le code source, permet de tester directement chaque endpoint depuis le navigateur, de visualiser les schémas de données attendus et retournés, et de comprendre le comportement de l'API sans lire le code source. C'est un avantage considérable pour l'intégration avec les partenaires d'ObRail Europe et pour les tests manuels pendant le développement.

---

# CHAPITRE 4 : FRONTEND

## 4.1 Architecture technique

Le frontend est un tableau de bord analytique développé avec Streamlit, un framework Python qui génère automatiquement des interfaces web sans écrire de HTML, de CSS ni de JavaScript. Son organisation suit une séparation claire entre les responsabilités.

Le fichier app.py est le point d'entrée de l'application. Il initialise Streamlit, définit la barre de navigation entre les pages et injecte les styles globaux, notamment les variables CSS de couleur et les règles d'accessibilité. Le dossier pages contient les trois pages fonctionnelles de l'application. Le dossier components regroupe les composants réutilisables : charts.py génère les graphiques Plotly, map.py génère les cartes interactives Folium, et icons.py encapsule les icônes vectorielles SVG. Enfin, le dossier services contient api_service.py, le client HTTP centralisé qui regroupe tous les appels vers le backend et vers Prometheus.

## 4.2 Choix techniques

Streamlit a été choisi pour sa capacité à produire rapidement des interfaces analytiques interactives sans nécessiter de compétences en développement web front-end. Son intégration native avec Pandas pour la manipulation des données, Plotly pour les graphiques et Folium pour les cartes géographiques en fait l'outil idéal pour un projet de data science. Il inclut son propre serveur web, ce qui simplifie le déploiement Docker.

Ce choix présente cependant une contrepartie importante : Streamlit génère le HTML de façon automatique, ce qui limite le contrôle sur les attributs d'accessibilité comme les attributs aria. Cette limitation a été identifiée, documentée, et des mesures palliatives ont été mises en place, comme expliqué dans la section suivante.

Plotly a été retenu pour ses graphiques interactifs en Python, permettant aux utilisateurs de zoomer, de filtrer et d'inspecter les valeurs directement dans le navigateur. Folium permet de générer des cartes Leaflet interactives depuis Python, idéales pour visualiser les tracés des trajets ferroviaires sur une carte de l'Europe. Pandas assure la manipulation des données reçues de l'API avant leur affichage.

## 4.3 Les trois pages du tableau de bord

La page Trajets est la page d'exploration détaillée du réseau. Elle propose des filtres permettant de sélectionner les trajets par pays, par opérateur et par type de service jour ou nuit. Elle affiche une carte interactive Folium qui trace le tracé géographique du trajet sélectionné, ses horaires de départ et d'arrivée, un graphique comparant les émissions de CO2 du train et de l'avion pour ce même trajet, ainsi que la liste ordonnée des arrêts intermédiaires de l'itinéraire.

La page Observatoire est la vue d'ensemble synthétique destinée aux décideurs et aux partenaires institutionnels. Elle affiche en tête de page quatre indicateurs clés : le nombre total de trajets, le nombre de gares couvertes, le nombre de pays, et l'empreinte carbone moyenne comparée train versus avion. Elle présente ensuite un graphique en anneau montrant la répartition entre trains de jour et trains de nuit, un graphique à barres comparant les émissions de CO2 des deux modes de transport, et un histogramme représentant le volume de trajets par opérateur ferroviaire.

La page Supervision est dédiée au suivi technique de l'état du système. Elle interroge l'endpoint /health du backend pour vérifier que l'API répond correctement et mesure sa latence. Elle interroge également Prometheus directement via des requêtes en langage PromQL pour récupérer le taux d'erreurs 5xx en temps réel et la latence au percentile 95. Si Prometheus est indisponible, la page affiche un état dégradé indiquant que les métriques ne sont pas accessibles, sans pour autant faire crasher l'application.

## 4.4 Accessibilité RGAA

L'application respecte plusieurs critères du Référentiel Général d'Amélioration de l'Accessibilité, niveau AA. Premièrement, le contraste entre le texte et le fond a été calculé et ajusté : la couleur dite muted, utilisée pour le texte secondaire, a été modifiée de la valeur #4f6b62 à #3d5a52, ce qui porte le ratio de contraste à 5,2 pour 1, au-dessus du seuil minimal de 4,5 pour 1 imposé par le niveau AA. Deuxièmement, un lien d'évitement, dit skip link, est présent en tête de chaque page sous la forme d'un lien ancré vers l'identifiant main-content. Ce lien, invisible à l'écran mais accessible au clavier, permet aux utilisateurs naviguant au clavier ou avec un lecteur d'écran de sauter directement au contenu principal sans traverser toute la navigation. Troisièmement, la hiérarchie des titres est respectée : chaque page contient un seul titre de niveau h1, puis des titres h2 et h3 pour les sous-sections. Quatrièmement, la navigation au clavier est fonctionnelle avec un focus visible sur les éléments interactifs.

La principale limitation liée à Streamlit est l'impossibilité de contrôler les attributs aria dans le HTML généré automatiquement par le framework. Cette limitation a été documentée de façon transparente comme un compromis assumé, en accord avec l'esprit du RGAA qui reconnaît que certains environnements techniques imposent des contraintes.

## 4.5 Communication avec le backend

Toutes les communications avec le backend transitent par le module api_service.py, qui constitue un client HTTP centralisé et défensif. La fonction get_trajets appelle l'endpoint /trajets avec un timeout de dix secondes et retourne une liste vide en cas d'erreur réseau plutôt que de provoquer une exception. La fonction get_stats_emissions récupère les statistiques de CO2 et retourne un objet avec des valeurs à zéro en cas d'indisponibilité. La fonction get_trajets_map utilise un timeout de quinze secondes, plus long, car les données géographiques sont volumineuses. La fonction ping mesure la latence du backend en calculant le temps de réponse de l'endpoint /health, et retourne un objet contenant un booléen indiquant si le service répond et la latence en millisecondes.

La fonction get_error_rate interroge l'API de Prometheus via une requête PromQL calculant le taux de requêtes HTTP ayant retourné un code d'erreur 5xx sur les cinq dernières minutes. La fonction get_api_latency_p95 interroge Prometheus pour calculer la latence au percentile 95 via la fonction histogram_quantile de PromQL. Ces deux fonctions retournent systématiquement un objet avec la clé value à None en cas d'erreur, sans jamais faire crasher le tableau de bord.

---

# CHAPITRE 5 : TESTS ET INTÉGRATION CONTINUE

## 5.1 Types de tests

Le projet met en œuvre une stratégie de tests à cinq niveaux, chacun correspondant à une granularité différente de vérification.

Les tests unitaires, annotés avec le marqueur pytest unit, testent une seule fonction de façon totalement isolée, sans base de données ni serveur HTTP. Ils vérifient par exemple le comportement des fonctions de normalisation des noms de gares ou de génération des graphiques. Les tests d'intégration, annotés integration, testent un endpoint complet depuis la requête HTTP jusqu'à la réponse JSON, en utilisant une vraie base de données de test. Ils vérifient que les composants s'assemblent correctement. Les tests de contrat, annotés contract, vérifient que la forme des réponses de l'API ne change jamais sans que les tests le signalent : si un champ disparaît ou change de type dans une réponse, le test échoue. Les tests de qualité, annotés quality, vérifient la cohérence métier des données issues de l'ETL Talend : absence de doublons, respect des formats attendus, cohérence géographique. Enfin, les tests de bout en bout utilisant Playwright pilotent un vrai navigateur web pour simuler des parcours utilisateur réels sur l'interface Streamlit.

## 5.2 Organisation des tests

Le projet compte au total cent vingt-huit tests répartis en trois suites. La suite backend comprend quatre-vingt-onze tests organisés dans huit fichiers. La suite dashboard comprend trente et un tests dans trois fichiers. La suite de tests de bout en bout comprend six tests dans deux fichiers.

Le fichier conftest.py joue un rôle central dans la suite backend : il prépare avant chaque test une base de données SQLite en mémoire, une base temporaire légère qui mime le comportement de PostgreSQL pour les tests. Cette base est peuplée avec des données de test connues : quatre pays (France, Allemagne, Italie, Autriche), six gares (Paris Nord, Paris Lyon, Berlin Hbf, München Hbf, Milano Centrale, Wien Hbf), trois opérateurs (SNCF, ÖBB Nightjet, Deutsche Bahn), trois lignes (Paris-Berlin en train de jour, Paris-Vienne en train de nuit, Berlin-Milan en train de jour), quatre trajets avec leurs identifiants, leurs itinéraires et leurs émissions associées. Comme ces données sont réinitialisées à chaque test, chaque test part d'un état connu et propre, ce qui garantit l'isolation et la reproductibilité des résultats.

## 5.3 Outils de test

pytest a été retenu comme framework de test pour sa découverte automatique des fichiers de test, son système de marqueurs qui permet de filtrer les tests par type, et ses rapports détaillés incluant la couverture de code. Playwright a été choisi pour les tests de bout en bout car il pilote un vrai navigateur Chromium en mode headless, c'est-à-dire sans interface graphique visible, et peut être exécuté dans l'environnement de CI/CD sans installation d'un serveur X11. Ruff sert de linter, c'est-à-dire d'outil d'analyse statique du code : il vérifie en quelques millisecondes que le code respecte les conventions de style Python et remplace avantageusement les outils plus anciens Flake8 et isort.

## 5.4 Pipeline GitHub Actions

Le pipeline d'intégration et de livraison continues est défini dans le fichier .github/workflows/main.yml et se déclenche automatiquement à chaque push sur les branches main et develop et à chaque Pull Request vers main. Il est composé de neuf jobs.

Le job changes est le premier à s'exécuter. Il analyse quels dossiers ont été modifiés dans le commit, parmi dashboard, backend et talend, et transmet cette information aux jobs suivants. Ce mécanisme évite de retester l'intégralité de la suite quand un seul composant a changé.

Le job frontend-test s'exécute si des fichiers du dossier dashboard ont changé. Sur un serveur Linux Ubuntu temporaire fourni par GitHub, il installe Python 3.12, installe les dépendances du tableau de bord, puis lance Ruff pour vérifier la syntaxe du code avant de lancer les trente et un tests pytest du dashboard.

Le job backend-test s'exécute si des fichiers du dossier backend ont changé. Il démarre un service PostgreSQL de test, installe Python 3.12 et les dépendances du backend, lance Ruff pour le lint, puis exécute les quatre-vingt-onze tests pytest en utilisant cette base de données réelle.

Le job talend-lint valide l'intégrité du pipeline ETL. Il lance ShellCheck, un outil d'analyse des scripts shell, pour détecter les erreurs dans les scripts bash. Il effectue un scan de secrets pour vérifier qu'aucun mot de passe n'est présent en clair dans les scripts. Il vérifie la présence des neuf fichiers JAR correspondant aux neuf jobs Talend. Il vérifie enfin l'intégrité de chaque fichier JAR en le décompressant et en contrôlant que son contenu est lisible.

Le job talend-etl-dryrun exécute l'intégralité des neuf jobs Talend sur une base de test PostgreSQL provisionnée dans GitHub Actions, en repartant du dernier dump SQL disponible dans le dépôt. Les logs de chaque job sont archivés comme artefact et conservés quatorze jours pour permettre le débogage.

Le job e2e-test s'exécute après la validation des tests frontend et backend. Il lance la stack Docker complète avec docker compose up, attend que Streamlit réponde sur le port 8501 via une boucle de vérification d'une durée maximale de soixante secondes, installe Playwright et son navigateur Chromium, puis exécute les six tests de bout en bout. Quelle que soit l'issue des tests, un docker compose down est systématiquement exécuté pour nettoyer l'environnement.

Les jobs docker-frontend et docker-backend s'exécutent exclusivement sur la branche main, après que les tests correspondants ont réussi. Ils construisent les images Docker du frontend et du backend depuis leurs Dockerfile respectifs, puis les poussent vers le GitHub Container Registry, le registre d'images Docker hébergé par GitHub. Chaque image est taguée avec trois références : le nom de la branche, le SHA du commit pour une traçabilité exacte, et le tag latest pour pointer vers la dernière version stable.

Le job summary s'exécute en dernier, quels que soient les résultats des autres jobs. Il génère un tableau récapitulatif affiché directement dans l'interface GitHub, montrant le statut de chaque bloc du pipeline.

## 5.5 De l'intégration continue à la livraison continue

L'intégration continue et la livraison continue sont dans le même pipeline, mais s'appliquent à des contextes différents. Sur une Pull Request, seuls les tests sont exécutés : le code soumis doit passer l'intégralité des cent vingt-huit tests avant de pouvoir être fusionné dans la branche principale. Sur un push direct sur main, si les tests réussissent, les images Docker sont automatiquement construites et poussées vers le registre. Cette architecture garantit que l'image déployée en production est exactement celle qui a été testée, sans aucune intervention manuelle entre les deux étapes.

---

# CHAPITRE 6 : SUPERVISION

## 6.1 Pourquoi monitorer

La supervision d'une application en production est aussi importante que le code lui-même. Sans monitoring, une panne du backend peut rester inaperçue pendant des heures, jusqu'à ce qu'un utilisateur signale le problème. Avec Prometheus et Grafana, les équipes d'ObRail Europe peuvent consulter en temps réel l'état de l'API, détecter les dégradations de performance avant qu'elles affectent les utilisateurs, et réagir rapidement aux incidents.

## 6.2 Architecture Prometheus et Grafana

L'architecture de supervision repose sur deux outils complémentaires. Prometheus est un système de collecte de métriques open source qui fonctionne en mode scraping : il interroge périodiquement les services qu'il surveille pour récupérer leurs métriques. Dans notre projet, Prometheus scrute l'endpoint /metrics du backend toutes les quinze secondes. Grafana est l'outil de visualisation qui interroge Prometheus via le langage PromQL pour afficher les métriques sous forme de graphiques interactifs.

La liaison entre le backend FastAPI et Prometheus est assurée par la bibliothèque prometheus-fastapi-instrumentator. Cette bibliothèque injecte automatiquement un middleware dans FastAPI, c'est-à-dire une couche intermédiaire invisible qui mesure chaque requête reçue par l'API : sa durée, son code de réponse HTTP et l'endpoint appelé. Elle crée également l'endpoint /metrics que Prometheus interroge. Elle est activée en deux lignes de code dans main.py. Prometheus stocke l'historique de ces métriques dans un volume Docker persistant avec une rétention configurée à trente jours.

## 6.3 Métriques collectées

FastAPI expose nativement deux métriques grâce à l'instrumentation. La première est http_request_duration_seconds, un histogramme qui enregistre la durée de chaque requête en secondes, ventilée par endpoint et par code de réponse HTTP. La seconde est http_requests_inprogress, un compteur en temps réel du nombre de requêtes en cours de traitement à l'instant T.

Prometheus les agrège ensuite pour calculer des métriques dérivées plus utiles pour l'analyse opérationnelle : le taux de requêtes par seconde, le taux d'erreurs 4xx correspondant aux erreurs côté client et le taux d'erreurs 5xx correspondant aux erreurs côté serveur, les percentiles de latence aux niveaux p50, p95 et p99, et l'indicateur de disponibilité du service qui indique si le backend répond ou non.

## 6.4 Le dashboard Grafana en six panneaux

Le dashboard Grafana intitulé ObRail FastAPI Metrics présente six panneaux complémentaires, chacun répondant à une question opérationnelle précise.

Le premier panneau, Requêtes par seconde, utilise la requête PromQL rate appliquée au compteur de requêtes sur la dernière minute. Il permet de visualiser le trafic entrant en temps réel et de détecter des pics ou des baisses anormales d'activité.

Le deuxième panneau, Taux d'erreurs 4xx et 5xx, distingue visuellement les erreurs client, affichées en orange, des erreurs serveur, affichées en rouge. Cette distinction est essentielle car les erreurs 4xx indiquent généralement un problème dans l'utilisation de l'API par les clients, tandis que les erreurs 5xx signalent des bugs ou des indisponibilités côté serveur.

Le troisième panneau, Latence p50/p95/p99, utilise la fonction histogram_quantile de PromQL pour afficher les percentiles de latence. L'utilisation des percentiles plutôt que de la moyenne est un choix délibéré et important : la moyenne peut masquer des situations problématiques. Si quatre-vingt-dix-neuf requêtes répondent en dix millisecondes mais qu'une requête met dix secondes, la moyenne semble acceptable alors que le percentile 99 révèle immédiatement qu'un pourcent des utilisateurs attend dix secondes.

Le quatrième panneau, Requêtes en cours, affiche en temps réel le compteur http_requests_inprogress. Un pic inhabituel de requêtes simultanées peut signaler une saturation du backend ou une boucle de requêtes non maîtrisée.

Le cinquième panneau, Total requêtes, affiche le compteur cumulé de toutes les requêtes traitées depuis le démarrage du service. C'est un indicateur de volume d'utilisation global.

Le sixième panneau, Backend UP/DOWN, est le plus immédiat : il affiche une pastille verte si le service répond et une pastille rouge sinon, en utilisant la métrique up de Prometheus qui vaut 1 quand le scraping réussit et 0 sinon.

## 6.5 Reproductibilité garantie

Lors de la mise en place du monitoring, un problème de reproductibilité a été identifié et documenté dans le fichier why.md. Grafana génère un identifiant unique aléatoire, appelé UID, pour chaque source de données au premier démarrage. Sur une deuxième machine, cet identifiant est différent. Or le fichier JSON du dashboard référence cet UID pour savoir quelle source de données utiliser. Résultat : les panneaux du dashboard s'affichaient vides sur toute machine autre que celle où le dashboard avait été initialement créé.

La solution adoptée consiste à fixer explicitement l'UID de la source de données Prometheus à la valeur littérale obrail-prometheus dans le fichier de provisioning Grafana. Le dashboard JSON référence ensuite cet UID fixe et non plus un identifiant aléatoire. Grâce au provisioning automatique via les volumes Docker, qui charge les dashboards et les datasources au démarrage depuis des fichiers du dépôt, le dashboard s'affiche correctement sur n'importe quelle machine, en CI comme en déploiement, sans la moindre intervention manuelle.

---

# CHAPITRE 7 : DÉPLOIEMENT

## 7.1 Déploiement local avec Docker Compose

Le déploiement local de la stack complète s'effectue avec une seule commande : docker compose up -d --build. Docker lit le fichier docker-compose.yml qui définit les cinq services du projet et les assemble dans un réseau privé nommé obrail.

Le service PostgreSQL démarre en premier et charge automatiquement le dump SQL du dépôt, ce qui initialise toutes les tables avec les données réelles sans intervention manuelle. Le service backend attend que PostgreSQL soit pleinement opérationnel grâce au mécanisme de condition de démarrage depends_on avec la vérification de santé service_healthy. Une fois PostgreSQL prêt, le backend démarre et expose l'API sur le port 8000. Le frontend Streamlit, Prometheus et Grafana démarrent ensuite de façon parallèle.

Des volumes Docker persistants garantissent que les données survivent aux redémarrages : postgres_data conserve les données de la base, prometheus_data conserve l'historique des métriques sur trente jours, et grafana_data conserve les configurations. Les ports exposés sur la machine hôte sont le port 5433 pour PostgreSQL, le port 8000 pour le backend, le port 8501 pour le frontend, le port 9090 pour Prometheus et le port 3010 pour Grafana. Le port non standard 5433 pour PostgreSQL est un choix délibéré pour éviter les conflits avec une éventuelle instance PostgreSQL locale déjà en cours.

Le premier démarrage nécessite trois à cinq minutes en raison du téléchargement des images Docker et de la construction des images custom. Les démarrages suivants prennent trente secondes environ car les images sont mises en cache localement.

## 7.2 Build et push des images

Sur un push sur la branche main, après que les tests ont réussi, le pipeline GitHub Actions exécute automatiquement les jobs docker-backend et docker-frontend. Ces jobs construisent les images Docker depuis les Dockerfile de chaque composant, les taggent avec trois formats différents, le nom de la branche main pour les déploiements stables, le SHA du commit pour la traçabilité exacte de la version déployée, et le tag latest pour pointer vers la dernière version stable. Les images sont poussées vers GitHub Container Registry, accessible à l'adresse ghcr.io. Cette approche permet de déployer la dernière version validée en production avec une simple commande docker pull, sans avoir à reconstruire l'image localement.

## 7.3 Options de déploiement en ligne

Trois options de déploiement en ligne ont été étudiées pour héberger l'application publiquement. Fly.io est l'option recommandée : son offre gratuite inclut trois machines virtuelles partagées et une base PostgreSQL de trois gigaoctets, sans mise en veille automatique. Le déploiement s'effectue avec quatre commandes : la création de la base PostgreSQL, l'initialisation de l'application, l'attachement de la base à l'application, la configuration des secrets d'environnement, et le déploiement proprement dit.

Render est plus simple à prendre en main grâce à son interface web, mais présente un inconvénient majeur pour une démo publique : les services gratuits se mettent en veille après quinze minutes d'inactivité, ce qui rend le premier appel suivant cette mise en veille très lent, de l'ordre de trente secondes.

Oracle Cloud Free Tier offre deux machines virtuelles gratuites à vie, ce qui est techniquement suffisant pour faire tourner la stack complète incluant Prometheus et Grafana. En revanche, cette option nécessite une configuration plus technique, notamment l'ouverture manuelle des ports réseau dans les règles de sécurité du cloud et l'installation de Docker via SSH. Fly.io représente le meilleur compromis entre simplicité de déploiement et stabilité pour une démonstration publique.

---

# CHAPITRE 8 : CONCLUSION

## 8.1 Synthèse des compétences couvertes

Ce projet couvre l'ensemble des huit compétences définies par le référentiel RNCP36581 du titre Développeur en Intelligence Artificielle et Data Science.

La compétence d'analyse du besoin est couverte par le chapitre d'introduction, qui formalise le contexte d'ObRail Europe, identifie les contraintes techniques et réglementaires, et traduit les besoins métier en sept objectifs opérationnels mesurables.

La compétence de conception de l'architecture est couverte par le schéma des cinq services Docker et les justifications des choix techniques documentées dans chaque chapitre : PostgreSQL pour la base de données, FastAPI pour le backend, Streamlit pour le frontend, Prometheus et Grafana pour le monitoring.

La compétence de coordination en contexte agile et MLOps est couverte par le workflow Git structuré autour des branches, des Pull Requests et du pipeline CI/CD qui impose la validation des tests avant tout merge. Le monitoring continu et le fichier why.md documentant les décisions techniques s'inscrivent dans une démarche MLOps.

La compétence de développement front-end, back-end et sécurité est couverte par le backend avec ses treize endpoints, son rate limiting et ses quatre headers de sécurité, par le frontend avec ses trois pages et ses mesures RGAA, et par l'ETL Talend qui traite les sources de données hétérogènes.

La compétence d'automatisation des tests est couverte par les cent vingt-huit tests organisés en cinq types et exécutés automatiquement dans le pipeline GitHub Actions à chaque push.

La compétence de livraison continue est couverte par le build automatique des images Docker et leur push vers GitHub Container Registry sur la branche main, garantissant que l'image déployée est exactement celle qui a été testée.

La compétence de supervision avec monitoring est couverte par Prometheus et Grafana avec leur dashboard en six panneaux, par la page Supervision du tableau de bord qui expose les métriques en temps réel, et par la gestion de la reproductibilité de la configuration Grafana documentée dans why.md.

La compétence de résolution des incidents est couverte par les trois corrections documentées dans why.md : le problème de double montage du dump SQL au démarrage, le problème de l'UID aléatoire de Grafana qui rendait le dashboard vide sur d'autres machines, et les mesures de sécurité ajoutées suite à l'identification d'un backend non protégé.

## 8.2 Perspectives d'accueil d'un futur modèle d'intelligence artificielle

Le projet a été conçu dès l'origine pour faciliter l'intégration d'un modèle d'intelligence artificielle dans une prochaine itération. Plusieurs éléments de l'architecture actuelle constituent des fondations directement exploitables.

L'API expose les données ferroviaires au format JSON standardisé, ce que tout modèle d'apprentissage machine peut consommer facilement sans transformation supplémentaire. Le pipeline CI/CD peut être étendu pour intégrer une étape d'entraînement automatique déclenchée lors des modifications des données sources ou du code du modèle. Le monitoring Prometheus peut être étendu pour suivre des métriques spécifiques aux modèles d'intelligence artificielle, comme la dérive des données d'entrée, la précision des prédictions ou le taux de rappel, en ajoutant simplement de nouveaux compteurs dans le service d'inférence. Les volumes persistants Docker permettent de conserver les artefacts d'entraînement, les checkpoints de modèles et les historiques d'évaluation entre les redémarrages. La conteneurisation Docker garantit que le service d'inférence sera déployé dans les mêmes conditions reproductibles que le reste de la stack.

La prochaine étape naturelle du projet consiste à implémenter un microservice de prédiction qui, à partir des données historiques des trajets stockées dans PostgreSQL, estimera la fréquentation future d'une ligne ou recommandera des optimisations de dessertes. Ce service s'inscrirait dans le réseau Docker existant, exposerait ses propres endpoints via l'API FastAPI, et bénéficierait immédiatement du monitoring et de la couverture de tests mis en place dans ce MSPR3. En ce sens, la valeur de ce projet ne réside pas seulement dans ce qu'il fait aujourd'hui, mais dans la robustesse de l'infrastructure qu'il établit pour demain.
