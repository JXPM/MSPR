import asyncio
import os
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes import gare_routes, health_routes, ligne_routes, stats_routes, trajet_routes
from prometheus_fastapi_instrumentator import Instrumentator


def _parse_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:4173,http://localhost:8501"
CORS_ORIGINS = _parse_origins(os.getenv("CORS_ORIGINS") or DEFAULT_ORIGINS)

app = FastAPI(
    title="ObRail Europe API",
    description="API REST — dessertes ferroviaires européennes",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._lock = asyncio.Lock()
        self._requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/trajets") or path.startswith("/stats"):
            ip = request.client.host if request.client else "unknown"
            now = time.time()
            async with self._lock:
                self._requests[ip] = [t for t in self._requests[ip] if now - t < self.window]
                if len(self._requests[ip]) >= self.max_requests:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded. Try again in 60 seconds."},
                    )
                self._requests[ip].append(now)
        return await call_next(request)


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(trajet_routes.router)
app.include_router(gare_routes.router)
app.include_router(ligne_routes.router)
app.include_router(stats_routes.router)
