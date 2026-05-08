Voici le guide **sans aucune commande `make`**, uniquement du Docker natif. Parfait pour toi qui as déjà Docker mais pas `make`.

---

# LANCEMENT — Guide de démarrage du projet ObRail Europe

> Ce guide fonctionne sur **Windows, macOS et Linux**.
> Tu as déjà Docker installé. Pas besoin de `make`.
> Chaque commande est expliquée ligne par ligne.

---

## Sommaire

1. [Prérequis](#prérequis)
2. [Récupérer le projet](#étape-1--récupérer-le-projet)
3. [Configurer le fichier `.env`](#étape-2--configurer-le-fichier-env)
4. [Lancer la stack](#étape-3--lancer-toute-la-stack)
5. [Vérifier que tout fonctionne](#étape-4--vérifier-que-tout-fonctionne)
6. [Commandes du quotidien](#commandes-du-quotidien)
7. [Accéder aux services](#accéder-aux-services-dans-le-navigateur)
8. [Lancer les tests](#lancer-les-tests)
9. [Base de données](#base-de-données)
10. [Workflow collaboratif](#workflow-collaboratif-github)
11. [Dépannage](#dépannage)
12. [Déploiement en ligne gratuit](#déploiement--mettre-le-projet-en-ligne-gratuitement)

---

## Prérequis

### Vérifie que Docker est bien installé

**Ouvre un terminal :**

- **Windows** → utilise `Git Bash` ou `PowerShell`
- **macOS / Linux** → n'importe quel terminal

**Tape ces commandes :**

```bash
docker --version
```

*Ce que ça fait* : affiche la version de Docker installée.
*Résultat attendu* : `Docker version 24.x.x` ou supérieur.

```bash
docker compose version
```

*Ce que ça fait* : affiche la version de Docker Compose.
*Résultat attendu* : `Docker Compose version v2.x.x`.

> Si ces commandes ne fonctionnent pas → Docker n'est pas installé ou pas démarré.
> Lance Docker Desktop (Windows/macOS) ou démarre le service Docker (Linux : `sudo systemctl start docker`).

---

## Étape 1 — Récupérer le projet

### Si tu travailles seul (première fois)

```bash
git clone <URL_DU_REPO>
```

*Ce que ça fait* : télécharge tout le code du projet depuis GitHub vers ton ordinateur.
*Remplace `<URL_DU_REPO>`* par l'URL réelle du dépôt (ex: `https://github.com/ton-orga/MSPR3.git`).

```bash
cd MSPR3
```

*Ce que ça fait* : se déplace dans le dossier du projet.

### Si tu travailles en équipe (récupérer les dernières modifications)

```bash
git pull origin main
```

*Ce que ça fait* : télécharge et applique les modifications que tes collègues ont poussées sur GitHub.
À faire à chaque fois avant de commencer à coder.

---

## Étape 2 — Configurer le fichier `.env`

Le fichier `.env` contient les mots de passe. Il n'est **PAS** dans git (pour la sécurité).

### Créer le `.env` depuis le modèle

**Sur Windows (PowerShell) :**
```bash
copy .env.example .env
```

**Sur macOS / Linux :**
```bash
cp .env.example .env
```

*Ce que ça fait* : duplique le fichier `.env.example` en `.env`.

### Modifier le `.env`

Ouvre le fichier `.env` avec un éditeur (Notepad, VSCode, nano...).

```env
# --- Base de données PostgreSQL ---
POSTGRES_DB=mspr2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=girllikepro12

# --- URL complète de connexion à la base ---
DATABASE_URL=postgresql://postgres:girllikepro12@localhost/mspr2

# --- Frontend ---
API_URL=http://localhost:8000

# --- Grafana ---
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

> **Important** : le mot de passe dans `POSTGRES_PASSWORD` et dans le `DATABASE_URL` doit être **exactement le même**.

---

## Étape 3 — Lancer toute la stack

**Une seule commande pour lancer les 5 services** (PostgreSQL, Backend, Frontend, Prometheus, Grafana) :

```bash
docker compose up -d --build
```

### Détail de la commande

| Morceau | Ce que ça fait |
|---------|----------------|
| `docker compose` | Ouvre le fichier `docker-compose.yml` et lit la configuration |
| `up` | Démarre tous les services décrits |
| `-d` | Mode **detached** = tourne en arrière-plan (tu récupères la main dans le terminal) |
| `--build` | Reconstruit les images Docker du backend et du frontend (nécessaire si le code a changé) |

### Ce qu'il se passe dans les coulisses

1. Docker lit `docker-compose.yml`
2. Il voit 5 services : `postgres`, `backend`, `frontend`, `prometheus`, `grafana`
3. Il crée un réseau privé `obrail` pour qu'ils se parlent
4. Il démarre **PostgreSQL en premier** (le backend en dépend)
5. Quand PostgreSQL est "healthy", il démarre le **backend**
6. Puis le **frontend**, **Prometheus** et **Grafana** en parallèle
7. PostgreSQL charge automatiquement le fichier `talend/dump/mspr2_dump_2026-04-22.sql` (les données)

### Premier lancement

**Temps** : 3 à 5 minutes (téléchargement + construction des images).
**Les fois suivantes** : 30 secondes.

---

## Étape 4 — Vérifier que tout fonctionne

### Voir l'état des containers

```bash
docker compose ps
```

*Ce que ça fait* : liste tous les containers et leur état.

**Résultat attendu :**

```
NAME               STATUS          PORTS
obrail-postgres    healthy         0.0.0.0:5433->5432/tcp
obrail-backend     running         0.0.0.0:8000->8000/tcp
obrail-frontend    running         0.0.0.0:8501->8501/tcp
obrail-prometheus  running         0.0.0.0:9090->9090/tcp
obrail-grafana     running         0.0.0.0:3010->3000/tcp
```

**Interprétation** :
- `healthy` → PostgreSQL est prêt à recevoir des requêtes
- `running` → le container tourne (mais peut encore être en train de démarrer)
- Si un container est `restarting` ou `exited` → voir la section [Dépannage](#dépannage)

### Voir les logs pour s'assurer que tout est ok

```bash
docker compose logs --tail=50
```

*Ce que ça fait* : affiche les 50 dernières lignes de logs de **tous** les services.
*Utile pour* : voir s'il y a des erreurs au démarrage.

Pour un service précis :
```bash
docker compose logs backend --tail=30
docker compose logs postgres --tail=30
```

---

## Accéder aux services dans le navigateur

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8501 | Interface principale (carte, graphiques, stats) |
| **API Documentation** | http://localhost:8000/docs | Swagger UI — tester l'API depuis le navigateur |
| **API santé** | http://localhost:8000/health | Vérification rapide : doit afficher `{"status":"ok"}` |
| **Prometheus** | http://localhost:9090 | Métriques brutes du backend |
| **Grafana** | http://localhost:3010 | Dashboards de monitoring (login: `admin` / `admin`) |

---

## Commandes du quotidien

### Arrêter la stack

```bash
docker compose down
```

*Ce que ça fait* : arrête et supprime les containers. **Les données PostgreSQL sont conservées** (le volume persiste).

### Redémarrer la stack

```bash
docker compose down && docker compose up -d --build
```

### Reset complet (supprime TOUTES les données)

```bash
docker compose down -v
```

*Ce que fait `-v`* : supprime aussi les volumes (PostgreSQL, Prometheus, Grafana).
**Attention** : les données sont perdues. La prochaine fois que tu lances `docker compose up`, la base sera rechargée depuis le dump SQL.

### Voir les logs en continu

```bash
docker compose logs -f
```

*Ce que fait `-f`* : "follow" — affiche les nouveaux messages en temps réel. Appuie sur `Ctrl+C` pour arrêter.

### Logs d'un seul service

```bash
docker compose logs -f backend
docker compose logs -f postgres
docker compose logs -f frontend
```

### Reconstruire sans redémarrer

```bash
docker compose build
```

*Utile quand* : tu as modifié le code Python d'un service et tu veux reconstruire l'image sans tout redémarrer.

### Entrer dans un container (mode exploration)

```bash
docker compose exec backend bash
```

*Ce que ça fait* : ouvre un terminal à l'intérieur du container backend. Tu peux explorer les fichiers, lancer des commandes Python...
*Pour sortir* : tape `exit`.

---

## Lancer les tests

### Tous les tests backend (91 tests)

```bash
cd backend
python -m pytest tests/ -v
cd ..
```

*Ce que ça fait* :
- `cd backend` → se déplace dans le dossier backend
- `python -m pytest` → lance le framework de tests Python
- `tests/` → cherche tous les fichiers de test dans le dossier `tests/`
- `-v` → mode verbeux (montre le nom de chaque test et son résultat)

**Alternative (sans cd) :**
```bash
docker compose exec backend pytest -v
```

*Ce que ça fait* : exécute pytest directement dans le container backend (pas besoin d'avoir Python installé sur ta machine).

### Tous les tests dashboard (31 tests)

```bash
cd dashboard
python -m pytest tests/ -v
cd ..
```

ou

```bash
docker compose exec frontend pytest -v
```

### Un fichier de test spécifique

```bash
docker compose exec backend pytest tests/test_trajets.py -v
```

### Un test spécifique par son nom

```bash
docker compose exec backend pytest tests/test_stats.py -k "test_jour_count" -v
```

*Ce que fait `-k`* : exécute uniquement les tests dont le nom contient "test_jour_count".

---

## Base de données

### Ouvrir un shell PostgreSQL (pour taper des requêtes SQL)

```bash
docker compose exec postgres psql -U postgres -d mspr2
```

*Ce que ça fait* :
- `exec` → exécute une commande dans le container qui tourne
- `postgres` → nom du service (le container PostgreSQL)
- `psql` → client PostgreSQL en ligne de commande
- `-U postgres` → utilisateur `postgres`
- `-d mspr2` → base de données `mspr2`

Une fois dans `psql`, tu tapes des commandes SQL :

```sql
-- Liste toutes les tables
\dt

-- Compter les trajets
SELECT COUNT(*) FROM trajet;

-- Voir les 5 premiers trajets
SELECT trajet_id, gare_depart, gare_arrivee FROM trajet LIMIT 5;

-- Quitter psql
\q
```

### Sauvegarder la base (créer un dump)

```bash
docker compose exec postgres pg_dump -U postgres -d mspr2 > talend/dump/backup_$(date +%Y-%m-%d).sql
```

*Ce que ça fait* :
- `pg_dump` → outil d'export PostgreSQL
- `> talend/dump/backup_...` → redirige la sortie vers un fichier sur ta machine
- `$(date +%Y-%m-%d)` → ajoute la date automatiquement (ex: `backup_2026-05-04.sql`)

### Restaurer la base depuis un dump

```bash
docker compose exec -T postgres psql -U postgres -d mspr2 < talend/dump/mspr2_dump_2026-04-22.sql
```

*Ce que fait `-T`* : désactive l'allocation d'un pseudo-terminal (nécessaire pour rediriger un fichier depuis la machine hôte).

### Vérifier que la base est bien chargée

```bash
docker compose exec postgres psql -U postgres -d mspr2 -c "SELECT COUNT(*) FROM trajet;"
```

*Ce que fait `-c`* : exécute une commande SQL et quitte immédiatement.

---

## Workflow collaboratif (GitHub)

### Avant de commencer à coder

```bash
# 1. Récupère les dernières modifications de tes collègues
git pull origin main

# 2. Crée une nouvelle branche pour ta fonctionnalité
git checkout -b feature/ma-fonctionnalite
```

*Ce que fait `git checkout -b`* : crée une nouvelle branche et bascule dessus (main reste intact).

### Avant de pousser ton code

```bash
# 1. Lance tous les tests localement
cd backend && pytest -v && cd ..
cd dashboard && pytest -v && cd ..

# 2. Si tout passe, ajoute tes modifications
git add .

# 3. Crée un commit
git commit -m "feat: description de ce que tu as fait"

# 4. Pousse ta branche sur GitHub
git push origin feature/ma-fonctionnalite
```

### Créer une Pull Request

Va sur GitHub → ta branche → clique **"Compare & pull request"** → décris tes changements → crée la PR.

**GitHub Actions** (la CI/CD du projet) va automatiquement :
1. Lancer tous les tests (backend + dashboard)
2. Vérifier que tout passe
3. Si ok, marquer la PR comme prête à être fusionnée

---

## Dépannage

### Problème : "port already allocated" (déjà utilisé)

**Message :** `Error starting userland proxy: listen tcp4 0.0.0.0:5433: bind: address already in use`

**Cause :** le port 5433 est déjà utilisé par un autre programme.

**Solution :** change le port dans `docker-compose.yml` :
```yaml
ports:
  - "5434:5432"   # au lieu de 5433:5432
```
Puis relance `docker compose up -d`.

### Problème : le backend ne démarre pas

**Vérifie :**
```bash
docker compose logs backend --tail=50
```

**Cause probable :** PostgreSQL n'est pas encore "healthy".

**Solution :** attends 30 secondes puis :
```bash
docker compose restart backend
```

### Problème : "cannot connect to database"

**Vérifie le `.env` :**
```bash
# Sur Windows PowerShell
cat .env | Select-String "POSTGRES_PASSWORD"

# Sur macOS/Linux
cat .env | grep POSTGRES_PASSWORD
```
Les deux mot de passe (POSTGRES_PASSWORD et celui dans DATABASE_URL) doivent être identiques.

**Redémarrage forcé :**
```bash
docker compose down -v
docker compose up -d --build
```

### Problème : le dashboard tourne mais les données sont vides

**Vérifie que le backend répond :**
```bash
curl http://localhost:8000/health
# Doit retourner : {"status":"ok"}

curl http://localhost:8000/stats/trajets/count
# Doit retourner : {"total_trajets": quelque_chose}
```

**Vérifie la base de données :**
```bash
docker compose exec postgres psql -U postgres -d mspr2 -c "SELECT COUNT(*) FROM trajet;"
```

Si le compte est 0, la base ne s'est pas chargée. Relance avec reset :

```bash
docker compose down -v && docker compose up -d --build
```

### Problème général — reset complet

```bash
# 1. Arrête tout et supprime les volumes
docker compose down -v

# 2. Supprime les images construites localement
docker compose build --no-cache

# 3. Relance
docker compose up -d --build
```

**Quand utiliser ça** : quand tu penses que quelque chose est corrompu (base, cache Docker, etc.). Ça repart à zéro.

---

## Récapitulatif des commandes essentielles

| Action | Commande |
|--------|----------|
| **Lancer** | `docker compose up -d --build` |
| **Arrêter** | `docker compose down` |
| **Reset complet** | `docker compose down -v` |
| **État des services** | `docker compose ps` |
| **Logs (tous)** | `docker compose logs -f` |
| **Logs (backend)** | `docker compose logs backend -f` |
| **Tester backend** | `docker compose exec backend pytest -v` |
| **Tester dashboard** | `docker compose exec frontend pytest -v` |
| **Shell PostgreSQL** | `docker compose exec postgres psql -U postgres -d mspr2` |
| **Sauvegarder BDD** | `docker compose exec postgres pg_dump -U postgres -d mspr2 > backup.sql` |
| **Restaurer BDD** | `docker compose exec -T postgres psql -U postgres -d mspr2 < backup.sql` |

---

## URLs d'accès rapide

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API (Swagger) | http://localhost:8000/docs |
| API santé | http://localhost:8000/health |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3010 (admin / admin) |

---

## Déploiement — mettre le projet en ligne gratuitement

> Tu as besoin de montrer le projet à quelqu'un sans qu'il ait à tout installer ?

Cette section explique comment déployer ObRail Europe sur internet **gratuitement**, en utilisant uniquement Docker (pas de make).

Le projet est composé de 5 services. Aucune plateforme gratuite ne peut héberger les 5 en même temps. La stratégie recommandée :

| Service | Où le déployer |
|---------|----------------|
| **Backend + Frontend** | Fly.io ou Render (gratuit) |
| **PostgreSQL** | Fly.io (inclus) ou Render (90 jours gratuit) |
| **Prometheus + Grafana** | Restent en local (monitoring dev) |

---

### Option A — Fly.io (recommandé, gratuit, pas de mise en veille)

Fly.io déploie des containers Docker. Tier gratuit : 3 VM partagées + PostgreSQL 3 Go.

#### 1. Installer Fly CLI

```bash
# Windows (PowerShell)
winget install flyctl

# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

#### 2. Se connecter

```bash
fly auth login
# Ouvre le navigateur pour créer un compte
```

#### 3. Créer la base PostgreSQL

```bash
fly postgres create --name obrail-db --region cdg
```

*`cdg` = Paris (région la plus proche de la France)*
**Note bien le mot de passe affiché** après la création.

#### 4. Déployer le backend

```bash
cd backend

fly launch --name obrail-backend --region cdg --no-deploy

fly postgres attach obrail-db --app obrail-backend

fly secrets set CORS_ORIGINS="https://obrail-frontend.fly.dev" --app obrail-backend

fly deploy --app obrail-backend
```

#### 5. Déployer le frontend

```bash
cd ../dashboard

fly launch --name obrail-frontend --region cdg --no-deploy

fly secrets set API_URL="https://obrail-backend.fly.dev" --app obrail-frontend

fly deploy --app obrail-frontend
```

#### 6. Charger les données

```bash
# Depuis ta machine, envoie le dump SQL
fly postgres connect --app obrail-db -d mspr2 < talend/dump/mspr2_dump_2026-04-22.sql
```

#### URLs après déploiement

- Dashboard : `https://obrail-frontend.fly.dev`
- API : `https://obrail-backend.fly.dev/docs`

---

### Option B — Render (plus simple, mais mise en veille après 15 min)

Facile à configurer via l'interface web.

#### 1. Créer un compte sur https://render.com

#### 2. Créer PostgreSQL

- **New** → **PostgreSQL**
- Nom : `obrail-db`
- Tier : Free
- Région : Frankfurt
- **Create Database**
- Copier l'**Internal Database URL** (format : `postgresql://...`)

#### 3. Déployer le backend

- **New** → **Web Service**
- Connecter ton dépôt GitHub
- Nom : `obrail-backend`
- Root Directory : `backend`
- Environnement : **Docker**
- Ajouter les variables :
  - `DATABASE_URL` = (l'URL copiée à l'étape 2)
  - `CORS_ORIGINS` = `https://obrail-frontend.onrender.com`

#### 4. Déployer le frontend

- **New** → **Web Service**
- Root Directory : `dashboard`
- Environnement : **Docker**
- Variable : `API_URL` = `https://obrail-backend.onrender.com`

> **⚠️ Limite** : Render Free met les services en veille après 15 min d'inactivité. Le premier appel après une pause prend ~30 secondes.

---

### Option C — Oracle Cloud Free Tier (pour la stack complète)

Oracle offre **2 VMS gratuites à vie** (1 CPU, 1 Go RAM). Assez pour tout faire tourner.

**Résumé des étapes** (détaillées dans le guide complet):

1. Créer un compte Oracle Cloud (carte demandée pour vérification, pas de prélèvement)
2. Créer une VM Ubuntu 22.04
3. Ouvrir les ports dans le pare-feu (22, 8000, 8501, 3010, 9090)
4. Se connecter en SSH : `ssh ubuntu@<IP_VM>`
5. Installer Docker : `curl -fsSL https://get.docker.com | sh`
6. Cloner le projet : `git clone <URL> && cd MSPR3`
7. Créer le `.env` : `cp .env.example .env` (éditer les mots de passe)
8. Lancer : `docker compose up -d --build`

---

### Résumé des options

| | Fly.io | Render | Oracle Cloud |
|---|---|---|---|
| **Gratuit** | Oui | Oui | Oui (à vie) |
| **Complexité** | Moyenne | Facile | Élevée |
| **PostgreSQL inclus** | Oui | Oui (90j) | Non |
| **Mise en veille** | Non | Oui (15 min) | Non |
| **Prometheus+Grafana** | Non | Non | Oui |
| **Idéal pour** | Démo publique | Présentation | Stack complète |

---
