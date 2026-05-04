from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import trajet_routes, health_routes, gare_routes, ligne_routes, stats_routes
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="ObRail Europe API",
    description="API REST — dessertes ferroviaires européennes",
    version="1.0.0",
)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],  # dev + preview Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(trajet_routes.router)
app.include_router(gare_routes.router)
app.include_router(ligne_routes.router)
app.include_router(stats_routes.router)