# ObRail Europe — Frontend

Interface web de l'observatoire ObRail Europe.
Consomme l'API FastAPI du MSPR TPRE512/612 pour exposer :

- **Trajets** — exploration avec filtres avancés, pagination, cards éditoriales
- **Observatoire** — dashboard : jour/nuit (donut), opérateurs (barres), empreinte CO₂, qualité des données
- **Détail trajet** — carte Leaflet interactive, métadonnées enrichies, détails gares
- **Supervision** — monitoring live (sonde 10s), latence temps réel, timeline disponibilité, statut par endpoint

Réalisé dans le cadre de la **MSPR TPRE532 — Bloc E6.3** (Produire et maintenir une solution I.A).

---

## 🧰 Stack

- **React 18** + **TypeScript 5** + **Vite 5**
- **Tailwind CSS** (design tokens custom ObRail : forest / cream / rust / midnight)
- **TanStack Query** (cache + états API)
- **React Router 6** (routing SPA)
- **Recharts** (graphiques Dashboard + Supervision)
- **Leaflet** + **react-leaflet** (cartographie détail trajet)
- **Playwright** (tests E2E)
- **nginx:alpine** (serveur prod — user non-root, gzip, security headers)

Typographies : **Instrument Serif** (display) + **IBM Plex Sans/Mono** — volontairement
non-génériques, pour incarner l'identité éditoriale d'un observatoire institutionnel.

---

## 📁 Structure

```
obrail-frontend/
├── .github/workflows/ci.yml           # Pipeline CI/CD
├── src/
│   ├── components/
│   │   ├── layout/         Header, Footer, RootLayout
│   │   ├── ui/             Button, Input, Select, Badge
│   │   ├── trajets/        TrajetCard, TrajetsFiltersPanel, TrajetsPagination
│   │   ├── dashboard/      StatCard, JourNuitChart, OperateursChart, EmissionsChart, DataQuality
│   │   ├── detail/         TrajetMap
│   │   └── supervision/    LatencyChart, UptimeTimeline, EndpointStatusList
│   ├── hooks/
│   │   ├── useTrajets.ts           Hooks React Query pour les endpoints
│   │   ├── useEnrichedTrajets.ts   Fetch + jointure + filtrage + pagination
│   │   ├── useTrajetsUrlState.ts   Sync filtres ↔ URL (query params)
│   │   └── useLatencyMonitor.ts    Sonde périodique client-side
│   ├── lib/
│   │   ├── api.ts              axios + interception erreurs
│   │   ├── queryClient.ts      Config TanStack Query
│   │   ├── useLeafletCss.ts    Injection CSS Leaflet à la demande
│   │   └── utils.ts            cn() pour Tailwind
│   ├── pages/      Home, Trajets, TrajetDetail, Dashboard, Supervision, NotFound
│   ├── types/      api.ts (miroir des schémas Pydantic backend)
│   ├── App.tsx     Routing
│   ├── main.tsx    Entry point
│   └── index.css   Design tokens + styles globaux
├── tests/e2e/      4 specs Playwright
├── Dockerfile      Multi-stage (Node build → nginx alpine)
├── docker-compose.yml
├── nginx.conf
├── playwright.config.ts
└── COMPETENCES_MSPR.md  Mapping livrables ↔ RNCP 36581
```

---

## ⚠️ Avant de lancer — Ajouter CORS côté backend

Ton `app/main.py` n'expose pas CORS par défaut. En dev le proxy Vite contourne le
problème, mais **en prod c'est obligatoire**. À ajouter :

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import trajet_routes, health_routes, gare_routes, ligne_routes, stats_routes

app = FastAPI(
    title="ObRail Europe API",
    description="API REST — dessertes ferroviaires européennes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev
        "http://localhost:4173",   # Vite preview
        "http://localhost:8080",   # Nginx prod
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(trajet_routes.router)
app.include_router(gare_routes.router)
app.include_router(ligne_routes.router)
app.include_router(stats_routes.router)
```

---

## 🚀 Installation & développement

**Prérequis :** Node.js 20+, backend FastAPI sur `http://localhost:8000`

```bash
npm install
cp .env.example .env
npm run dev
```

→ `http://localhost:5173`

Le proxy Vite redirige `/api/*` vers `http://localhost:8000/*` automatiquement.

---

## 🧪 Tests E2E

```bash
npm run test:e2e                  # run all
npx playwright test --ui          # UI mode
npx playwright show-report        # rapport HTML
```

Les 4 specs couvrent home, trajets, dashboard, supervision.

---

## 🏗️ Build production

```bash
npm run build
npm run preview
```

---

## 🐳 Docker

```bash
docker build -t obrail-frontend .
docker run -p 8080:8080 obrail-frontend

# Ou avec compose
docker compose up --build
```

**Image :** multi-stage Node 20 → nginx 1.27 alpine, user non-root, security headers,
gzip, cache 1 an sur assets hashés, fallback SPA, HEALTHCHECK.

---

## 🔄 CI/CD

Workflow GitHub Actions (`.github/workflows/ci.yml`) :

1. **`build`** — install, `tsc --noEmit`, `vite build`, artifact
2. **`e2e`** — Playwright browsers, tests, rapport HTML
3. **`docker`** — build + push sur GHCR (sur `main` uniquement)

Déclenchement : push sur `main`/`develop`, PR vers `main`.

---

## 🎨 Design

### Palette
- **Forest** — primaire, écologie institutionnelle
- **Cream** — fond éditorial, pas blanc
- **Rust** — accent, trains de jour
- **Midnight** — trains de nuit, contraste profond

### Identité jour vs nuit
Les trajets de **nuit** basculent sur fond `midnight-900` avec accent `rust-400`,
les trajets de **jour** restent sur `cream` avec accent `rust-500`. Le contraste
est lisible au premier coup d'œil dans les cards et sur le dashboard.

---

## ♿ Accessibilité (RGAA 4.1)

- Skip link (critère 12.7)
- Focus visible conforme
- Labels explicites sur tous les inputs
- ARIA : `aria-label`, `aria-live`, `aria-current`, `aria-busy`
- Rôles : `role="img"`, `role="progressbar"`, `role="alert"`
- Structure sémantique `header` / `main` / `nav` / `footer`
- Tableau accessible doublant les graphiques (`<table class="sr-only">`)
- Contrastes AA minimum
- Autocomplete natif (`datalist`) pour champs gares

Audit complet à faire avec `axe-core` / Lighthouse.

---

## 📋 Roadmap livrée

| Chat | Sujet | Statut |
|------|-------|--------|
| 1 | Setup + layout + routing | ✅ |
| 2 | Liste Trajets + filtres (URL-sync, pagination) | ✅ |
| 3 | Dashboard + 4 graphiques Recharts | ✅ |
| 4 | Détail Trajet + carte Leaflet | ✅ |
| 5 | Supervision enrichie (latence, uptime) | ✅ |
| 6 | Tests E2E + CI/CD GitHub Actions | ✅ |

Voir `COMPETENCES_MSPR.md` pour le mapping détaillé livrables ↔ RNCP 36581.

---

## 🎓 Pour la soutenance

**Points forts à défendre :**

1. **Identité visuelle forte** — palette + typo cohérentes, pas de générique
2. **URL-state des filtres** — partage de recherche, retour navigateur
3. **Jointures client-side** — pragmatiques face à un backend sans filtres serveur
4. **Monitoring maison frontend** — démontre la compréhension MLOps
5. **Accessibilité dès la conception** — skip-link, ARIA, sémantique
6. **Docker non-root + security headers** — bonnes pratiques prod

**Questions-types à anticiper :**

- « Pourquoi pas Server Components ? » → SPA plus simple à containeriser, API REST existante
- « Pourquoi filtres côté client ? » → contrainte backend (`/trajets/` sans query params), à pousser côté serveur ultérieurement
- « Comment ça scale ? » → pagination virtuelle (react-window), filtres serveur, cache CDN
- « RGPD avec géoloc ? » → coordonnées des **gares** (entités publiques), pas des utilisateurs
