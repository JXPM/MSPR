# Guide de lancement – ObRail Europe

## Prérequis

- Python 3.14 installé
- PostgreSQL 18 installé et démarré
- Base de données `mspr2` créée et peuplée (via ETL Talend)
- Venv situé dans `MSPR/venv/`

---

## Ports utilisés

| Service         | Port  | URL                          |
|-----------------|-------|------------------------------| Backend FastAPI | 8003  | http://127.0.0.1:8003        || Swagger UI      | 8003  | http://127.0.0.1:8003/docs   || Dashboard       | 8502  | http://localhost:8502         |
| Backend FastAPI | 8001  | http://127.0.0.1:8001        |
| Swagger UI      | 8001  | http://127.0.0.1:8001/docs   |
| Dashboard       | 8501  | http://localhost:8501         |

> Le port 8000 est réservé à un autre projet sur cette machine. Le backend ObRail utilise le **port 8001**.

---

## Fichier .env

Le fichier `backend/.env` doit contenir :

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

> Pas de chevrons `< >` autour du mot de passe — c'est la valeur brute.

---

## Lancement

### Terminal 1 — Backend FastAPI

```bash
.\MSPR\venv\Scripts\activate.ps1
cd .\MSPR\backend
..\venv\Scripts\uvicorn app.main:app --port 500
```

Vérifier que l'API répond :

```bash
curl http://127.0.0.1:8001/health
# {"status":"ok"}
```

### Terminal 2 — Dashboard Streamlit

```bash
.\MSPR\venv\Scripts\activate.ps1
cd .\MSPR\dashboard
streamlit run app.py --server.port 8501
#en cas de probleme de port
taskkill /PID 20588 /F
```

Dashboard disponible sur : http://localhost:8501

---

## Installer / mettre à jour les dépendances

```bash
cd .\MSPR
venv\Scripts\pip install -r backend\requirements.txt
venv\Scripts\pip install -r dashboard\requirements.txt
```

---

## Dépendances installées (venv)

| Package         | Version  |
|-----------------|----------|
| fastapi         | 0.135.3  |
| uvicorn         | 0.44.0   |
| sqlalchemy      | 2.0.49   |
| psycopg2-binary | 2.9.11   |
| pydantic        | 2.12.5   |
| python-dotenv   | 1.2.2    |
| alembic         | 1.18.4   |
| pytest          | 9.0.2    |
| httpx           | 0.28.1   |
| streamlit       | 1.56.0   |
| pandas          | 3.0.2    |
| plotly          | 6.6.0    |
| requests        | 2.33.1   |

---

## Remarques

- Le backend et le dashboard doivent tourner **en même temps** dans deux terminaux séparés.
- Si la base de données est vide, lancer d'abord le pipeline ETL Talend (`talend/lancement/lancement.bat`).
- Logs backend : `MSPR/backend_uvicorn.log`
- Logs dashboard : `MSPR/dashboard_streamlit.log`
