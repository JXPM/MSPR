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

La base de données constitue le socle de toute l'application. Elle est structurée autour de dix tables organisées en trois couches logiques. La première couche, dite couche référentiel, regroupe les données de structure du réseau ferroviaire : la table pays stocke les vingt-six pays européens identifiés par leur code ISO à deux lettres, comme FR pour la France ou DE pour l'Allemagne. La table gare recense toutes les gares du réseau avec leur nom, leurs coordonnées GPS et leur appartenance à un pays. La table operateur liste les compagnies ferroviaires. La table ligne décrit les lignes ferroviaires avec leur nom, leur distance et leur type, qui peut être JOUR ou NUIT. La table type_train référence les catégories de matériel roulant.

La deuxième couche, dite couche exploitation, couvre les circulations réelles. La table trajet représente un aller simple entre une gare de départ et une gare d'arrivée, avec les horaires de départ et d'arrivée stockés au format texte HH:mm:ss. La table itineraire détaille les arrêts intermédiaires de chaque trajet, ordonnés par leur rang de passage et rattachés à leurs coordonnées géographiques via le code UIC de chaque gare.

La troisième couche, la couche analyse, contient une unique table emission qui stocke l'empreinte carbone de chaque trajet, à la fois pour le train et pour l'avion. Deux tables d'association complètent ce modèle : la table exploite lie les opérateurs aux lignes qu'ils exploitent, et la table utilisation associe les opérateurs aux types de matériel roulant qu'ils emploient.

Les clés primaires suivent des logiques différentes selon les tables : la table pays utilise le code ISO à deux caractères comme clé naturelle, la table gare utilise le code UIC à sept chiffres, la table trajet utilise un identifiant alphanumérique issu des données sources, et la table itineraire utilise une clé composite formée de l'identifiant du trajet et du rang de l'arrêt.

Le modèle respecte la troisième forme normale, communément abrégée 3NF, qui est le standard de normalisation des bases de données relationnelles. La normalisation est un processus de conception qui consiste à organiser les colonnes et les tables de façon à éliminer les redondances et à prévenir les anomalies de mise à jour. La première forme normale exige que chaque cellule d'une table ne contienne qu'une valeur atomique, c'est-à-dire non décomposable : dans notre table itineraire, chaque arrêt est stocké sur une ligne distincte avec son rang, plutôt que comme une liste de valeurs dans une seule colonne. La deuxième forme normale exige que chaque attribut non clé dépende de la totalité de la clé primaire et non d'une partie de celle-ci : dans la table trajet, le nom de la gare de départ n'est pas stocké directement mais est obtenu via la clé étrangère vers la table gare, évitant ainsi de dupliquer le nom à chaque trajet qui part de cette gare. La troisième forme normale exige qu'aucun attribut non clé ne dépende d'un autre attribut non clé : dans notre modèle, le pays d'une gare n'est pas stocké dans la table trajet mais dans la table gare, car c'est la gare qui appartient à un pays, non le trajet. Cette normalisation a une conséquence opérationnelle directe : si le nom d'une gare change, une seule mise à jour dans la table gare suffit pour que tous les trajets qui la référencent reflètent immédiatement le nouveau nom, sans avoir à parcourir toutes les tables.

## 2.2 Choix de PostgreSQL

Le choix du système de gestion de base de données s'est porté sur PostgreSQL en s'appuyant sur trois niveaux d'analyse complémentaires : une comparaison directe avec les alternatives envisagées, les trois V du Big Data qui caractérisent les contraintes imposées par les données elles-mêmes, et les propriétés ACID qui garantissent la fiabilité des opérations de lecture et d'écriture.

### Comparaison avec les alternatives

Par rapport à MySQL, PostgreSQL offre un meilleur support des contraintes d'intégrité référentielle et une conformité plus stricte au standard SQL, ce qui garantit la cohérence des relations entre les dix tables. MySQL est historiquement moins rigoureux sur certaines violations de contraintes qu'il peut accepter silencieusement selon la configuration du mode SQL, là où PostgreSQL rejette systématiquement toute violation. Par rapport à SQLite, PostgreSQL gère nativement la concurrence d'accès multiples, ce qui est indispensable dès lors que plusieurs services Docker lisent simultanément la même base : SQLite verrouille l'intégralité de son fichier lors de chaque écriture, ce qui provoquerait des erreurs de verrouillage dès que le backend FastAPI et un job Talend tenteraient d'accéder à la base au même moment. Par rapport à MongoDB, un système de base de données orientée documents, PostgreSQL impose un schéma relationnel strict qui correspond exactement à la nature des données ferroviaires, dans lesquelles chaque trajet appartient à une ligne, chaque ligne est exploitée par un opérateur, et chaque gare est localisée dans un pays. MongoDB convient bien à des données dont la structure varie d'un document à l'autre, ce qui n'est pas notre cas : nos données sont hautement structurées et interconnectées, et les contraintes d'intégrité référentielle de PostgreSQL sont précisément ce qui garantit que ces interconnexions restent valides. Enfin, PostgreSQL est le système de référence pour SQLAlchemy, l'ORM utilisé dans notre backend.

### Les trois V du Big Data appliqués au projet ObRail

Le modèle des trois V, formulé par l'analyste Doug Laney en 2001, est un cadre de référence pour évaluer les exigences techniques que posent les données à grande échelle. Il distingue le Volume, la Variété et la Vélocité.

Le Volume désigne la quantité totale de données à stocker et à interroger. Dans notre projet, les données ferroviaires européennes représentent plusieurs dizaines de milliers de gares, de trajets et d'itinéraires issus de sources couvrant vingt-six pays. PostgreSQL gère ce volume sans dégradation de performance grâce à son moteur d'indexation B-tree, qui permet des recherches en temps logarithmique même sur des tables contenant des millions d'enregistrements. Concrètement, l'index sur le code UIC de la table gare, ou sur l'identifiant de la table trajet, permet à la requête de trouver un enregistrement précis en quelques microsecondes quelle que soit la taille de la table. SQLite, par comparaison, ne dispose pas du même optimiseur de requêtes et deviendrait sensiblement plus lent à mesure que le volume de données augmenterait avec les prochaines intégrations de sources européennes supplémentaires.

La Variété désigne l'hétérogénéité des formats et des structures de données. Notre projet est confronté à une variété maximale : les données proviennent de fichiers CSV d'OpenStreetMap, de fichiers JSON de Back-on-Track, de flux GTFS de la SNCF au format ZIP, chacun avec ses propres conventions de nommage, ses propres types de champs et ses propres unités. PostgreSQL répond à cette variété de deux façons. D'une part, son schéma relationnel strict force une normalisation complète des données lors de l'insertion par l'ETL Talend : une gare dont le code pays n'existe pas dans la table pays ne peut pas être insérée, ce qui garantit la cohérence du référentiel. D'autre part, PostgreSQL supporte nativement les types JSON et JSONB, permettant de stocker des structures semi-structurées dans des colonnes dédiées lorsque le format source est trop irrégulier pour être normalisé. MongoDB aurait géré cette variété de format, mais au détriment de la cohérence relationnelle : sans contraintes d'intégrité référentielle, rien n'empêcherait d'insérer un trajet référençant une gare de départ inexistante dans la table gare.

La Vélocité désigne la fréquence à laquelle les données arrivent et doivent être interrogées. Dans notre cas, la vélocité comporte deux dimensions. En écriture, les neuf jobs Talend exécutent des insertions massives en batch lors de chaque chargement mensuel : PostgreSQL gère ces insertions en masse efficacement grâce au mécanisme COPY, qui contourne les vérifications ligne par ligne pour insérer des milliers d'enregistrements en une seule opération transactionnelle. En lecture, plusieurs services Docker interrogent simultanément la base : le backend FastAPI reçoit les requêtes du dashboard et les scrapes de Prometheus toutes les quinze secondes, les tests d'intégration du pipeline CI/CD ouvrent leurs propres connexions, et le job talend-etl-dryrun peut s'exécuter en parallèle. PostgreSQL gère cette concurrence d'accès en lecture grâce à son mécanisme MVCC, pour Multi-Version Concurrency Control ou Contrôle de Concurrence par Multiversion : chaque transaction de lecture voit un instantané cohérent de la base au moment où elle commence, sans bloquer ni être bloquée par les transactions d'écriture simultanées. SQLite, qui verrouille l'intégralité du fichier de base lors de chaque écriture, est incompatible avec cette contrainte de concurrence.

### Les propriétés ACID appliquées au projet ObRail

ACID est l'acronyme des quatre propriétés fondamentales que PostgreSQL garantit pour toutes ses transactions. Une transaction est une séquence d'opérations SQL qui s'exécutent comme un tout indivisible : soit toutes les opérations réussissent et leurs effets sont enregistrés définitivement, soit l'une d'elles échoue et toutes les autres sont annulées comme si rien ne s'était passé.

L'Atomicité signifie qu'une transaction est tout ou rien. Dans notre projet, le job Talend qui insère un trajet ne se contente pas d'écrire dans la table trajet : il insère également les enregistrements correspondants dans la table itineraire et dans la table emission dans la même transaction. Si l'insertion de l'itinéraire échoue, par exemple parce qu'un code UIC de gare intermédiaire est absent de la table gare, PostgreSQL annule automatiquement l'insertion du trajet et des émissions, laissant la base dans un état cohérent. Sans atomicité, on pourrait se retrouver avec un trajet sans itinéraire ni émissions associées, ce qui fausserait tous les calculs de statistiques.

La Cohérence signifie que toute transaction amène la base d'un état valide à un autre état valide, en respectant toutes les contraintes déclarées dans le schéma. Dans notre modèle, la contrainte de clé étrangère entre la table gare et la table pays garantit qu'une gare ne peut exister que si son pays est répertorié. La contrainte UNIQUE sur le code UIC garantit qu'une même gare ne peut pas être insérée deux fois. La contrainte NOT NULL sur le nom d'une ligne garantit qu'aucune ligne sans nom ne peut exister. PostgreSQL vérifie automatiquement l'ensemble de ces contraintes à chaque écriture et rejette toute tentative de violation, sans qu'aucun code applicatif n'ait à les vérifier manuellement.

L'Isolation signifie que les transactions concurrentes ne s'interfèrent pas entre elles. Concrètement, pendant qu'un job Talend est en train d'insérer de nouveaux trajets dans une transaction non encore validée, le backend FastAPI qui répond à une requête du dashboard voit la base dans l'état précédant cette insertion : il ne voit ni les données partiellement insérées, ni les données qui pourraient être annulées. Cela évite les lectures dites sales, où un service lirait des données temporaires qui disparaissent ensuite. Dans notre stack Docker où plusieurs services s'exécutent en parallèle, cette propriété est indispensable pour que les statistiques calculées par le backend soient toujours cohérentes.

La Durabilité signifie que les données d'une transaction validée sont définitivement enregistrées, même en cas de panne électrique ou de crash du serveur survenant immédiatement après la validation. PostgreSQL garantit cette propriété grâce au mécanisme WAL, pour Write-Ahead Logging : avant d'écrire les données dans les fichiers principaux, PostgreSQL écrit d'abord un journal des opérations effectuées. En cas de panne, ce journal permet de rejouer les opérations non encore écrites dans les fichiers principaux et de retrouver un état cohérent au redémarrage. Dans notre déploiement Docker, le volume persistant postgres_data garantit que ce journal et les fichiers de données survivent aux arrêts et redémarrages des conteneurs.

## 2.3 ETL Talend

L'ETL, acronyme d'Extract Transform Load désignant le pipeline de traitement des données, est orchestré avec Talend Open Studio for Data Integration. Talend lit les sources brutes, les nettoie, les transforme et les insère dans PostgreSQL via des connecteurs JDBC, le protocole standard de connexion Java aux bases de données.

Les sources de données mobilisées sont au nombre de trois principales. Le fichier stations.csv issu d'OpenStreetMap fournit les gares avec leurs coordonnées géographiques. Le fichier trips.json publié par Back-on-Track contient les trajets ferroviaires européens, notamment les trains de nuit, avec les informations d'opérateurs, de lignes, d'itinéraires et d'émissions de CO2. Les fichiers GTFS de la SNCF, au format ZIP contenant des fichiers CSV, fournissent les catégories de matériel roulant.

Pour bien comprendre ce que fait concrètement chaque lettre de l'acronyme ETL dans notre projet, il est utile de détailler chaque phase. L'Extraction consiste à lire les données brutes depuis leurs sources sans les modifier : Talend ouvre le fichier stations.csv, lit chaque ligne, ouvre le fichier trips.json et parcourt chaque objet du tableau, ou décompresse le fichier GTFS et lit les fichiers CSV qu'il contient. À ce stade, les données sont dans leur état d'origine, avec tous leurs défauts : encodage hétérogène des caractères, valeurs manquantes, noms de colonnes différents d'une source à l'autre. La Transformation est la phase la plus complexe : pour chaque enregistrement extrait, Talend applique une série d'opérations de nettoyage et de conversion. Cela inclut la normalisation des encodages de caractères pour corriger les noms de villes mal encodés, la déduplication pour supprimer les gares apparaissant plusieurs fois avec des orthographes légèrement différentes, la conversion des types pour transformer les coordonnées GPS de texte en nombres flottants, le mapping des colonnes pour faire correspondre le champ lat_lon du fichier source au champ latitude et longitude de la table gare, et le calcul des valeurs dérivées comme l'empreinte carbone de l'avion. Le Chargement est la phase finale : les enregistrements transformés et validés sont insérés dans PostgreSQL via JDBC. Talend contrôle l'ordre des insertions pour respecter les contraintes de clés étrangères : on ne peut pas insérer une gare avant que son pays soit présent, ni un trajet avant que ses gares de départ et d'arrivée existent.

Le choix de Talend s'explique par sa capacité à traiter simultanément des formats multi-sources très hétérogènes, par sa traçabilité graphique qui permet de visualiser et de documenter chaque étape de transformation sous forme de diagramme, et par le fait que les jobs compilés sous forme de fichiers JAR sont réutilisables sans dépendance à l'environnement de développement : n'importe quel serveur disposant d'une JVM Java peut exécuter ces jobs sans que Talend Open Studio soit installé.

Le pipeline Talend est composé de neuf jobs exécutés dans un ordre précis qui respecte les dépendances entre tables. Le premier job charge la table pays à partir des codes ISO. Le deuxième charge les gares depuis le fichier stations.csv. Le troisième charge les opérateurs ferroviaires. Le quatrième charge les types de matériel roulant depuis les données GTFS. Le cinquième charge les lignes. Le sixième charge les trajets. Le septième, le job exploite, établit les liens entre opérateurs et lignes. Le huitième charge les itinéraires, c'est-à-dire les arrêts intermédiaires. Le neuvième, enfin, calcule et insère les émissions de CO2.

Le calcul de l'empreinte carbone de l'avion suit la formule suivante : l'empreinte en kilogrammes est égale à la distance en kilomètres multipliée par le facteur d'émission 0,158 kilogramme de CO2 équivalent par passager et par kilomètre. Ce facteur est issu des référentiels de l'ADEME, l'Agence de la transition écologique française, et du BEIS, le département britannique équivalent. L'empreinte carbone du train, quant à elle, est directement lue depuis le champ emissions_co2e du fichier trips.json fourni par Back-on-Track.

## 2.4 Flux de données

Le flux de données suit une chaîne linéaire et déterministe. Les sources brutes, qu'il s'agisse de CSV, de JSON ou de fichiers GTFS, sont lues par les neuf jobs Talend qui effectuent l'extraction, le nettoyage, le mapping et la validation de chaque enregistrement avant son insertion dans PostgreSQL. Ce processus aboutit à une base relationnelle propre, déduplicatée et cohérente, qui constitue la seule source de vérité pour le reste de l'application. Au premier démarrage de Docker, la base est préchargée automatiquement depuis le dump SQL versé dans le dépôt, ce qui évite de devoir relancer l'ETL complet à chaque déploiement.

## 2.5 Conformité RGPD

Le projet ne traite aucune donnée à caractère personnel. Toutes les données utilisées proviennent de l'open data public : les horaires de trains, les coordonnées des gares et les émissions de CO2 sont des informations publiques qui ne permettent pas d'identifier un individu. Plusieurs mesures techniques renforcent néanmoins la conformité réglementaire. Les journaux applicatifs ne contiennent aucune adresse IP d'utilisateur. Les secrets de connexion à la base de données, comme les mots de passe, ne sont jamais versionnés dans le dépôt Git mais sont gérés via un fichier d'environnement non versionné et via les GitHub Secrets pour le pipeline CI/CD. L'historique des métriques Prometheus est limité à trente jours par paramétrage explicite, ce qui évite l'accumulation indéfinie de données. Enfin, un fichier d'exemple documenté est fourni pour permettre à tout nouveau contributeur de configurer son environnement sans accéder aux vraies credentials.

---

# CHAPITRE 3 : BACKEND

## 3.1 Qu'est-ce qu'un backend et pourquoi en avoir un ?

Avant de décrire les choix techniques, il est important de comprendre ce qu'est un backend et quel rôle il joue dans l'architecture d'une application web. Dans notre projet, trois composants logiciels coexistent : la base de données PostgreSQL, qui stocke les informations de façon permanente ; le frontend Streamlit, qui est l'interface que l'utilisateur voit dans son navigateur ; et le backend, qui joue le rôle d'intermédiaire entre les deux.

Concrètement, le frontend ne communique jamais directement avec la base de données. Si c'était le cas, il faudrait exposer le mot de passe de la base sur le réseau, ce qui constituerait une faille de sécurité majeure. Le frontend ne saurait pas non plus formuler les requêtes SQL complexes nécessaires pour calculer les statistiques d'émissions de CO2. Le backend résout ces deux problèmes à la fois : il sait parler à la base de données, il protège les identifiants de connexion, et il fournit au frontend des données déjà calculées et mises en forme, prêtes à l'affichage.

Le backend est ce qu'on appelle une API REST. Le terme API signifie Interface de Programmation Applicative, c'est-à-dire un point de contact standardisé qu'une application met à disposition pour que d'autres applications puissent lui poser des questions ou lui donner des instructions. Le terme REST, acronyme de Representational State Transfer, désigne un style d'architecture qui utilise le protocole HTTP, le même protocole que celui utilisé par votre navigateur pour afficher des pages web, et qui organise les échanges autour de ressources nommées par des URL. Une API REST répond en JSON, un format textuel structuré comme des paires clé-valeur que tous les langages de programmation savent lire nativement.

Pour illustrer concrètement : lorsque le tableau de bord Streamlit veut afficher la liste des trajets, il envoie une requête HTTP de type GET vers l'URL http://backend:8000/trajets. Le backend reçoit cette requête, interroge PostgreSQL, formate les résultats en JSON, et renvoie la réponse au frontend. Tout cela se passe en quelques dizaines de millisecondes.

## 3.2 Architecture en couches séparées

Le code du backend est organisé en couches séparées dont chacune a une responsabilité unique et clairement délimitée. Cette organisation, appelée architecture en couches ou layered architecture, présente plusieurs avantages essentiels pour un projet destiné à évoluer : si l'on décide de changer de base de données, seule la couche accès aux données est à modifier. Si l'on veut ajouter un nouvel endpoint, seules les couches routes et services sont concernées. Si les règles de validation des données changent, seule la couche schémas est à mettre à jour. Cette séparation limite l'impact des modifications et réduit le risque d'introduire des régressions.

Le fichier main.py est le point d'entrée de l'application, le premier fichier exécuté quand le serveur démarre. C'est lui qui instancie le framework FastAPI, c'est-à-dire qui crée l'objet central auquel tous les autres composants se rattachent. Il enregistre les middlewares, qui sont des couches de traitement intermédiaires qui interceptent chaque requête avant qu'elle n'atteigne sa destination et chaque réponse avant qu'elle soit renvoyée au client : un middleware peut ainsi ajouter des headers de sécurité à toutes les réponses sans que chaque endpoint ait à s'en préoccuper individuellement. Main.py active également le rate limiting pour limiter le débit des requêtes et connecte l'instrumentation Prometheus pour le monitoring.

Le fichier database.py gère exclusivement la connexion à PostgreSQL. Il configure SQLAlchemy avec l'URL de connexion à la base, crée le moteur de base de données, et fournit une fonction qui génère une session à la demande. Une session est en quelque sorte un canal de communication ouvert avec la base de données pour la durée d'une requête : elle s'ouvre quand le traitement commence et se ferme automatiquement une fois la réponse envoyée, libérant ainsi la connexion pour d'autres requêtes.

Le dossier models regroupe les classes Python qui représentent les dix tables de la base de données. C'est ici que le mapping entre le monde relationnel de SQL et le monde objet de Python est défini. Chaque classe hérite de la classe Base de SQLAlchemy et correspond à une table. Chaque attribut de classe décoré avec la fonction Column correspond à une colonne SQL, avec son type (entier, texte, nombre flottant), ses contraintes (clé primaire, unicité, valeur non nulle) et ses relations avec les autres tables. Par exemple, la classe Gare possède un attribut id_pays qui est une clé étrangère pointant vers la table pays, et SQLAlchemy sait automatiquement comment effectuer la jointure correspondante quand on accède à la gare.pays depuis le code Python.

Le dossier schemas contient les schémas de validation Pydantic. Il est important de ne pas confondre les modèles SQLAlchemy et les schémas Pydantic, même s'ils décrivent parfois les mêmes données. Les modèles SQLAlchemy servent à lire et écrire dans la base de données. Les schémas Pydantic, en revanche, définissent la forme exacte que doivent avoir les données qui entrent dans l'API et qui en sortent. Un schéma de sortie peut exposer moins de champs que la table correspondante pour ne pas divulguer des informations sensibles. Un schéma d'entrée peut inclure des validations métier comme l'obligation qu'un code UIC soit exactement à sept chiffres. Si une requête arrive avec un champ manquant ou d'un type incorrect, Pydantic rejette automatiquement la requête avec un message d'erreur clair, sans que le code métier n'ait besoin de vérifier quoi que ce soit manuellement.

Le dossier routes définit les endpoints de l'API, regroupés par domaine fonctionnel en cinq fichiers : health_routes.py pour la supervision, gare_routes.py pour les gares, ligne_routes.py pour les lignes, trajet_routes.py pour les trajets, et stats_routes.py pour les statistiques agrégées. Chaque fichier crée un routeur FastAPI et déclare des fonctions Python décorées avec le type de méthode HTTP et l'URL correspondante. Par exemple, la déclaration @router.get("/gares") devant une fonction Python indique à FastAPI que cette fonction doit être appelée chaque fois qu'une requête GET arrive sur l'URL /gares. FastAPI se charge lui-même d'analyser l'URL, d'extraire les paramètres éventuels, d'appeler la fonction et de sérialiser le résultat en JSON.

Enfin, le dossier services contient la logique métier, c'est-à-dire les traitements qui correspondent aux règles du domaine ferroviaire et non aux détails techniques du protocole HTTP ou du langage SQL. C'est ici que se trouvent les requêtes SQL complexes comme le calcul des émissions moyennes comparées entre train et avion, les jointures multi-tables pour reconstituer l'itinéraire complet d'un trajet, et les fonctions de normalisation des noms de gares qui unifient les différentes graphies trouvées dans les sources de données.

## 3.3 Choix techniques justifiés

Le choix de Python comme langage principal est naturel dans un projet de data science : son écosystème est le plus riche du domaine, avec des bibliothèques matures pour la manipulation de données, la validation et la création d'API. De plus, utiliser Python à la fois pour le backend et pour le frontend Streamlit permet à l'équipe de ne maîtriser qu'un seul langage pour l'ensemble du projet, ce qui est un avantage logistique non négligeable.

Le choix de FastAPI comme framework d'API plutôt que Flask, son concurrent le plus populaire, s'explique par deux avantages décisifs. D'une part, FastAPI génère automatiquement une documentation Swagger interactive à partir des annotations de type Python, ce qui évite de maintenir une documentation séparée qui finit inévitablement par diverger du code réel au fil des modifications. Tout développeur qui rejoint le projet peut consulter la documentation à l'adresse /docs et tester immédiatement les endpoints sans avoir à configurer un outil externe. D'autre part, FastAPI intègre nativement Pydantic pour la validation des données, ce qui permet de détecter immédiatement les erreurs de format avant même que la logique métier soit exécutée, là où Flask nécessite une bibliothèque tierce supplémentaire et une configuration manuelle.

SQLAlchemy est utilisé comme ORM, acronyme d'Object-Relational Mapper, que l'on peut traduire par Mappeur Objet-Relationnel. Pour comprendre pourquoi un ORM est utile, il faut avoir à l'esprit le problème qu'il résout. Sans ORM, le code Python doit construire des chaînes de texte SQL comme SELECT * FROM gare WHERE id_pays = 'FR' ORDER BY nom, les envoyer à la base, et interpréter manuellement le résultat brut sous forme de tuples. Cette approche est fastidieuse, source d'erreurs typographiques difficiles à détecter, et vulnérable aux injections SQL si les paramètres ne sont pas correctement échappés. Avec SQLAlchemy, on écrit à la place session.query(Gare).filter(Gare.id_pays == 'FR').order_by(Gare.nom).all(), ce qui est lisible, sûr par construction car SQLAlchemy paramètre automatiquement les valeurs, et indépendant du dialecte SQL utilisé. SQLAlchemy est le standard de facto pour Python et prend en charge les relations complexes entre tables telles que celles de notre modèle.

Pydantic assure le typage fort et la validation des réponses, garantissant que les données envoyées au frontend sont toujours dans le format attendu. Sans Pydantic, si le code Python construit un dictionnaire avec un champ manquant ou d'un type inattendu, le frontend reçoit des données incorrectes et produit des erreurs difficiles à diagnostiquer. Avec Pydantic, si la donnée ne correspond pas au schéma défini, une exception est levée immédiatement à la sortie du service, avant même que la réponse ne soit sérialisée en JSON.

Uvicorn sert de serveur ASGI, acronyme d'Asynchronous Server Gateway Interface. La différence entre ASGI et son prédécesseur WSGI, le Synchronous Server Gateway Interface, réside dans la gestion de la concurrence. Un serveur WSGI traditionnel comme Gunicorn crée un nouveau fil d'exécution ou un nouveau processus pour chaque requête simultanée. Cela fonctionne bien jusqu'à quelques dizaines de requêtes simultanées, mais devient coûteux en mémoire au-delà. Un serveur ASGI comme Uvicorn, en revanche, peut gérer des milliers de connexions simultanées dans un seul processus grâce à la programmation asynchrone, où une requête en attente d'une réponse de la base de données n'occupe pas un fil d'exécution entier pendant ce temps d'attente.

## 3.4 Les endpoints de l'API en détail

Pour comprendre ce qu'est un endpoint, il faut comprendre comment fonctionne une requête HTTP. Lorsqu'un client, qu'il s'agisse du navigateur d'un utilisateur, du frontend Streamlit ou d'un script de test automatisé, souhaite obtenir des données, il envoie un message standardisé selon le protocole HTTP. Ce message comporte plusieurs éléments : une méthode qui indique le type d'action souhaitée, une URL qui identifie la ressource visée, et éventuellement un corps contenant des données supplémentaires. La méthode GET signifie que le client veut lire des données sans modifier quoi que ce soit. La méthode POST signifie qu'il veut créer une nouvelle ressource. PUT et PATCH modifient une ressource existante. DELETE la supprime. Dans notre API, toutes les méthodes sont des GET car l'application expose uniquement des données en lecture seule.

Un endpoint est donc la combinaison d'une méthode HTTP et d'une URL. Lorsque le serveur reçoit cette combinaison, il exécute la fonction Python associée et renvoie une réponse HTTP comprenant un code de statut numérique à trois chiffres et un corps JSON contenant les données. Le code 200 signifie succès. Le code 404 signifie que la ressource demandée n'existe pas. Le code 422 signifie que les paramètres fournis sont invalides. Le code 429 signifie que le client a envoyé trop de requêtes trop vite. Le code 500 signifie qu'une erreur interne s'est produite côté serveur.

L'API expose treize endpoints. L'endpoint GET /health retourne simplement l'état de santé du serveur sous la forme d'un objet JSON minimal comme {"status": "ok"}, ce qui permet à l'infrastructure de surveiller que le backend est vivant. L'endpoint GET /metrics expose les métriques de performance dans un format texte propriétaire que Prometheus comprend, avec une ligne par métrique indiquant son nom, ses labels et sa valeur numérique. L'endpoint GET /trajets retourne la liste complète des trajets disponibles sous forme d'un tableau JSON. L'endpoint GET /trajets/{id} retourne le détail d'un trajet précis : les accolades dans l'URL indiquent un paramètre de chemin variable que FastAPI extrait automatiquement et transmet à la fonction Python. L'endpoint GET /trajets/{id}/itineraire retourne les arrêts intermédiaires ordonnés d'un trajet donné, dans l'ordre de passage. L'endpoint GET /gares retourne la liste de toutes les gares avec leur nom, leur code UIC, leurs coordonnées GPS en latitude et longitude, et le pays auquel elles appartiennent. L'endpoint GET /lignes retourne la liste de toutes les lignes ferroviaires avec leur nom, leur distance et leur type, qui peut être JOUR ou NUIT.

Du côté des statistiques, l'endpoint GET /stats/trajets/count retourne un objet JSON contenant uniquement le nombre total de trajets, sans le détail de chaque trajet. L'endpoint GET /stats/trajets/type retourne la répartition entre trains de jour et trains de nuit sous la forme d'un tableau avec deux objets. L'endpoint GET /stats/emissions retourne l'empreinte carbone moyenne d'un trajet en train comparée à celle d'un vol équivalent, permettant au tableau de bord d'afficher le bénéfice environnemental du train. L'endpoint GET /stats/operateurs retourne le volume de trajets par opérateur ferroviaire, trié par ordre décroissant. L'endpoint GET /stats/trajets/map retourne un tableau de segments géographiques, chacun décrivant une paire de coordonnées GPS de départ et d'arrivée, nécessaires pour tracer les lignes du réseau sur la carte Folium. Enfin, l'endpoint GET /docs donne accès à la documentation interactive Swagger générée automatiquement.

Les endpoints /trajets et tous les endpoints /stats sont soumis à un rate limiting, c'est-à-dire une limitation du débit de requêtes, car ce sont eux qui exécutent les requêtes SQL les plus coûteuses sur la base de données.

## 3.5 Sécurité

Deux mécanismes de sécurité distincts sont implémentés directement dans main.py. Il est important de comprendre que ces mécanismes sont dans main.py et non dans les fichiers de routes individuels, car ils doivent s'appliquer de façon transversale à l'ensemble des appels, sans qu'un développeur ait besoin d'y penser lors de l'écriture de chaque nouveau endpoint.

Le premier mécanisme est le rate limiting, mis en œuvre grâce à la bibliothèque slowapi. Le rate limiting, que l'on peut traduire par limitation du débit, répond à un problème concret : sans cette protection, un script automatisé malveillant pourrait envoyer des milliers de requêtes par seconde à l'API, épuisant les connexions disponibles à la base de données et rendant le service indisponible pour tous les utilisateurs légitimes. C'est ce qu'on appelle une attaque par déni de service, ou DoS. Notre implémentation limite à soixante requêtes par minute et par adresse IP l'accès aux endpoints /trajets et /stats. Ce seuil est largement suffisant pour un usage humain normal, y compris pour des scripts de test automatisés raisonnables, mais bloque le scraping massif. Lorsque cette limite est dépassée, l'API répond avec le code HTTP 429, qui signifie "Too Many Requests" ou "Trop de requêtes" en français, accompagné d'un message en JSON invitant le client à patienter soixante secondes avant de réessayer. L'implémentation avec slowapi s'effectue en deux lignes : une déclaration du limiter avec la clé d'identification par adresse IP et la configuration d'un gestionnaire d'erreur personnalisé dans main.py, et une annotation @limiter.limit("60/minute") ajoutée à chaque fonction d'endpoint concernée dans les fichiers de routes.

Le second mécanisme est l'injection automatique de quatre headers de sécurité HTTP dans chaque réponse de l'API, réalisée via un middleware. Un header HTTP est un champ de métadonnée envoyé en en-tête de chaque réponse, invisible pour l'utilisateur final mais interprété par le navigateur pour ajuster son comportement de sécurité. Ces quatre headers couvrent quatre vecteurs d'attaque distincts.

Le header X-Content-Type-Options avec la valeur nosniff interdit aux navigateurs de deviner le type d'un fichier à partir de son contenu. Sans ce header, un navigateur peut décider qu'un fichier texte contenant du code JavaScript est en réalité un script exécutable, ouvrant la voie à des attaques dites de MIME sniffing où un attaquant parvient à faire exécuter du code malveillant déguisé en données inoffensives.

Le header X-Frame-Options avec la valeur DENY interdit l'intégration de l'API dans une iframe d'une autre page web. Sans ce header, un attaquant pourrait créer une page piégée qui charge notre interface en transparence par-dessus un bouton légitime, amenant l'utilisateur à cliquer sur notre interface sans le savoir : c'est le principe du clickjacking, une attaque permettant de voler des clics et de tromper l'utilisateur sur ce qu'il valide réellement.

Le header X-XSS-Protection avec la valeur 1; mode=block active le filtre antiinjection de scripts croisés des navigateurs plus anciens qui ne supportent pas encore la Content Security Policy. Une injection XSS, pour Cross-Site Scripting, est une attaque où du code JavaScript malveillant est injecté dans une réponse HTTP puis exécuté par le navigateur de la victime, permettant de voler des cookies ou de réaliser des actions en son nom.

Le header Referrer-Policy avec la valeur strict-origin-when-cross-origin contrôle les informations de provenance transmises lors des requêtes vers d'autres domaines. Sans cette restriction, le navigateur peut inclure l'URL complète de la page précédente dans chaque requête vers des ressources externes, exposant potentiellement des informations structurelles sur la navigation de l'utilisateur.

## 3.6 Documentation automatique

FastAPI génère automatiquement une interface Swagger UI accessible à l'adresse /docs. Swagger UI est une application web intégrée dans FastAPI qui lit les annotations Python du code source et en déduit automatiquement la liste complète des endpoints, leurs paramètres attendus, les schémas de données en entrée et en sortie, et les codes de réponse possibles. Cette documentation est donc toujours synchronisée avec le code par construction : il est impossible qu'un endpoint existe dans le code sans apparaître dans la documentation, et impossible qu'un endpoint soit documenté avec des paramètres différents de ceux réellement attendus par le code. Depuis l'interface Swagger, il est possible de tester directement chaque endpoint sans aucun outil externe : on saisit les paramètres dans un formulaire web, on clique sur Execute, et la réponse JSON s'affiche immédiatement. C'est un avantage considérable pour l'intégration avec les partenaires d'ObRail Europe et pour les tests manuels pendant le développement, car tout nouveau développeur peut explorer l'API sans avoir à lire le code source.

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

## 5.1 Pourquoi écrire des tests ?

Pour comprendre la valeur d'une stratégie de tests, il est utile de se représenter ce qui se passe sans elle. Sans tests automatisés, la seule façon de vérifier qu'une modification du code n'a rien cassé est de lancer l'application manuellement et de cliquer sur chaque fonctionnalité pour s'assurer qu'elle fonctionne encore. Cette approche est laborieuse, incomplète, et ne passe pas à l'échelle : avec cent vingt-huit comportements à vérifier, une vérification manuelle complète prendrait des heures, et serait de toute façon peu fiable car la mémoire humaine oublie inévitablement des cas limites.

Les tests automatisés résolvent ce problème : ce sont des programmes Python qui appellent les fonctions et les endpoints du projet, vérifient que les résultats correspondent aux valeurs attendues, et signalent immédiatement toute divergence. Une fois écrits, ces tests s'exécutent en quelques secondes à chaque modification du code, sans intervention humaine. Si un développeur modifie la formule de calcul des émissions de CO2 et que ce changement produit une valeur différente de celle attendue, le test correspondant échoue instantanément, avant même que le code soit publié.

Dans le contexte d'un projet industrialisé comme le MSPR3, les tests ne sont pas un luxe : ils sont la condition sine qua non de la livraison continue. Sans tests, il est impossible de savoir si une image Docker construite automatiquement est déployable en production. Les tests sont ce qui transforme le pipeline CI/CD d'une simple chaîne de compilation en un vrai mécanisme de garantie qualité.

## 5.2 La pyramide des tests comme principe directeur

Avant de décrire chaque type de test, il est important de comprendre le principe qui guide leur organisation : la pyramide des tests, concept introduit par Mike Cohn dans son ouvrage Succeeding with Agile. Cette pyramide représente la distribution idéale des tests dans un projet : une large base de tests unitaires en bas, une couche intermédiaire de tests d'intégration, et un sommet plus étroit de tests de bout en bout.

Cette forme n'est pas arbitraire : elle reflète un compromis entre vitesse d'exécution, coût de maintenance et niveau de confiance apporté. Un test unitaire s'exécute en quelques millisecondes, ne nécessite aucune infrastructure, et si un test échoue il est immédiatement clair quelle fonction est en cause. Un test d'intégration prend quelques secondes, nécessite une base de données de test, et couvre un périmètre plus large mais plus difficile à diagnostiquer en cas d'échec. Un test de bout en bout prend plusieurs secondes à plusieurs minutes, nécessite la stack complète, et son échec peut avoir des dizaines de causes possibles. Si on inversait la pyramide en écrivant principalement des tests e2e, la suite de tests serait lente, coûteuse, fragile, et les développeurs finiraient par ne plus l'exécuter localement.

Dans notre projet, la pyramide est respectée : quatre-vingt-onze tests backend dont une majorité de tests unitaires et d'intégration, trente et un tests dashboard également centrés sur les fonctions unitaires, et seulement six tests de bout en bout Playwright ciblant les parcours utilisateur les plus critiques.

## 5.3 Les cinq types de tests

Le projet met en œuvre une stratégie de tests à cinq niveaux complémentaires, chacun correspondant à une granularité différente de vérification et à une catégorie distincte de problèmes détectables.

Les tests unitaires, annotés avec le marqueur pytest @pytest.mark.unit, constituent le niveau de vérification le plus fin. Ils testent une seule fonction de façon totalement isolée du reste du système : sans base de données, sans serveur HTTP, sans réseau. Pour que ce principe d'isolation soit respecté, les dépendances externes d'une fonction sont remplacées par des objets factices appelés mocks, qui simulent le comportement attendu sans exécuter réellement les opérations coûteuses. Un test unitaire doit être instantané, déterministe, c'est-à-dire qu'il produit toujours le même résultat pour les mêmes entrées, et compréhensible par un lecteur qui ne connaît pas l'ensemble du projet. Par exemple, un test unitaire de la fonction de normalisation des noms de gares vérifie que normalize_name("PARIS NORD") retourne "Paris Nord", et que normalize_name("münchen hbf") retourne "München Hbf", sans jamais interroger la base de données ni démarrer un serveur.

Les tests d'intégration, annotés @pytest.mark.integration, testent un endpoint complet depuis la requête HTTP jusqu'à la réponse JSON, en utilisant une vraie base de données de test. Là où le test unitaire vérifie qu'une pièce individuelle fonctionne seule, le test d'intégration vérifie que les pièces s'assemblent correctement. Dans notre projet, un test d'intégration typique ressemble à ceci : le test envoie une requête GET /gares au client de test FastAPI, reçoit la réponse JSON, et vérifie que le code HTTP est 200, que le corps de la réponse est un tableau non vide, et que chaque gare dans ce tableau possède les champs id_uic, nom, latitude et longitude. Si la couche routes ne transmet pas correctement les paramètres à la couche service, ou si la couche service ne construit pas correctement la requête SQL, ou si la couche schéma oublie de sérialiser un champ, le test d'intégration le détecte.

Les tests de contrat, annotés @pytest.mark.contract, vérifient que la forme des réponses de l'API reste stable au fil du temps. Le terme contrat désigne ici l'engagement implicite que le backend prend vis-à-vis du frontend : si le backend renvoie aujourd'hui un objet avec les clés id, nom et coordonnees, le frontend peut programmer son affichage en se basant sur ces clés. Si un développeur renomme ensuite la clé coordonnees en localisation, le frontend afficherait des données vides sans aucun message d'erreur explicite, ce qui serait difficile à diagnostiquer. Le test de contrat évite ce scénario : il vérifie explicitement la présence et le type de chaque champ de la réponse, si bien que tout changement de forme déclenche immédiatement un échec visible.

Les tests de qualité, annotés @pytest.mark.quality, vérifient la cohérence métier des données issues de l'ETL Talend. Ces tests répondent à des questions comme : y a-t-il des gares dont les coordonnées GPS sont en dehors des limites géographiques de l'Europe ? Y a-t-il des doublons d'identifiants dans la table des trajets ? Les émissions de CO2 sont-elles toutes des nombres positifs ? Ces vérifications sont impossibles à détecter par les autres types de tests car elles portent sur le contenu des données et non sur la structure du code. Elles sont particulièrement précieuses après chaque exécution de l'ETL.

Enfin, les tests de bout en bout, dits end-to-end ou e2e, constituent le niveau de vérification le plus réaliste et le plus proche de l'expérience réelle d'un utilisateur. Ils pilotent un vrai navigateur web, Chromium en l'occurrence, pour simuler des parcours utilisateur complets sur l'interface Streamlit. Un test e2e peut vérifier par exemple que lorsqu'un utilisateur ouvre le tableau de bord, la page Observatoire s'affiche correctement, que le titre "ObRail Europe" est visible, que les quatre métriques principales sont présentes, et que le graphique en anneau se charge sans erreur JavaScript. Ces tests détectent des catégories d'erreurs invisibles aux autres niveaux : une incompatibilité entre deux versions de bibliothèques, un problème de réseau entre le frontend et le backend dans l'environnement Docker, ou une régression dans l'interface utilisateur causée par une mise à jour de Streamlit.

## 5.4 Organisation des tests et rôle de conftest.py

Le projet compte au total cent vingt-huit tests répartis en trois suites distinctes. La suite backend comprend quatre-vingt-onze tests organisés dans huit fichiers. La suite dashboard comprend trente et un tests dans trois fichiers. La suite de tests de bout en bout comprend six tests dans deux fichiers.

Pour comprendre l'organisation des tests backend, il est essentiel de comprendre le rôle du fichier conftest.py, qui est un fichier spécial de pytest. Dans pytest, un fichier conftest.py définit des fixtures, terme technique désignant des ressources partagées entre plusieurs tests. Une fixture est une fonction décorée avec @pytest.fixture qui est exécutée automatiquement avant les tests qui en ont besoin, et qui peut effectuer un nettoyage automatiquement après. Quand un test déclare un paramètre dont le nom correspond à une fixture, pytest l'injecte automatiquement sans que le test n'ait à l'instancier lui-même.

Le conftest.py backend déclare la fixture db_session qui est la plus importante du projet. Avant chaque test, cette fixture crée une base de données SQLite en mémoire, c'est-à-dire une base temporaire qui vit uniquement dans la RAM du processus et disparaît à la fin du test. SQLite est choisi pour les tests plutôt que PostgreSQL pour deux raisons pratiques : il ne nécessite aucune installation ni aucun serveur séparé, et il est extrêmement rapide car les accès se font directement en mémoire. SQLAlchemy supporte les deux moteurs avec une configuration minimale.

Cette base de test est ensuite peuplée avec des données connues et maîtrisées : quatre pays représentant la France, l'Allemagne, l'Italie et l'Autriche avec leurs codes ISO, six gares couvrant Paris Nord, Paris Lyon, Berlin Hbf, München Hbf, Milano Centrale et Wien Hbf avec leurs coordonnées GPS réelles, trois opérateurs ferroviaires SNCF, ÖBB Nightjet et Deutsche Bahn, trois lignes avec leur type jour ou nuit, quatre trajets complets avec leurs identifiants, leurs itinéraires détaillant les arrêts intermédiaires, et leurs émissions de CO2 correspondantes. Ces données de test sont représentatives mais limitées : elles permettent de couvrir tous les cas de figure sans alourdir l'exécution des tests.

L'intérêt décisif de cette approche est l'isolation complète entre les tests. Comme chaque test reçoit une base de données fraîche dans l'état initial défini par la fixture, l'ordre d'exécution des tests est sans importance, et aucun test ne peut polluer l'état d'un autre. Si un test insère un enregistrement dans la base pour vérifier un cas particulier, cet enregistrement disparaît automatiquement à la fin du test, sans que le test suivant en soit affecté.

La fixture client, également définie dans conftest.py, crée un client de test FastAPI en utilisant la base SQLite préparée par db_session. Ce client se comporte exactement comme un client HTTP réel, avec la différence qu'il court-circuite le réseau et exécute les requêtes directement en mémoire, ce qui le rend instantané. Les tests d'intégration utilisent ce client pour envoyer des requêtes HTTP simulées et inspecter les réponses.

## 5.5 Les outils de test en détail

pytest est le framework de test retenu pour l'ensemble du projet. pytest détecte automatiquement les fichiers de test en cherchant les fichiers dont le nom commence par test_, puis les fonctions dont le nom commence par test_ à l'intérieur de ces fichiers, sans qu'aucune configuration explicite ne soit nécessaire. Il propose un système de marqueurs avec @pytest.mark.nom qui permet de filtrer les tests lors de l'exécution : la commande pytest -m unit n'exécute que les tests unitaires, ce qui est utile pour une vérification rapide pendant le développement. pytest génère des rapports d'erreur très lisibles : en cas d'échec, il affiche la ligne problématique, les valeurs attendues et les valeurs obtenues, et la pile d'appels complète. Il calcule également le taux de couverture de code, c'est-à-dire le pourcentage des lignes du code source qui ont été exécutées par au moins un test, ce qui aide à identifier les zones du code non couvertes.

Playwright est l'outil retenu pour les tests de bout en bout. Playwright est une bibliothèque développée par Microsoft qui permet de contrôler un navigateur web par programme depuis Python. Elle supporte Chromium, Firefox et WebKit. Dans notre cas, Playwright pilote Chromium en mode headless, c'est-à-dire sans fenêtre graphique visible, ce qui permet de l'exécuter dans des environnements sans interface graphique comme les serveurs CI/CD. Un test Playwright typique ressemble à ceci : le test ouvre une page à l'URL du tableau de bord Streamlit, attend que l'élément HTML avec le texte "ObRail" soit visible, clique sur le lien de navigation vers la page Observatoire, vérifie que le titre de la page change, et confirme que les métriques s'affichent. Playwright gère automatiquement les délais d'attente, en réessayant de trouver un élément jusqu'à un timeout configurable.

Ruff sert de linter, terme désignant un outil d'analyse statique du code. Un linter lit le code source sans l'exécuter et détecte les problèmes de style, les erreurs potentielles et les non-conformités aux conventions. Ruff vérifie par exemple qu'il n'y a pas de variables importées mais non utilisées, pas de lignes trop longues, pas d'indentation incohérente, pas de comparaisons incorrectes comme l'utilisation de == au lieu de is pour comparer à None. Ruff remplace avantageusement les outils plus anciens Flake8 pour le style et isort pour l'ordre des imports, car il est plusieurs centaines de fois plus rapide, réécrit en Rust, et produit des messages d'erreur plus clairs avec souvent une suggestion de correction automatique.

## 5.6 Le pipeline GitHub Actions en détail

Pour comprendre ce qu'est le pipeline GitHub Actions, il faut d'abord comprendre ce qu'est l'intégration continue. Dans un projet collaboratif, plusieurs développeurs modifient le code en parallèle sur des branches séparées. Lorsqu'une branche est prête à être fusionnée dans la branche principale, il faut vérifier qu'elle ne casse rien. L'intégration continue automatise cette vérification : à chaque push de code sur le dépôt, un serveur distant exécute automatiquement les tests et signale les résultats. GitHub Actions est l'outil qui permet de définir et d'exécuter ces vérifications directement depuis le dépôt GitHub, sans infrastructure de CI/CD externe à configurer.

Le pipeline est défini dans le fichier .github/workflows/main.yml, un fichier en format YAML qui décrit une séquence de jobs et d'étapes. Chaque job s'exécute sur une machine virtuelle Ubuntu fraîche fournie par GitHub gratuitement pour les projets publics. Le pipeline se déclenche automatiquement à chaque push sur les branches main et develop et à chaque Pull Request vers main. Il est composé de neuf jobs qui forment un graphe de dépendances.

Le job changes est le premier à s'exécuter sur chaque déclenchement. Il utilise l'action dorny/paths-filter pour analyser la liste des fichiers modifiés dans le commit en cours et déterminer quels dossiers ont été touchés parmi dashboard, backend et talend. Il expose ensuite les résultats comme des sorties booléennes que les jobs suivants peuvent lire pour décider s'ils doivent s'exécuter. Ce mécanisme est une optimisation importante : si seul le fichier README.md a été modifié, il n'y a pas lieu de relancer l'ETL complet ni de reconstruire les images Docker. Cette optimisation peut réduire le temps d'exécution du pipeline de plusieurs minutes sur des commits de documentation.

Le job frontend-test s'exécute si des fichiers du dossier dashboard ont changé. Il utilise la condition if: needs.changes.outputs.dashboard == 'true'. Sur une machine Ubuntu fraîche, il installe Python 3.12 et les dépendances du tableau de bord listées dans requirements.txt, puis lance Ruff pour vérifier la syntaxe du code. Si Ruff détecte une erreur de style, le job s'arrête immédiatement et signale l'échec. Sinon, il lance les trente et un tests pytest du dashboard, qui testent les fonctions de génération de graphiques Plotly, la logique du client HTTP, et les composants d'icônes SVG.

Le job backend-test s'exécute si des fichiers du dossier backend ont changé. Sa particularité par rapport au job frontend est qu'il démarre un service PostgreSQL en parallèle de la machine Ubuntu principale. Cette configuration est possible grâce aux services GitHub Actions, qui permettent de lancer des conteneurs Docker adjacents à la machine de build. Le job configure les variables d'environnement de connexion à ce PostgreSQL de test, installe Python 3.12 et les dépendances du backend, lance Ruff, puis exécute les quatre-vingt-onze tests pytest en ciblant cette base de données réelle. Le fait d'utiliser PostgreSQL pour les tests du backend en CI, là où conftest.py utilise SQLite en développement local, garantit que les fonctionnalités spécifiques à PostgreSQL comme certains types de colonnes ou des comportements de tri sont également vérifiés.

Le job talend-lint valide l'intégrité du pipeline ETL sans l'exécuter complètement. Il lance ShellCheck, un outil d'analyse statique spécialisé pour les scripts bash, pour détecter les erreurs communes comme une variable non initialisée, un test mal formé ou une commande pouvant échouer silencieusement. Il effectue ensuite un scan de secrets avec l'outil truffleHog pour vérifier qu'aucun mot de passe, clé API ou token d'authentification n'est présent en clair dans les scripts. Il vérifie la présence des neuf fichiers JAR compilés correspondant aux neuf jobs Talend, afin de s'assurer qu'aucun JAR n'a été accidentellement supprimé du dépôt. Il vérifie enfin l'intégrité de chaque JAR en le décompressant et en contrôlant que son contenu est un fichier ZIP Java valide.

Le job talend-etl-dryrun exécute l'intégralité des neuf jobs Talend sur une base de test PostgreSQL provisionnée dans GitHub Actions en repartant du dernier dump SQL disponible dans le dépôt. C'est le test d'intégration le plus lourd du pipeline : il prend plusieurs minutes et consomme beaucoup de ressources, car il exécute réellement les transformations de données. Les logs de chaque job sont archivés comme artefact dans l'interface GitHub Actions et conservés quatorze jours, ce qui permet à l'équipe de consulter le détail de chaque exécution pour diagnostiquer les échecs.

Le job e2e-test s'exécute après la validation des tests frontend et backend, grâce à la condition needs: [frontend-test, backend-test]. Il utilise Docker Compose pour lancer la stack complète des cinq services sur la machine Ubuntu de GitHub Actions. Après la commande docker compose up -d, le job attend que Streamlit réponde effectivement sur le port 8501 via une boucle de vérification qui tente une requête HTTP toutes les cinq secondes pendant soixante secondes au maximum. Cette attente est nécessaire car les conteneurs Docker mettent plusieurs secondes à démarrer complètement après que la commande up a retourné. Une fois Streamlit disponible, le job installe Playwright et son navigateur Chromium, puis exécute les six tests de bout en bout. La clause finally garantit que docker compose down est systématiquement exécuté à la fin, quelle que soit l'issue des tests, pour libérer les ressources de la machine et éviter des interférences avec les exécutions suivantes.

Les jobs docker-frontend et docker-backend s'exécutent exclusivement sur la branche main, après que les tests correspondants ont réussi. Cette restriction est explicite dans le fichier YAML avec la condition if: github.ref == 'refs/heads/main'. Ces jobs construisent les images Docker du frontend et du backend depuis leurs Dockerfile respectifs et les poussent vers le GitHub Container Registry, accessible à l'adresse ghcr.io/nom-du-projet. Chaque image est taguée avec trois références simultanément : le nom de la branche main pour les déploiements stables, le SHA du commit pour une traçabilité exacte permettant de savoir quelle version précise est déployée, et le tag latest pour que docker pull sans spécification de version récupère toujours la dernière build valide.

Le job summary s'exécute en dernier avec la condition always() qui garantit son exécution même si les jobs précédents ont échoué. Il génère un tableau récapitulatif en Markdown affiché directement dans l'onglet Actions de l'interface GitHub, montrant le statut de chaque bloc du pipeline. Ce tableau est particulièrement utile pour comprendre d'un coup d'œil ce qui a réussi et ce qui a échoué lors d'un run problématique.

## 5.7 De l'intégration continue à la livraison continue

L'intégration continue et la livraison continue sont dans le même pipeline, mais s'appliquent à des contextes différents et servent des objectifs complémentaires. L'intégration continue répond à la question : ce nouveau code est-il correct et compatible avec le reste du projet ? La livraison continue répond à la question : comment déployer ce code validé de façon reproductible et traçable ?

Sur une Pull Request, seuls les jobs de test sont exécutés : le code soumis doit passer l'intégralité des cent vingt-huit tests avant de pouvoir être fusionné dans la branche principale. GitHub peut être configuré pour bloquer automatiquement la fusion d'une Pull Request dont les tests n'ont pas réussi, ce qui garantit que la branche main ne contient jamais de code défectueux connu. C'est le principe de la "green build" : on ne fusionne que ce qui est vert.

Sur un push direct sur main, si les tests réussissent, les images Docker sont automatiquement construites et poussées vers le registre. Cette architecture garantit une propriété essentielle : l'image déployée en production est exactement celle qui a été testée, construite depuis le même commit et avec les mêmes dépendances. Il n'y a aucune étape manuelle entre la validation des tests et la production de l'artefact déployable, ce qui élimine la classe d'erreurs dites "ça marchait sur ma machine" où une différence d'environnement entre le développeur et le serveur de production provoque des bugs inexplicables.

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

## 6.5 SLI, SLO et SLA : définir ce que signifie "ça marche"

La supervision technique ne se réduit pas à observer des graphiques : elle suppose d'abord de définir précisément ce que signifie le fait qu'un service fonctionne correctement. Le domaine de la fiabilité des sites, connu sous l'acronyme SRE pour Site Reliability Engineering et popularisé par Google, propose trois concepts complémentaires pour formaliser cette définition : les SLI, les SLO et les SLA.

Un SLI, pour Service Level Indicator, est une mesure quantitative d'un aspect du comportement du service. Dans notre projet, trois SLI sont instrumentés directement dans Prometheus. Le premier est la disponibilité, mesurée par la métrique up qui vaut 1 si le backend répond au scraping et 0 sinon. Le deuxième est la latence, mesurée par l'histogramme http_request_duration_seconds qui enregistre la durée de chaque requête. Le troisième est le taux d'erreurs, mesuré comme la proportion de requêtes retournant un code HTTP 5xx sur le total des requêtes.

Un SLO, pour Service Level Objective, est la valeur cible que l'on se fixe pour un SLI donné. Il représente l'engagement interne de l'équipe technique envers elle-même. Pour ObRail Europe, on pourrait définir les SLO suivants en s'appuyant sur les métriques déjà collectées : une disponibilité de 99 % sur une période glissante de trente jours, ce qui tolère un peu moins de sept heures d'indisponibilité par mois ; une latence au percentile 95 inférieure à 500 millisecondes pour les endpoints de statistiques, qui sont les plus sollicités ; et un taux d'erreurs 5xx inférieur à 1 % sur une fenêtre de cinq minutes. Ces seuils sont directement observables dans le dashboard Grafana grâce aux panneaux de latence p95 et de taux d'erreurs déjà configurés.

Un SLA, pour Service Level Agreement, est l'engagement contractuel formel vis-à-vis d'un partenaire externe, avec des conséquences définies en cas de non-respect. Dans le contexte d'ObRail Europe, le SLA serait négocié avec la Commission européenne ou les opérateurs ferroviaires partenaires qui consomment les données via l'API. Le SLA est généralement légèrement moins ambitieux que le SLO interne, pour laisser une marge de manœuvre entre la réalité opérationnelle et l'engagement public.

Cette distinction SLI/SLO/SLA est importante car elle permet de distinguer ce qu'on mesure, ce qu'on vise, et ce qu'on promet, trois questions qui ont des réponses différentes et qui impliquent des acteurs différents dans l'organisation.

## 6.6 Reproductibilité garantie

Lors de la mise en place du monitoring, un problème de reproductibilité a été identifié et documenté dans le fichier why.md. Grafana génère un identifiant unique aléatoire, appelé UID, pour chaque source de données au premier démarrage. Sur une deuxième machine, cet identifiant est différent. Or le fichier JSON du dashboard référence cet UID pour savoir quelle source de données utiliser. Résultat : les panneaux du dashboard s'affichaient vides sur toute machine autre que celle où le dashboard avait été initialement créé.

La solution adoptée consiste à fixer explicitement l'UID de la source de données Prometheus à la valeur littérale obrail-prometheus dans le fichier de provisioning Grafana. Le dashboard JSON référence ensuite cet UID fixe et non plus un identifiant aléatoire. Grâce au provisioning automatique via les volumes Docker, qui charge les dashboards et les datasources au démarrage depuis des fichiers du dépôt, le dashboard s'affiche correctement sur n'importe quelle machine, en CI comme en déploiement, sans la moindre intervention manuelle.

---

# CHAPITRE 7 : DÉPLOIEMENT

## 7.1 La méthodologie 12-factor appliquée au projet

Avant de décrire le déploiement concret, il est utile de situer notre architecture dans le cadre de la méthodologie 12-factor, formulée par Adam Wiggins de Heroku en 2011. Cette méthodologie définit douze principes qui, lorsqu'ils sont respectés, garantissent qu'une application web est déployable de façon fiable dans n'importe quel environnement cloud. Elle est devenue la référence de facto pour les applications conteneurisées.

Le premier facteur, Base de code unique, est respecté : l'ensemble du projet, backend, frontend, configuration Prometheus, Dockerfiles et pipeline CI/CD, est versionné dans un seul dépôt Git. Le deuxième facteur, Dépendances explicites, est respecté : chaque composant déclare ses dépendances dans un fichier requirements.txt et les isole dans son propre conteneur Docker, sans supposer qu'une bibliothèque soit préinstallée sur le système hôte. Le troisième facteur, Configuration dans l'environnement, est respecté : les valeurs qui changent entre les environnements, comme l'URL de la base de données, le mot de passe PostgreSQL et les secrets applicatifs, sont stockées dans des variables d'environnement injectées via le fichier .env en local et via les GitHub Secrets en CI/CD, et jamais codées en dur dans le code source. Le quatrième facteur, Services externes comme ressources attachées, est respecté : PostgreSQL, Prometheus et Grafana sont des services attachés identifiés par leur URL, et on pourrait les remplacer par des instances managées dans le cloud en changeant uniquement les variables d'environnement. Le sixième facteur, Processus sans état, est respecté par le backend FastAPI : chaque requête est traitée indépendamment, sans que le serveur conserve de session entre les requêtes. Le septième facteur, Liaison de port, est respecté : chaque service expose ses fonctionnalités via un port réseau déclaré dans docker-compose.yml, sans dépendre d'un serveur web externe. Le huitième facteur, Concurrence, est adressé par Uvicorn qui supporte plusieurs workers. Le neuvième facteur, Jetabilité, est respecté : les conteneurs Docker démarrent en quelques secondes et s'arrêtent proprement à réception du signal SIGTERM, sans laisser de données corrompues. Le onzième facteur, Journaux comme flux d'événements, est respecté : tous les services écrivent leurs journaux sur la sortie standard, et Docker les collecte sans que l'application ait à gérer des fichiers de log.

Cette conformité à la méthodologie 12-factor n'est pas un objectif en soi mais une conséquence naturelle des choix techniques effectués. Elle garantit que l'application peut être déployée sur Fly.io, Render, ou Oracle Cloud sans modification du code, uniquement en adaptant les variables d'environnement.

## 7.2 Déploiement local avec Docker Compose

Le déploiement local de la stack complète s'effectue avec une seule commande : docker compose up -d --build. Docker lit le fichier docker-compose.yml qui définit les cinq services du projet et les assemble dans un réseau privé nommé obrail.

Le service PostgreSQL démarre en premier et charge automatiquement le dump SQL du dépôt, ce qui initialise toutes les tables avec les données réelles sans intervention manuelle. Le service backend attend que PostgreSQL soit pleinement opérationnel grâce au mécanisme de condition de démarrage depends_on avec la vérification de santé service_healthy. Une fois PostgreSQL prêt, le backend démarre et expose l'API sur le port 8000. Le frontend Streamlit, Prometheus et Grafana démarrent ensuite de façon parallèle.

Des volumes Docker persistants garantissent que les données survivent aux redémarrages : postgres_data conserve les données de la base, prometheus_data conserve l'historique des métriques sur trente jours, et grafana_data conserve les configurations. Les ports exposés sur la machine hôte sont le port 5433 pour PostgreSQL, le port 8000 pour le backend, le port 8501 pour le frontend, le port 9090 pour Prometheus et le port 3010 pour Grafana. Le port non standard 5433 pour PostgreSQL est un choix délibéré pour éviter les conflits avec une éventuelle instance PostgreSQL locale déjà en cours.

Le premier démarrage nécessite trois à cinq minutes en raison du téléchargement des images Docker et de la construction des images custom. Les démarrages suivants prennent trente secondes environ car les images sont mises en cache localement.

## 7.3 Build et push des images

Sur un push sur la branche main, après que les tests ont réussi, le pipeline GitHub Actions exécute automatiquement les jobs docker-backend et docker-frontend. Ces jobs construisent les images Docker depuis les Dockerfile de chaque composant, les taggent avec trois formats différents, le nom de la branche main pour les déploiements stables, le SHA du commit pour la traçabilité exacte de la version déployée, et le tag latest pour pointer vers la dernière version stable. Les images sont poussées vers GitHub Container Registry, accessible à l'adresse ghcr.io. Cette approche permet de déployer la dernière version validée en production avec une simple commande docker pull, sans avoir à reconstruire l'image localement.

## 7.4 Options de déploiement en ligne

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

## 8.2 Positionnement dans la maturité MLOps

Pour situer précisément ce projet dans la progression vers un système d'intelligence artificielle en production, il est utile de le positionner sur le modèle de maturité MLOps de Google, qui définit trois niveaux de sophistication croissante.

Le niveau 0, dit MLOps manuel, correspond à une situation où les modèles sont entraînés et déployés à la main, sans automatisation ni supervision. Le niveau 1, dit automatisation du pipeline ML, correspond à une situation où l'entraînement est déclenché automatiquement par de nouvelles données et où le modèle est monitoré en production. Le niveau 2, dit automatisation du pipeline CI/CD ML, correspond à une situation où la mise à jour du code du modèle déclenche automatiquement un entraînement, une validation et un déploiement, avec tests A/B et rollback automatique.

Le MSPR3 place ObRail Europe en position de démarrer directement au niveau 1 lors de l'intégration du premier modèle, ce qui est remarquable pour un prototype. Le pipeline CI/CD GitHub Actions fournit déjà le squelette dans lequel une étape d'entraînement automatique peut être insérée. La base PostgreSQL stocke les données d'entraînement dans un format propre et normalisé prêt à être consommé par scikit-learn, PyTorch ou TensorFlow via SQLAlchemy. Prometheus est déjà en place pour recevoir des métriques de dérive des données, de précision et de rappel en ajoutant simplement de nouveaux compteurs dans le service d'inférence. Les volumes Docker persistants peuvent stocker les artefacts d'entraînement, les checkpoints et les journaux d'évaluation entre les redémarrages. La conteneurisation garantit que le service d'inférence sera déployé dans les mêmes conditions que le reste de la stack.

## 8.3 Perspectives d'accueil d'un futur modèle d'intelligence artificielle

La prochaine étape naturelle consiste à implémenter un microservice de prédiction qui, à partir des données historiques des trajets stockées dans PostgreSQL, estimera la fréquentation future d'une ligne ou recommandera des optimisations de dessertes. Ce service s'inscrirait dans le réseau Docker existant, exposerait ses propres endpoints via FastAPI, et bénéficierait immédiatement du monitoring et de la couverture de tests mis en place dans ce MSPR3.

L'API expose les données ferroviaires au format JSON standardisé, ce que tout modèle d'apprentissage machine peut consommer facilement sans transformation supplémentaire. Le monitoring Prometheus peut être étendu pour suivre des métriques spécifiques aux modèles d'IA : la dérive des données d'entrée, c'est-à-dire la détection que la distribution des trajets observés s'éloigne de la distribution sur laquelle le modèle a été entraîné, signalerait automatiquement qu'un réentraînement est nécessaire. La précision et le rappel du modèle pourraient être publiés comme des métriques Prometheus et affichés dans un nouveau panneau Grafana dédié à la santé du modèle, au même titre que la latence de l'API aujourd'hui.

En ce sens, la valeur de ce projet ne réside pas seulement dans ce qu'il fait aujourd'hui, mais dans la robustesse de l'infrastructure qu'il établit pour demain. Chaque choix technique effectué dans ce MSPR3, de la normalisation 3NF de la base de données à la séparation en couches du backend, de la pyramide des tests à la méthodologie 12-factor du déploiement, constitue un fondement délibérément conçu pour accueillir la complexité supplémentaire qu'introduira l'intelligence artificielle dans le prochain cycle du projet.
