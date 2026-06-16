FROM python:3.12-slim AS base

# Non-buffered output, pas de pyc files, pas de prompt pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dépendances système minimales (psycopg2 a besoin de libpq)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

# Install des deps en couche dédiée pour le cache Docker
# NB: contexte de build = racine du repo (cf. .dockerignore), d'où les chemins backend/…
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code applicatif
COPY backend/app/ ./app/

# Modèles ML + code d'inférence : nécessaires aux routes /predict.
# Embarqués dans l'image pour fonctionner sans volume (ex. déploiement Render),
# contrairement au montage ./ml:/app/ml utilisé en local via docker-compose.
COPY ml/__init__.py ./ml/__init__.py
COPY ml/api/ ./ml/api/
COPY ml/models/ ./ml/models/
COPY ml/data/processed/ ./ml/data/processed/

# Créer un user non-root (sécurité)
RUN groupadd --system app && useradd --system --gid app app \
 && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# uvicorn en prod. Chaque worker charge les modèles ML en mémoire : sur le
# plan free Render (512 Mi), 4 workers provoquent un OOM. Défaut = 1 worker,
# surchargeable via WEB_CONCURRENCY sur des instances plus grosses.
# Forme shell volontaire pour permettre la substitution de la variable.
CMD uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${WEB_CONCURRENCY:-1} \
    --access-log \
    --proxy-headers
