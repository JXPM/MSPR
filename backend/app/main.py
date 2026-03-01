from fastapi import FastAPI
from app.routes import health_routes, trajet_routes

app = FastAPI(title="ObRail API")

app.include_router(health_routes.router)
app.include_router(trajet_routes.router)