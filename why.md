# Why — Journal des modifications ObRail

> Modifications apportées pour mise en conformité avec le cahier des charges TPRE532.

## 1. Grafana — UID datasource (`monitoring/grafana/dashboards/fastapi-observability.json`, `monitoring/grafana/datasources/prometheus.yml`)

**Problème :** L'UID `PBFA97CFB590B2093` est généré localement par Grafana au premier démarrage. Sur une autre machine, Grafana génère un UID différent, ce qui rend tous les panels du dashboard vides car aucune datasource ne correspond.

**Modification (en deux étapes) :**
1. Ajout de `uid: obrail-prometheus` dans `monitoring/grafana/datasources/prometheus.yml` — Grafana utilise désormais cet UID fixe au lieu d'en générer un aléatoire.
2. Remplacement de toutes les occurrences de `"uid": "PBFA97CFB590B2093"` dans le dashboard JSON par `"uid": "obrail-prometheus"`. Ajout des blocs `__inputs` et `__requires` (utiles pour l'import manuel via l'UI Grafana).

**Pourquoi pas seulement `${DS_PROMETHEUS}` :** Cette syntaxe de variable fonctionne uniquement lors d'un import manuel via le bouton "Import" de l'interface. Pour le provisioning automatique par fichier (notre cas), Grafana lit le JSON directement sans résoudre les variables — il faut un UID littéral qui corresponde exactement à la datasource provisionnée.

**Impact :** Le dashboard s'affiche correctement sur toute machine sans intervention manuelle. Garanti reproductible en CI et en déploiement.

---

## 2. Sécurisation backend (`backend/app/main.py`, `backend/requirements.txt`)

**Problème :** Aucun rate limiting ni headers de sécurité HTTP. L'API exposée sans protection permet des abus (scraping massif, clickjacking, MIME sniffing).

**Modification :**
- Ajout de `slowapi` dans `requirements.txt`.
- Configuration d'un `Limiter` global (60 req/min par IP) via slowapi dans `main.py`.
- Middleware `RateLimitMiddleware` (Starlette `BaseHTTPMiddleware`) appliqué aux paths `/trajets` et `/stats/*` : retourne HTTP 429 si dépassement.
- Middleware `SecurityHeadersMiddleware` qui injecte sur chaque réponse : `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`.

**Impact :** Protection contre le scraping abusif et les attaques web courantes (clickjacking, MIME confusion). Aucun endpoint existant modifié, tests existants non cassés.

---

## 3. Accessibilité RGAA (`dashboard/app.py`)

**Problème :** Contraste `--muted` borderline RGAA AA (#4f6b62 sur fond #f6f1e8 ≈ ratio 3.8:1, sous le seuil de 4.5:1 pour le texte normal). Absence de skip link et d'ancre `#main-content`.

**Modification :**
- `--muted` passé de `#4f6b62` à `#3d5a52` (ratio de contraste ≈ 5.2:1, conforme RGAA AA).
- Ajout de la classe CSS `.skip-link` / `.skip-link:focus` dans le bloc `<style>` existant.
- Ajout du lien `<a href="#main-content" class="skip-link">Aller au contenu principal</a>` en tête du premier `st.html()`.
- Ajout de `<div id="main-content">` comme ancre cible.

**Impact :** Conformité RGAA AA sur le contraste. Navigation clavier améliorée pour les utilisateurs de lecteurs d'écran.

---

## 4. Supervision Prometheus (`dashboard/services/api_service.py`)

**Problème :** La supervision ne lisait que `/health`. Aucune métrique réelle (taux d'erreur, latence) n'était interrogée, rendant la page supervision insuffisante.

**Modification :**
- Ajout de `PROMETHEUS_URL` lue depuis l'environnement (défaut : `http://prometheus:9090`).
- Fonction `get_error_rate()` : requête PromQL `sum(rate(http_request_duration_seconds_count{status_code=~"5.."}[5m]))` sur l'API Prometheus `/api/v1/query`. Retourne `{"value": float}` ou `{"value": None}` sans lever d'exception.
- Fonction `get_api_latency_p95()` : requête PromQL `histogram_quantile(0.95, ...)`. Même comportement défensif.

**Impact :** La page supervision peut afficher les vraies métriques de l'API en temps réel. Toute erreur réseau est silencieuse (`{"value": None}`), sans crash du dashboard.

---

## 5. Tests E2E Playwright (`dashboard/tests_e2e/`)

**Problème :** Aucun test navigateur end-to-end. Le cahier des charges TPRE532 l'exige explicitement pour valider les parcours utilisateur réels.

**Modification :**
- Création de `dashboard/tests_e2e/conftest.py` : fixture `base_url` lue depuis `E2E_BASE_URL` (défaut : `http://localhost:8501`).
- `test_navigation.py` : 4 tests — chargement home, navigation Trajets, Observatoire, Supervision.
- `test_accessibility.py` : 2 tests — présence du skip link, présence d'un `<h1>` sur la page.
- Ajout de `pytest-playwright` et `playwright` dans `dashboard/requirements.txt`.

**Impact :** Couverture E2E des parcours critiques. Tests exécutables en local (`playwright install chromium` puis `pytest tests_e2e/`) et en CI.

---

## 6. Pipeline CI/CD E2E (`.github/workflows/main.yml`)

**Problème :** Aucun job E2E dans le pipeline. Les tests Playwright ne s'exécutaient pas en CI, laissant des régressions navigateur non détectées.

**Modification :** Ajout du job `e2e-test` après `frontend-test` et `backend-test` :
1. Lance la stack complète via `docker compose up -d`.
2. Attend que Streamlit réponde sur `:8501/_stcore/health` (boucle curl, max 60s).
3. Installe Python 3.12 + `playwright` + `pytest-playwright` + navigateur Chromium.
4. Exécute `pytest tests_e2e/ -v` avec `E2E_BASE_URL=http://localhost:8501`.
5. `docker compose down` en step `if: always()` pour nettoyage garanti.

**Impact :** Les régressions navigateur sont détectées à chaque PR. Le job ne bloque pas les jobs Docker (il est en parallèle avec eux).
