from fastapi import FastAPI
from app.routes import trajet_routes, health_routes, gare_routes, ligne_routes, stats_routes

app = FastAPI()

app.include_router(health_routes.router)
app.include_router(trajet_routes.router)
app.include_router(gare_routes.router)
app.include_router(ligne_routes.router)
app.include_router(stats_routes.router)