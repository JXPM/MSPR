# Ajouts à intégrer dans Documentation_MSPR3_.docx

Ce fichier regroupe trois sections rédigées dans le style de la documentation principale, prêtes à être copiées-collées dans Word.

- **Ajout 1** → s'insère dans le **Chapitre 5 — Tests et intégration continue**, idéalement après la section *5.4 Pipeline GitHub Actions* et avant la section *5.5 De l'intégration continue à la livraison continue*. La section sera renumérotée *5.5* et l'actuelle 5.5 devient 5.6.
- **Ajout 2** → s'insère également dans le **Chapitre 5**, en complément de la sous-section *5.2 Organisation des tests*, ou comme nouvelle sous-section *5.6 Couverture du code par les tests*.
- **Ajout 3** → s'ajoute en fin de document comme **Annexe A — Glossaire**, après le *Chapitre 8 Conclusion*.

---

## Ajout 1 — Section 5.5 Garde-fou local : pre-commit hooks

La pyramide des tests et le pipeline GitHub Actions garantissent qu'aucune régression ne passe la barrière du dépôt central. Mais ces deux dispositifs ne s'exécutent qu'à la création d'une Pull Request ou lors d'un push, c'est-à-dire après que le développeur a déjà rédigé son commit. Pour intercepter les défauts plus tôt, dès l'instant où le code est sur le point d'entrer dans l'historique Git, le projet met en place un troisième garde-fou : les *pre-commit hooks*.

Un pre-commit hook est un programme déclenché automatiquement par Git au moment d'un `git commit`. Si l'un des contrôles échoue, le commit est annulé et le développeur reçoit le détail de l'erreur dans son terminal. Cette boucle de retour locale permet de corriger les problèmes triviaux — espaces en fin de ligne, fichier sans saut de ligne final, secret oublié dans un script — sans attendre les quelques minutes que prend la CI.

Le projet utilise le framework `pre-commit`, configuré via le fichier `.pre-commit-config.yaml` à la racine du dépôt. Sa philosophie est délibérée : chaque hook reflète exactement un contrôle effectué par la CI. Cette correspondance un-pour-un évite la situation, fréquente dans les projets mal configurés, où la CI échoue alors que le commit est passé en local — ou inversement.

Quatre familles de contrôles sont activées. Les contrôles d'hygiène, fournis par le dépôt officiel `pre-commit-hooks`, suppriment les espaces en fin de ligne, ajoutent un saut de ligne final aux fichiers qui en manquent, valident la syntaxe des fichiers YAML et JSON, détectent les marqueurs de conflit Git oubliés, refusent les fichiers de plus de deux mégaoctets et signalent les clés privées commitées par mégarde. Les contrôles de style Python sont assurés par `ruff`, le même outil que la CI : il s'applique à `backend/app/` et à `dashboard/` à l'exclusion des dossiers de tests, avec correction automatique des erreurs réparables. Les scripts shell de l'ETL Talend sont validés par `shellcheck`, en niveau d'avertissement, exactement comme dans le job `talend-lint` de la CI. Enfin, un hook local en bash réplique la recherche de secrets en clair (motifs `password=`, `PGPASSWORD=`, `secret=`) dans les répertoires `talend/lancement`, `talend/planication` et `talend/execution_etl`.

Une attention particulière est portée à la liste d'exclusions globale, déclarée dans le bloc `exclude` en tête de fichier. Sont ignorés les fichiers générés par Talend (`talend/Jobs/`), les dumps SQL massifs (`talend/dump/`), les scripts batch Windows (`*.bat` et `*.ps1`) ainsi que les documents bureautiques (`documentations/`). Cette précaution est essentielle : sans elle, les hooks d'hygiène réécriraient les fins de ligne CRLF des fichiers Windows en LF Unix, ce qui casserait leur exécution sur les machines de l'équipe travaillant sous Windows.

L'activation est triviale pour un nouveau contributeur : `pip install pre-commit && pre-commit install`. La première commande installe l'outil, la seconde inscrit le hook dans le répertoire `.git/hooks` du dépôt local. À partir de cet instant, chaque commit déclenche automatiquement la suite de contrôles. Le développeur peut également exécuter manuellement l'ensemble des hooks sur tous les fichiers du dépôt avec `pre-commit run --all-files`, ce qui est utile lors de l'initialisation ou après une mise à jour majeure de la configuration.

Cette mise en place complète la stratégie qualité du projet en trois cercles concentriques : les pre-commit hooks filtrent au niveau du commit individuel, les tests pytest et Playwright filtrent au niveau de la branche locale, et le pipeline GitHub Actions filtre au niveau de l'intégration centrale. Aucun défaut n'a vocation à franchir simultanément ces trois barrières.

---

## Ajout 2 — Section 5.6 Couverture du code par les tests

Le nombre de tests, à lui seul, ne suffit pas à caractériser la qualité d'une suite. Une centaine de tests qui n'exercent que le chemin nominal d'une seule fonction laissent l'essentiel du code sans filet de sécurité. La métrique pertinente est la couverture de code, c'est-à-dire le pourcentage de lignes du projet effectivement exécutées au moins une fois lorsque la suite de tests est lancée.

Le projet mesure cette couverture grâce à `pytest-cov`, une extension de pytest qui s'appuie sur la bibliothèque `coverage.py`. À chaque exécution de la suite, l'outil instrumente le code source, enregistre les lignes traversées, et produit un rapport synthétique. Ce rapport est généré localement lors des exécutions manuelles et archivé comme artefact dans le pipeline GitHub Actions, conservé quatorze jours pour permettre le suivi de l'évolution dans le temps.

Sur la suite backend, qui regroupe quatre-vingt-onze tests, la couverture atteint **98 %** sur un total de trois cent quatre-vingt-huit instructions du dossier `app/`. Seules neuf instructions ne sont pas exercées, réparties principalement dans le module `app/database.py`, qui contient le code de gestion d'une connexion à PostgreSQL en environnement de production que les tests, eux, remplacent par une base SQLite en mémoire. Tous les modèles SQLAlchemy, tous les endpoints des routes, et la quasi-totalité des services métier sont couverts à 100 %.

Sur la suite dashboard, qui regroupe trente et un tests, la couverture atteint **67 %**. Cette valeur, plus modeste, s'explique par la nature même du tableau de bord : les composants de génération de cartes Folium dans `components/map.py` et certaines fonctions du client HTTP dans `services/api_service.py` sont exercés indirectement par les six tests Playwright de la suite e2e, qui pilotent un vrai navigateur et chargent réellement les pages. Les outils de mesure de couverture ne traversent pas cette frontière entre Python et le navigateur, si bien que ce code apparaît à tort comme non couvert dans le rapport unitaire alors qu'il est validé fonctionnellement.

Les tableaux suivants détaillent la répartition fichier par fichier.

**Couverture backend (extrait, 98 % au total)**

| Module                          | Instructions | Manquantes | Couverture |
| ------------------------------- | ------------ | ---------- | ---------- |
| `app/main.py`                   | 51           | 1          | 98 %       |
| `app/database.py`               | 14           | 4          | 71 %       |
| `app/models/` (8 fichiers)      | 81           | 0          | 100 %      |
| `app/routes/` (5 fichiers)      | 108          | 2          | 98 %       |
| `app/services/` (4 fichiers)    | 95           | 2          | 98 %       |
| `app/schemas/` (3 fichiers)     | 30           | 0          | 100 %      |
| **Total**                       | **388**      | **9**      | **98 %**   |

**Couverture dashboard (67 % au total)**

| Module                          | Instructions | Manquantes | Couverture |
| ------------------------------- | ------------ | ---------- | ---------- |
| `components/charts.py`          | 60           | 0          | 100 %      |
| `components/icons.py`           | 5            | 0          | 100 %      |
| `components/map.py`             | 26           | 26         | 0 % *      |
| `services/api_service.py`       | 87           | 33         | 62 % *     |
| **Total**                       | **178**      | **59**     | **67 %**   |

\* exercé fonctionnellement par les six tests Playwright e2e qui n'instrumentent pas le code unitaire.

Une couverture de 98 % sur le backend constitue un seuil largement supérieur aux pratiques courantes de l'industrie, qui considère 80 % comme un objectif solide pour un projet en production. Elle reflète la stratégie d'écriture de tests adoptée dès le début du projet : pour chaque endpoint nouvellement ajouté, au moins un test d'intégration valide le chemin nominal, un test de contrat valide la forme de la réponse, et un ou plusieurs tests unitaires valident les fonctions de service appelées en interne. Cette discipline, soutenue par la barrière du pipeline CI qui rejette toute Pull Request faisant chuter la couverture, garantit que la qualité ne se dégrade pas avec le temps.

---

## Ajout 3 — Annexe A Glossaire

Cette annexe regroupe les acronymes et termes techniques cités dans le rapport. Elle est conçue pour une lecture transverse au document : chaque entrée donne la signification de l'acronyme et un rappel concis de son rôle dans le projet.

| Terme | Signification et usage dans le projet |
| ----- | ------------------------------------- |
| **ACID** | Atomicity, Consistency, Isolation, Durability. Quatre propriétés garanties par PostgreSQL pour la fiabilité des transactions. Voir section 2.2. |
| **ADEME** | Agence de l'environnement et de la maîtrise de l'énergie. Source du facteur d'émission de 0,158 kg CO₂/passager·km utilisé dans le calcul de l'empreinte avion. |
| **API** | Application Programming Interface. Interface exposée par le backend pour permettre au frontend de récupérer les données. |
| **ARIA** | Accessible Rich Internet Applications. Ensemble d'attributs HTML pour rendre les interfaces accessibles aux lecteurs d'écran. Limité par Streamlit (voir section 4.4). |
| **ASGI** | Asynchronous Server Gateway Interface. Protocole asynchrone implémenté par Uvicorn pour gérer des milliers de connexions simultanées dans un seul processus. |
| **BEIS** | Department for Business, Energy and Industrial Strategy (Royaume-Uni). Référentiel britannique des facteurs d'émission. |
| **CI/CD** | Continuous Integration / Continuous Delivery. Pratique d'intégration et de livraison automatisées via le pipeline GitHub Actions du projet. |
| **CSV** | Comma-Separated Values. Format de fichier tabulaire utilisé notamment par les sources OpenStreetMap et GTFS. |
| **ETL** | Extract, Transform, Load. Pipeline de traitement de données implémenté avec Talend (chapitre 2.3). |
| **GTFS** | General Transit Feed Specification. Standard ouvert publié par Google pour les données de transport public, utilisé par la SNCF. |
| **HTTP** | HyperText Transfer Protocol. Protocole d'échange entre le frontend et le backend. |
| **JAR** | Java ARchive. Format d'archive Java utilisé pour distribuer les neuf jobs Talend compilés. |
| **JDBC** | Java Database Connectivity. API standard Java pour se connecter à PostgreSQL depuis les jobs Talend. |
| **JSON** | JavaScript Object Notation. Format d'échange textuel structuré utilisé par l'API REST. |
| **MCD** | Modèle Conceptuel de Données. Représentation graphique du schéma relationnel des dix tables (Figure 1). |
| **MLOps** | Machine Learning Operations. Discipline d'industrialisation des projets de ML, dont le projet adopte les principes (chapitre 8.2). |
| **MVCC** | Multi-Version Concurrency Control. Mécanisme PostgreSQL qui permet aux lectures de ne pas bloquer les écritures concurrentes. |
| **ORM** | Object-Relational Mapping. Traduction automatique entre objets Python et requêtes SQL, assurée par SQLAlchemy. |
| **p50, p95, p99** | Percentiles. Valeurs en dessous desquelles tombent respectivement 50 %, 95 % et 99 % des observations. Utilisés pour caractériser la latence de l'API. |
| **PostgreSQL** | Système de gestion de base de données relationnelle open source utilisé comme socle de stockage du projet. |
| **PromQL** | Prometheus Query Language. Langage d'interrogation des métriques Prometheus utilisé par Grafana et la page Supervision du dashboard. |
| **REST** | Representational State Transfer. Style architectural de l'API du projet, où chaque ressource est identifiée par une URL. |
| **RGAA** | Référentiel Général d'Amélioration de l'Accessibilité. Référentiel français d'accessibilité numérique. Le projet vise le niveau AA (chapitre 4.4). |
| **RGPD** | Règlement Général sur la Protection des Données. Règlement européen sur la vie privée. Conformité traitée au chapitre 2.5. |
| **RNCP** | Répertoire National des Certifications Professionnelles. Le titre visé est enregistré sous le numéro RNCP36581. |
| **SLA** | Service Level Agreement. Engagement contractuel public sur la qualité de service. Voir section 6.5. |
| **SLI** | Service Level Indicator. Mesure quantitative d'un aspect du service (disponibilité, latence, taux d'erreurs). Voir section 6.5. |
| **SLO** | Service Level Objective. Cible interne fixée pour un SLI. Voir section 6.5. |
| **SQL** | Structured Query Language. Langage standard d'interrogation des bases de données relationnelles. |
| **SRE** | Site Reliability Engineering. Discipline d'ingénierie de la fiabilité formalisée par Google, dont le projet emprunte le vocabulaire SLI/SLO/SLA. |
| **SVG** | Scalable Vector Graphics. Format vectoriel utilisé pour les icônes du dashboard. |
| **TEN-T** | Trans-European Transport Network. Programme européen de réseau transeuropéen de transport, cadre stratégique du projet. |
| **UID** | Unique Identifier. Identifiant unique généré par Grafana pour chaque source de données. Sa nature aléatoire a posé un problème de reproductibilité résolu en section 6.6. |
| **UIC** | Union Internationale des Chemins de fer. Code à sept chiffres identifiant chaque gare européenne, utilisé comme clé primaire de la table `gare`. |
| **URL** | Uniform Resource Locator. Adresse identifiant chaque ressource exposée par l'API. |
| **WAL** | Write-Ahead Logging. Mécanisme de journalisation de PostgreSQL qui garantit la durabilité des transactions. |
| **WSGI** | Web Server Gateway Interface. Protocole synchrone, ancêtre d'ASGI, moins adapté à la concurrence élevée. |
| **XSS** | Cross-Site Scripting. Famille d'attaques par injection de script, contre laquelle le header HTTP `X-XSS-Protection` apporte une protection résiduelle dans les anciens navigateurs (chapitre 3.4). |
| **YAML** | YAML Ain't Markup Language. Format de configuration utilisé par Docker Compose, GitHub Actions et le fichier `.pre-commit-config.yaml`. |
