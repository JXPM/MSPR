# Déploiement gratuit — ObRail Europe

Stack cible : **Neon** (Postgres) + **Render** (FastAPI) + **Streamlit Community Cloud** (dashboard).
Total : 0 € / mois. Le monitoring (Prometheus + Grafana) reste local pour la démo.

---

## 0. Pré-requis

- Compte GitHub avec le repo `JXPM/MSPR` poussé.
- Compte gratuit sur :
  - [Neon](https://neon.tech) (Postgres serverless, 3 GB free, ne s'endort pas)
  - [Render](https://render.com) (Docker web service free, s'endort après 15 min d'inactivité)
  - [Streamlit Community Cloud](https://streamlit.io/cloud) (illimité pour repos publics)
- `psql` 17 installé en local pour seeder la base (`sudo apt install postgresql-client-17`).

---

## 1. Base de données — Neon

1. Crée un projet Neon, région `eu-central-1` (Francfort).
2. Dans le dashboard Neon → **Connection Details** → copie l'URL au format :
   ```
   postgresql://<user>:<password>@<host>/<db>?sslmode=require
   ```
3. Charge le dump le plus récent dans Neon :
   ```bash
   DUMP=$(ls -t talend/dump/mspr2_dump_*.sql | head -1)
   psql "postgresql://<user>:<password>@<host>/<db>?sslmode=require" -f "$DUMP"
   ```
4. Vérifie :
   ```bash
   psql "$NEON_URL" -c "SELECT COUNT(*) FROM trajet;"
   ```

> **Pourquoi pas Talend en prod ?** Render free tier ne tolère pas un job Java planifié.
> L'ETL Talend reste en local pour rafraîchir le dump, qu'on recharge ensuite dans Neon.

---

## 2. Backend FastAPI — Render

Le repo contient déjà un `render.yaml` (Blueprint). Render le détecte automatiquement.

1. Sur Render → **New** → **Blueprint** → connecte le repo GitHub.
2. Render lit `render.yaml` et propose de créer le service `obrail-backend`.
3. Renseigne les **environment variables** (marquées `sync: false`) :
   - `DATABASE_URL` = l'URL Neon (avec `?sslmode=require`)
   - `CORS_ORIGINS` = `https://<ton-app>.streamlit.app` (à remplir après l'étape 3)
4. Clique **Apply**. Premier build ~5 min.
5. Une fois live, teste :
   ```
   https://obrail-backend.onrender.com/health
   https://obrail-backend.onrender.com/stats/trajets/count
   ```

> **Cold start** : Render free endort le service après 15 min. La 1ʳᵉ requête prend ~30 s à réveiller. Acceptable pour une démo.

---

## 3. Dashboard Streamlit — Streamlit Cloud

1. Sur [share.streamlit.io](https://share.streamlit.io) → **New app**.
2. Configure :
   - **Repository** : `JXPM/MSPR`
   - **Branch** : `main`
   - **Main file path** : `dashboard/app.py`
3. **Advanced settings** → **Secrets** (TOML) :
   ```toml
   API_URL = "https://obrail-backend.onrender.com"
   PROMETHEUS_URL = ""
   ```
4. **Deploy**. Tu obtiens une URL `https://<slug>.streamlit.app`.
5. **Retour sur Render** : édite `CORS_ORIGINS` du service `obrail-backend` pour y mettre l'URL Streamlit, puis redeploy.

---

## 4. Vérifications post-déploiement

```bash
# Backend
curl https://obrail-backend.onrender.com/health
curl https://obrail-backend.onrender.com/stats/trajets/count

# Dashboard : ouvre l'URL streamlit.app dans le navigateur,
# vérifie que la page Trajets affiche des données.
```

---

## 5. Mise à jour des données

Quand l'ETL Talend produit un nouveau dump localement :

```bash
# Régénérer le dump (lancement local)
make etl   # ou : ./talend/lancement

# Pousser vers Neon
DUMP=$(ls -t talend/dump/mspr2_dump_*.sql | head -1)
psql "$NEON_URL" -f "$DUMP"
```

Le backend Render n'a pas besoin d'être redéployé : il lit Neon en direct.

---

## 6. Ce qui n'est PAS déployé (et pourquoi)

| Service | Raison |
|---|---|
| Prometheus | Pas d'utilité publique, consomme un free tier. Reste en `docker-compose` local. |
| Grafana | Idem. Pour la soutenance, lancer `docker compose up grafana prometheus` localement. |
| Talend ETL | Job Java planifié, ne rentre pas dans le free tier Render. Exécution locale → push du dump vers Neon. |

L'endpoint `/metrics` du backend reste **exposé** sur Render pour démontrer l'instrumentation, même si aucun Prometheus distant ne le scrape.

---

## 7. Coûts

| Service | Plan | Limite | Coût |
|---|---|---|---|
| Neon | Free | 3 GB stockage, 100h/mois compute actif | 0 € |
| Render | Free | 750h/mois, sleep après 15 min | 0 € |
| Streamlit Cloud | Community | Illimité (repo public) | 0 € |
| **Total** | | | **0 €** |
