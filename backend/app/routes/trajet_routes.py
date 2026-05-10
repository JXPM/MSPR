from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.schemas.trajet_schema import TrajetResponse
from app.services import trajet_service

router = APIRouter(prefix="/trajets", tags=["Trajets"])


@router.get("/", response_model=List[TrajetResponse])
def get_trajets():
    return trajet_service.get_all_trajets()


@router.get("/{trajet_id}", response_model=TrajetResponse)
def get_trajet(trajet_id: str = Path(min_length=1, max_length=64)):
    trajet = trajet_service.get_trajet_by_id(trajet_id)
    if not trajet:
        raise HTTPException(status_code=404, detail="Trajet not found")
    return trajet


@router.get("/{trajet_id:path}/itineraire")
def get_trajet_itineraire(trajet_id: str = Path(min_length=1, max_length=64)):
    """Retourne la liste ordonnée des gares desservies par le trajet.

    On utilise le converter ``:path`` pour tolérer les ``/`` dans
    ``trajet_id`` (ex : 'CFR 78/1743').
    """
    stops = trajet_service.get_itineraire_by_trajet(trajet_id)
    if not stops:
        raise HTTPException(status_code=404, detail="Itineraire not found")
    return stops
